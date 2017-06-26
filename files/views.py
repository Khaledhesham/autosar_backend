from files.models import File,Directory,Project
import arxml.models as ArxmlModels
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
    if user and user.is_authenticated:
        if file is None or file.directory.GetProject() is None:
            raise Http404("Not Found")
        else:
            owner = file.directory.GetProject().user
            if user.is_staff or owner.id == user.id:
                return True

    raise False

@api_view(['GET'])
def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    if OwnsFile(file, request.user) is True:
        return HttpResponse(file.Read())
    return HttpResponse("Permission Denied")

def GetSoftwareComponentIfOwns(user, id):
    file = ArxmlModels.SoftwareComponent.objects.get(pk=id)

    if file is None:
        raise Http404

    if not OwnsFile(file, user):
        raise PermissionDenied

    return file

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
    composition = ArxmlModels.Composition(file=arxml_file, project=project)
    composition.save()
    composition.Rewrite()
    sub_directory = Directory(name=project_name, parent=main_directory)
    sub_directory.save()
    factory = APIRequestFactory()
    request = factory.get('/')
    ser = ProjectSerializer(instance=project, context={ 'request': Request(request) })
    return Response(ser.data)

@api_view(['POST'])
def add_software_component(request):
    project = Project.objects.get(id=request.POST['project_id'])
    if project is not None and project.user == request.user:
        file = File(directory=project.directory, file_type="arxml", name=request.POST['name'])
        file.save()
        swc = ArxmlModels.SoftwareComponent(name=request.POST['name'], composition=project.composition, file=file, x=request.POST['x'], y=request.POST['y'])
        swc.save()
        swc.Rewrite()
        project.composition.Rewrite()
        return HttpResponse(swc.id)
    return HttpResponse("Permission Denied")

@api_view(['POST'])
def add_interface(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
        interface = ArxmlModels.Interface(name=request.POST['name'], swc=file.softwarecomponent)
        interface.save()
        file.swc.Rewrite()
        return HttpResponse(interface.id)
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def add_port(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
        
        type = "R-PORT-PROTOTYPE"
        if request.POST['type'] == "P":
            type = "P-PORT-PROTOTYPE"

        port = ArxmlModels.Port(name=request.POST['name'], swc=file.softwarecomponent, type=type)
        port.save()
        file.swc.Rewrite()
        return HttpResponse(port.id)
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def set_port_interface(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

        interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
        if interface is None or interface.swc != file.softwarecomponent:
            return HttpResponse("Invalid Interface")

        port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
        if port is None or port.swc != file.softwarecomponent:
            return HttpResponse("Invalid Port")

        port.interface = interface
        port.save()
        file.swc.Rewrite()
        return HttpResponse("True")
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def add_dataType(request):
    try:
        swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

        if request.POST['type'] not in { "Boolean", "Float", "SInt8", "UInt8", "SInt16", "UInt16", "SInt32", "UInt32" }:
            return HttpResponse("Unsupported Type")

        data_type = ArxmlModels.DataType(type=request.POST['type'], swc=file.softwarecomponent)
        data_type.save()
        file.swc.Rewrite()
        return HttpResponse("True")
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def add_dataElement(request):
    try:
        GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

        interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
        if interface is None or interface.swc != file.softwarecomponent:
            return HttpResponse("Invalid Interface")
        
        data_type = ArxmlModels.DataType.objects.get(name=request.POST['type'])
        if data_type is None or data_type.swc != file.softwarecomponent:
            return HttpResponse("Invalid Type")

        element = ArxmlModels.DataElement(name=request.POST['name'], interface=interface, type=data_type)
        element.save()
        file.swc.Rewrite()
        return HttpResponse(element.id)
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def add_runnable(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
        runnable = ArxmlModels.Runnable(name=request.POST['name'], concurrent=bool(request.POST['concurrent']), swc=file.softwarecomponent)
        runnable.save()
        file.swc.Rewrite()
        return HttpResponse(runnable.id)
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def add_timingEvent(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

        runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
        if runnable is None or runnable.swc != file.softwarecomponent:
            return HttpResponse("Invalid Runnable")

        event = ArxmlModels.TimingEvent(name=request.POST['name'], runnable=runnable, period=float(request.POST['period']), swc=file.softwarecomponent)
        event.save()
        file.swc.Rewrite()
        return HttpResponse(event.id)
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def add_dataAccess(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

        runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
        if runnable is None or runnable.swc != file.softwarecomponent:
            return HttpResponse("Invalid Runnable")

        element = ArxmlModels.DataElement.objects.get(pk=request.POST['element_id'])
        if element is None or element.swc != file.softwarecomponent:
            return HttpResponse("Invalid Data Element")

        type = "DATA-READ-ACCESSS"
        if request.POST['type'] == "WRITE":
            type = "DATA-WRITE-ACCESSS"

        access = ArxmlModels.DataAccess(name=request.POST['name'], runnable=runnable, data_element=element, type=type)
        access.save()
        file.swc.Rewrite()
        return HttpResponse(access.id)
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def delete_softwareComponent(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
        file.delete()
        return HttpResponse("True")
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

@api_view(['POST'])
def remove_port(request):
    try:
        file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

        port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
        if port is None or port.swc != file.softwarecomponent:
            return HttpResponse("Invalid Port")

        port.delete()
        file.Rewrite()
        return HttpResponse("True")
    except Http404:
        return HttpResponse("Not Found")
    except PermissionDenied:
        return HttpResponse("Permission Denied")
    except:
        return HttpResponse("Error")

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
        return HttpResponse("Permission Denied")

@api_view(['POST'])
def delete_project(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        if request.user.is_staff or project.user == request.user:
            project.delete()
            return  HttpResponse("Done")
        return HttpResponse("Permission Denied")
    except Project.DoesNotExist:
        return HttpResponse("Not Found")
