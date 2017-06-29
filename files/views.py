from files.models import File,Directory,Project
import arxml.models as ArxmlModels
from django.http import HttpResponse, Http404, JsonResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.utils.datastructures import MultiValueDictKeyError
from .serializers import ProjectSerializer
import shutil
import os


def APIResponse(status, message={}):
    return JsonResponse(message, status=status)


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
    if file is None or file.directory.GetProject() is None:
        raise Http404
    else:
        owner = file.directory.GetProject().user
        if user.is_staff or owner.id == user.id:
            return True
    return False


@api_view(['GET'])
@access_error_wrapper
def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    if OwnsFile(file, request.user) is True:
        return HttpResponse(file.Read())
    return APIResponse(550)


def GetSoftwareComponentIfOwns(user, id):
    component = ArxmlModels.SoftwareComponent.objects.get(pk=id)
    file = component.file

    if file is None:
        raise Http404

    if not OwnsFile(file, user):
        raise PermissionDenied

    return component


def GetCompositionIfOwns(user, id):
    composition = ArxmlModels.Composition.objects.get(project_id=id)
    file = composition.file

    if file is None:
        raise Http404

    if not OwnsFile(file, user):
        raise PermissionDenied

    return composition


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


### software component


@api_view(['POST'])
@access_error_wrapper
def add_software_component(request):
    project = Project.objects.get(id=request.POST['project_id'])
    file = File
    try:
        if project is not None and project.user == request.user:
            file = File(directory=project.directory, file_type="arxml", name=request.POST['name'])
            file.save()
            swc = ArxmlModels.SoftwareComponent(name=request.POST['name'], composition=project.composition, file=file, x=request.POST['x'], y=request.POST['y'])
            swc.save()
            swc.Rewrite()
            project.composition.Rewrite()
            return HttpResponse(swc.id)
        return APIResponse(550)
    except Exception as e:
        file.delete()
        raise e


@api_view(['POST'])
@access_error_wrapper
def delete_softwareComponent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    composition = swc.composition
    swc.file.delete()
    composition.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def rename_softwareComponent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    composition = swc.composition
    swc.name = request.POST['name']
    swc.save()
    swc.Rewrite()
    composition.Rewrite()
    return HttpResponse("True")


### port


