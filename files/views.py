from files.models import File,Directory,Project
import arxml.models as ArxmlModels
from django.http import HttpResponse, Http404, JsonResponse
from django.template import loader
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.utils.datastructures import MultiValueDictKeyError
from .serializers import ProjectSerializer

def APIResponse(status, message = {}):
    return JsonResponse(message,status=status)

def access_error_wrapper(func):
    def func_wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Http404:
            return APIResponse(404)
        except ObjectDoesNotExist:
            return APIResponse(404)
        except PermissionDenied:
            return APIResponse(550)
        except MultiValueDictKeyError:
            return APIResponse(404, { 'error' : 'Missing Parameter' } )
        except Exception as e:
            return APIResponse(500, { 'error' : str(type(e)) } )
    return func_wrapper

def OwnsFile(file, user):
    if user and user.is_authenticated:
        if file is None or file.directory.GetProject() is None:
            raise Http404
        else:
            owner = file.directory.GetProject().user
            if user.is_staff or owner.id == user.id:
                return True

    raise False

@api_view(['GET'])
@access_error_wrapper
def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    if OwnsFile(file, request.user) is True:
        return HttpResponse(file.Read())
    return APIResponse(550)

def GetSoftwareComponentIfOwns(user, id):
    file = ArxmlModels.SoftwareComponent.objects.get(pk=id)

    if file is None:
        raise Http404

    if not OwnsFile(file, user):
        raise PermissionDenied

    return file

@api_view(['POST'])
@access_error_wrapper
def generate_project(request, project_name):
    req_user = request.user
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
@access_error_wrapper
def add_software_component(request):
    return JsonResponse(request.POST)

@api_view(['POST'])
@access_error_wrapper
def add_interface(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    interface = ArxmlModels.Interface(name=request.POST['name'], swc=file.softwarecomponent)
    interface.save()
    file.swc.Rewrite()
    return HttpResponse(interface.id)

@api_view(['POST'])
@access_error_wrapper
def add_port(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    
    type = "R-PORT-PROTOTYPE"
    if request.POST['type'] == "P":
        type = "P-PORT-PROTOTYPE"

    port = ArxmlModels.Port(name=request.POST['name'], swc=file.softwarecomponent, type=type)
    port.save()
    file.swc.Rewrite()
    return HttpResponse(port.id)

@api_view(['POST'])
@access_error_wrapper
def set_port_interface(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if interface is None or interface.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Interface" })

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Port" })

    port.interface = interface
    port.save()
    file.swc.Rewrite()
    return HttpResponse("True")

@api_view(['POST'])
@access_error_wrapper
def add_dataType(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    if request.POST['type'] not in { "Boolean", "Float", "SInt8", "UInt8", "SInt16", "UInt16", "SInt32", "UInt32" }:
        return APIResponse(404, { 'error' : "Unsupported Type" })

    data_type = ArxmlModels.DataType(type=request.POST['type'], swc=file.softwarecomponent)
    data_type.save()
    file.swc.Rewrite()
    return HttpResponse("True")

@api_view(['POST'])
@access_error_wrapper
def add_dataElement(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if interface is None or interface.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Interface" })
    
    data_type = ArxmlModels.DataType.objects.get(name=request.POST['type'])
    if data_type is None or data_type.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Type" })

    element = ArxmlModels.DataElement(name=request.POST['name'], interface=interface, type=data_type)
    element.save()
    file.swc.Rewrite()
    return HttpResponse(element.id)

@api_view(['POST'])
@access_error_wrapper
def add_runnable(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    runnable = ArxmlModels.Runnable(name=request.POST['name'], concurrent=bool(request.POST['concurrent']), swc=file.softwarecomponent)
    runnable.save()
    file.swc.Rewrite()
    return HttpResponse(runnable.id)

@api_view(['POST'])
@access_error_wrapper
def add_timingEvent(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    event = ArxmlModels.TimingEvent(name=request.POST['name'], runnable=runnable, period=float(request.POST['period']), swc=file.softwarecomponent)
    event.save()
    file.swc.Rewrite()
    return HttpResponse(event.id)

@api_view(['POST'])
@access_error_wrapper
def add_dataAccess(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    element = ArxmlModels.DataElement.objects.get(pk=request.POST['element_id'])
    if element is None or element.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid DataElement" })

    type = "DATA-READ-ACCESSS"
    if request.POST['type'] == "WRITE":
        type = "DATA-WRITE-ACCESSS"

    access = ArxmlModels.DataAccess(name=request.POST['name'], runnable=runnable, data_element=element, type=type)
    access.save()
    file.swc.Rewrite()
    return HttpResponse(access.id)

@api_view(['POST'])
@access_error_wrapper
def delete_softwareComponent(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    file.delete()
    return HttpResponse("True")

@api_view(['POST'])
@access_error_wrapper
def remove_port(request):
    file = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != file.softwarecomponent:
        return APIResponse(404, { 'error' : "Invalid Port" })

    port.delete()
    file.Rewrite()
    return HttpResponse("True")

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

@api_view(['GET'])
@access_error_wrapper
def get_user_projects(request, user_id):
    if request.user.id == user_id or request.user.is_staff:
        Projects = Project.objects.filter(user=user_id)
        serializer = ProjectSerializer(Projects, many=True, context={'request': request})
        return Response(serializer.data)
    else:
        return APIResponse(550)

@api_view(['POST'])
@access_error_wrapper
def delete_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.user.is_staff or project.user == request.user:
        project.delete()
        return HttpResponse("Done")
    return APIResponse(550)