from django.shortcuts import render
from files.models import File,Directory,Project
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .serializers import ProjectSerializer, UUIDSerializer
import time
from arxml.wrapper import Arxml
from django.views.decorators.csrf import csrf_exempt

def OwnsFile(file, user):
    if user and user.is_authenticated:
        if file is None or file.directory.GetProject() is None:
            raise Http404("File doesn't exist")
    else:
        owner = file.directory.GetProject().user
        if user.is_staff or owner.id == user.id:
            return True
        else:
            raise PermissionDenied

def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    if OwnsFile(file, request.user) is True:
        return HttpResponse(file.Read())
    return False

@api_view(['GET', 'POST', ])
def generate_project(APIView, project_name, user_id):
    req_user = User.objects.get(id=user_id)
    project = Project(name=project_name , user=req_user)
    project.save()
    directory_name = project_name + str("-") + str(project.id)
    main_directory = Directory(name=directory_name, project=project)
    main_directory.save()
    arxml_file = File(name=project_name, file_type = "arxml", directory= main_directory )
    arxml_file.save()
    sub_directory = Directory(name=project_name, parent=main_directory)
    sub_directory.save()
    c_file = File(name="components", file_type="c", directory=sub_directory)
    c_file.save()
    h_file = File(name="components", file_type="h", directory=sub_directory)
    h_file.save()
    factory = APIRequestFactory()
    request = factory.get('/')
    serializer_context = {
        'request': Request(request),
    }
    ser = ProjectSerializer(instance=project, context=serializer_context)
    return Response(ser.data)

@csrf_exempt
def add_software_component(request):
    if request.method == 'POST':
        file = File.objects.get(id=request.POST['file_id'])
        if True:
            arxml = Arxml(file)
            uuid = arxml.CreateSoftwareComponent(request.POST['name'], request.POST['x'], request.POST['y'])
            arxml.Save()
            return HttpResponse(uuid)
        return False
    else:
        raise Http404("Method not supported.")

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))