@api_view(['POST'])
def add_port(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    type = "R-PORT-PROTOTYPE"
    if request.POST['type'] == "P":
        type = "P-PORT-PROTOTYPE"

    port = ArxmlModels.Port(name=request.POST['name'], x=request.POST['x'], y=request.POST['y'], swc=swc, type=type)
    port.save()
    swc.Rewrite()
    return HttpResponse(port.id)


@api_view(['POST'])
@access_error_wrapper
def remove_port(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Port" })

    port.delete()
    swc.Rewrite()
    swc.composition.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def rename_port(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Port" })

    port.name = request.POST['name']
    port.save()
    swc.Rewrite()
    swc.composition.Rewrite()
    return HttpResponse("True")


### interface


@api_view(['POST'])
@access_error_wrapper
def add_interface(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    interface = ArxmlModels.Interface(name=request.POST['name'], swc=swc)
    interface.save()
    swc.Rewrite()
    return HttpResponse(interface.id)


@api_view(['POST'])
@access_error_wrapper
def set_port_interface(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if interface is None or interface.swc != swc:
        return APIResponse(404, {'error': "Invalid Interface" })

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != swc:
        return APIResponse(404, {'error': "Invalid Port"})

    port.interface = interface
    port.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def add_port_dataElement(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    data_element = ArxmlModels.DataElement.objects.get(pk=request.POST['data_element_id'])
    if data_element is None or data_element.swc != swc:
        return APIResponse(404, {'error': "Invalid Data Element" })

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != swc:
        return APIResponse(404, {'error': "Invalid Port"})

    interface = port.interface

    if data_element.interface != interface:
        return APIResponse(404, {'error': "Data Element Doesn't belong to the Port's Interface"})

    ref = ArxmlModels.DataElementRef(data_element=data_element, port=port)
    ref.save()
    swc.Rewrite()
    return HttpResponse("True")

@api_view(['POST'])
@access_error_wrapper
def remove_interface(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    interface.delete()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def rename_interface(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    interface.name = request.POST['name']
    interface.save()
    swc.Rewrite()
    return HttpResponse("True")


### datatype


@api_view(['POST'])
@access_error_wrapper
def add_datatype(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    if request.POST['type'] not in { "Boolean", "Float", "SInt8", "UInt8", "SInt16", "UInt16", "SInt32", "UInt32" }:
        return APIResponse(404, { 'error' : "Unsupported Type" })

    data_type = ArxmlModels.DataType(type=request.POST['type'], swc=swc)
    data_type.save()
    swc.Rewrite()
    return HttpResponse(data_type.id)


@api_view(['POST'])
@access_error_wrapper
def remove_datatype(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    if request.POST['type'] not in { "Boolean", "Float", "SInt8", "UInt8", "SInt16", "UInt16", "SInt32", "UInt32" }:
        return APIResponse(404, { 'error' : "Unsupported Type" })

    data_type = ArxmlModels.DataType.objects.get(pk=request.POST['datatype_id'])
    data_type.delete()
    swc.Rewrite()
    return HttpResponse("True")


### data element


@api_view(['POST'])
@access_error_wrapper
def add_dataElement(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if interface is None or interface.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Interface" })
    
    data_type = ArxmlModels.DataType.objects.get(name=request.POST['type'])
    if data_type is None or data_type.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Type" })

    element = ArxmlModels.DataElement(name=request.POST['name'], interface=interface, type=data_type)
    element.save()
    swc.Rewrite()
    return HttpResponse(element.id)


@api_view(['POST'])
@access_error_wrapper
def rename_dataElement(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    element = ArxmlModels.DataElement.objects.get(pk=request.POST['dataElement_id'])
    element.name = request.POST['name']
    element.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_dataElement(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    element = ArxmlModels.DataElement.objects.get(pk=request.POST['dataElement_id'])
    element.delete()
    swc.Rewrite()
    return HttpResponse("True")


### runnable


@api_view(['POST'])
@access_error_wrapper
def add_runnable(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    runnable = ArxmlModels.Runnable(name=request.POST['name'], concurrent=bool(request.POST['concurrent']), swc=swc)
    runnable.save()
    swc.Rewrite()
    return HttpResponse(runnable.id)


@api_view(['POST'])
@access_error_wrapper
def rename_runnable(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    runnable.name = request.POST['name']
    runnable.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_runnable(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    runnable.delete()
    swc.Rewrite()
    return HttpResponse("True")


### timing events


@api_view(['POST'])
@access_error_wrapper
def add_timingEvent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    event = ArxmlModels.TimingEvent(name=request.POST['name'], runnable=runnable, period=float(request.POST['period']), swc=swc)
    event.save()
    swc.Rewrite()
    return HttpResponse(event.id)


@api_view(['POST'])
@access_error_wrapper
def rename_timingEvent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.TimingEvent.objects.get(pk=request.POST['timingEvent_id'])
    event.name = request.POST['name']
    event.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_timingEvent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.TimingEvent.objects.get(pk=request.POST['timingEvent_id'])
    event.delete()
    swc.Rewrite()
    return HttpResponse("True")


### data access


@api_view(['POST'])
@access_error_wrapper
def add_dataAccess(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    element = ArxmlModels.DataElementRef.objects.get(pk=request.POST['element_ref_id'])
    if element is None or element.port.swc != swc:
        return APIResponse(404, { 'error' : "Invalid DataElement Reference" })

    type = "DATA-READ-ACCESSS"
    if request.POST['type'] == "WRITE":
        type = "DATA-WRITE-ACCESSS"

    access = ArxmlModels.DataAccess(name=request.POST['name'], runnable=runnable, data_element_ref=element, type=type)
    access.save()
    swc.Rewrite()
    return HttpResponse(access.id)


@api_view(['POST'])
@access_error_wrapper
def rename_dataAccess(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    access = ArxmlModels.DataAccess.objects.get(pk=request.POST['dataAccess_id'])
    access.name = request.POST['name']
    access.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_dataAccess(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    access = ArxmlModels.DataAccess.objects.get(pk=request.POST['dataAccess_id'])
    access.delete()
    swc.Rewrite()
    return HttpResponse("True")


### connector


@api_view(['POST'])
@access_error_wrapper
def add_connector(request):
    composition = GetCompositionIfOwns(request.user, request.POST['project_id'])
    p_port = ArxmlModels.Port.objects.get(pk=request.POST['p_port_id'])
    r_port = ArxmlModels.Port.objects.get(pk=request.POST['r_port_id'])
    conn = ArxmlModels.Connector(composition=composition,p_port=p_port,r_port=r_port)
    conn.save()
    composition.Rewrite()
    return HttpResponse(conn.id)


@api_view(['POST'])
@access_error_wrapper
def remove_connector(request):
    composition = GetCompositionIfOwns(request.user, request.POST['project_id'])
    conn = ArxmlModels.Connector.objects.get(pk=request.POST['connection_id'])
    conn.delete()
    composition.Rewrite()
    return HttpResponse("True")


### project


@api_view(['GET'])
@access_error_wrapper
def get_user_projects(request):
    Projects = Project.objects.filter(user=request.user)
    serializer = ProjectSerializer(Projects, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@access_error_wrapper
def delete_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.user.is_staff or project.user == request.user:
        project.delete()
        return HttpResponse("Done")
    return APIResponse(550)

@api_view(['GET'])
@access_error_wrapper
def download_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.user.is_staff or project.user == request.user:
        shutil.make_archive("files/storage/"+project.name, 'zip', project.directory.GetPath())
        zip = open("files/storage/"+project.name+".zip", 'rb')
        response = HttpResponse(content=zip)
        response['Content-Type'] = 'application/zip, application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' \
                                          % project.name
        os.remove("files/storage/" + project.name + ".zip")
        return response
    return APIResponse(550)