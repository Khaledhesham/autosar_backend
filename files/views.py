from files.models import File,Directory,Project,ArxmlFile
from arxml.wrapper import Arxml
from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .serializers import ProjectSerializer

def OwnsFile(file, user):
    if user and (user.is_authenticated or user.is_staff):
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
    factory = APIRequestFactory()
    request = factory.get('/')
    ser = ProjectSerializer(instance=project, context={ 'request': Request(request) })
    return Response(ser.data)

@api_view(['POST'])
def add_software_component(request):
    project = Project.objects.get(id=request.POST['project_id'])
    if project.user == request.user:
        sub_directory = Directory(name=project.name, parent=project.directory)
        sub_directory.save()
        File(name="components", file_type="c", directory=sub_directory).save()
        File(name="components", file_type="h", directory=sub_directory).save()
        file = File(directory=project.directory, file_type="arxml", name=request.POST['name'])
        file.save()
        arxml = ArxmlFile(file=file,swc_uid='')
        return HttpResponse(str(arxml.CreateSoftwareComponent(request.POST['name'], request.POST['x'], request.POST['y'])))
    raise PermissionDenied

@api_view(['POST'])
def add_interface(request):
    file = ArxmlFile.objects.get(swc_uid=request.POST['swc_uid'])
    if file is None and OwnsFile(file, request.user):
        raise Http404("SWC not found.")
    uid = file.AddInterface(request.POST['name'])
    return HttpResponse(uid)

@api_view(['POST'])
def add_port(request):
    file = ArxmlFile.objects.get(swc_uid=request.POST['swc_uid'])
    if file is None:
        raise Http404("Port not found.")
    uid = file.AddPort(request.POST['type'], request.POST['name'], request.POST['interface'])
    return HttpResponse(uid)

@api_view(['POST'])
def add_dataType(request):
    file = ArxmlFile.objects.get(swc_uid=request.POST['swc_uid'])
    if file is None:
        raise Http404("SWC not found.")
    return HttpResponse(file.AddDataType(request.POST['type']))

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))

@api_view(['GET'])
def get_user_projects(request, user_id):
    if request.user.id == user_id or request.user.is_staff:
        Projects = Project.objects.filter(user=user_id)
        serializer = ProjectSerializer(Projects, many=True, context={'request': request})
        return Response(serializer.data)
    else:
        raise PermissionDenied

@api_view(['POST'])
def delete_project(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        if request.user.is_staff or project.user == request.user:
            project.delete()
            return  HttpResponse("Done")
        raise PermissionDenied
    except Project.DoesNotExist:
        
        raise Http404