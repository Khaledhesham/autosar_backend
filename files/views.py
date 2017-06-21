from django.shortcuts import render
from files.models import File,Directory,Project,ArxmlFile
from arxml.wrapper import Arxml
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .serializers import ProjectSerializer
import time
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
    arxml_file = File(name="composition", file_type="arxml", directory=main_directory)
    arxml_file.save()
    wrapper = Arxml("", main_directory.GetPath())
    wrapper.CreateComposition(project_name)
    arxml_file.Write(str(wrapper))
    sub_directory = Directory(name=project_name, parent=main_directory)
    sub_directory.save()
    c_file = File(name="components", file_type="c", directory=sub_directory)
    c_file.save()
    factory = APIRequestFactory()
    request = factory.get('/')
    ser = ProjectSerializer(instance=project, context={ 'request': Request(request) })
    return Response(ser.data)

@csrf_exempt
def add_software_component(request):
    if request.method == 'POST':
        project = Project.objects.get(id=request.POST['project_id'])
        if True:
            sub_directory = Directory(name=project.name, parent=project.directory)
            sub_directory.save()
            File(name="components", file_type="c", directory=sub_directory).save()
            File(name="components", file_type="h", directory=sub_directory).save()
            file = File(directory=project.directory, file_type="arxml", name=request.POST['name'])
            file.save()
            arxml = ArxmlFile(file=file,swc_uid='')
            return HttpResponse(arxml.CreateSoftwareComponent(request.POST['name'], request.POST['x'], request.POST['y']))
        raise PermissionDenied
    else:
        raise Http404("Method not supported.")

@csrf_exempt
def add_interface(request):
    if request.method == 'POST':
        file = ArxmlFile.objects.get(swc_uid=request.POST['swc_uid'])
        if file is None:
            raise Http404("SWC not found.")
        uid = file.AddInterface(request.POST['name'])
        return HttpResponse(uid)
    else:
        raise Http404("Method not supported.")

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))