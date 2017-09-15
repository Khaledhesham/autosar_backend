from autosar_studio.helpers import APIResponse, access_error_wrapper, OwnsFile
import arxml.models as ArxmlModels
from files.models import File, Directory, Project
from django.core.exceptions import PermissionDenied, Http404
from rest_framework.decorators import api_view
from django.http import HttpResponse

### software component

def GetProjectIfOwns(user, project_id):
    project = Project.objects.get(pk=project_id)

    if user.is_staff or project.user == user:
        return project

    raise PermissionDenied


def GetCompositionIfOwns(user, id):
    composition = ArxmlModels.Composition.objects.get(project_id=id)
    file = composition.file

    if file is None:
        raise Http404

    if not OwnsFile(file, user):
        raise PermissionDenied

    return composition


def GetSoftwareComponentIfOwns(user, id):
    component = ArxmlModels.SoftwareComponent.objects.get(pk=id)
    file = component.file

    if file is None:
        raise Http404

    if not OwnsFile(file, user):
        raise PermissionDenied

    return component


@api_view(['POST'])
@access_error_wrapper
def add_software_component(request):
    project = Project.objects.get(id=request.POST['project_id'])
    file = File
    try:
        if project is not None and project.user == request.user:
            file = File(directory=project.directory, file_type="arxml", name=request.POST['name'])
            file.save()
            swc_directory = Directory(name=request.POST['name'], parent=project.directory)
            swc_directory.save()
            rte_types = File(directory=swc_directory, file_type="h", name='rtetypes')
            rte_types.save()
            rte_types.Write(open("files/default_datatypes.orig").read())
            datatypes = File(directory=swc_directory, file_type="h", name=request.POST['name'] + '_datatypes')
            datatypes.save()
            rte = File(directory=swc_directory, file_type="h", name=request.POST['name'] + '_rte')
            rte.save()
            runnables_file = File(directory=swc_directory, file_type="c", name=request.POST['name'] + '_runnables')
            runnables_file.save()
            swc = ArxmlModels.SoftwareComponent(name=request.POST['name'], composition=project.composition, file=file, x=request.POST['x'], y=request.POST['y'], \
                    rte_datatypes_file=rte_types, datatypes_file=datatypes, rte_file=rte, child_directory=swc_directory, runnables_file=runnables_file, package=project.package)
            swc.save()
            swc.Rewrite()
            RunnableCFile(runnables_file.Open('w+'), swc)
            project.composition.Rewrite()
            return HttpResponse(swc.id)
        return APIResponse(550)
    except Exception as e:
        if file.id is not None:
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

@api_view(['POST'])
@access_error_wrapper
def move_softwareComponent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    composition = swc.composition
    swc.x = request.POST['x']
    swc.y = request.POST['y']
    swc.save()
    swc.Rewrite()
    composition.Rewrite()
    return HttpResponse("True")


### port


@api_view(['POST'])
@access_error_wrapper
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
    project = GetProjectIfOwns(request.user, request.POST['project_id'])
    package = project.package
    interface = ArxmlModels.Interface(name=request.POST['name'], package=package)
    interface.save()

    if request.POST['type'] and request.POST['type'] == "CS":
        interface.type = "CLIENT-SERVER-INTERFACE"
        sender_receiver_if = ArxmlModels.SenderReceiverInterface(interface=interface)
        sender_receiver_if.save()
    else:
        interface.type = "SENDER-RECEIVER-INTERFACE"
        interface.save()
        client_server_if = ArxmlModels.ClientServerInterface(interface=interface)
        client_server_if.save()

    package.Rewrite()
    return HttpResponse(interface.id)


@api_view(['POST'])
@access_error_wrapper
def set_port_interface(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if interface is None or interface.package != swc.package:
        return APIResponse(404, {'error': "Invalid Interface" })

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None or port.swc != swc:
        return APIResponse(404, {'error': "Invalid Port"})

    if port.type == "P-PORT-PROTOTYPE":
        port.provided_interface = interface
    else:
        port.interface = interface

    port.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def add_port_dataelement(request):
    data_element = ArxmlModels.DataElement.objects.get(pk=request.POST['data_element_id'])
    if data_element is None:
        return APIResponse(404, {'error': "Invalid Data Element" })
    if data_element.interface.package.project.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None:
        return APIResponse(404, {'error': "Invalid Port"})
    if port.swc.package.project.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    interface = port.interface

    if data_element.interface != interface:
        return APIResponse(404, {'error': "Data Element Doesn't belong to the Port's Interface"})

    ref = ArxmlModels.DataElementRef(data_element=data_element, port=port)
    ref.save()
    ref.port.swc.Rewrite()
    return HttpResponse(ref.id)

@api_view(['POST'])
@access_error_wrapper
def remove_port_dataelement(request):
    data_element_ref = ArxmlModels.DataElementRef.objects.get(pk=request.POST['element_ref_id'])
    if request.user.is_staff or data_element_ref.port.swc.package.user == request.user:
        swc = data_element_ref.port.swc
        data_element_ref.delete()
        swc.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied


@api_view(['POST'])
@access_error_wrapper
def add_port_operation(request):
    operation = ArxmlModels.Operation.objects.get(pk=request.POST['operation_id'])
    if operation is None:
        return APIResponse(404, {'error': "Invalid Operation" })
    if operation.interface.package.project.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    port = ArxmlModels.Port.objects.get(pk=request.POST['port_id'])
    if port is None:
        return APIResponse(404, {'error': "Invalid Port"})
    if port.swc.package.project.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    interface = port.interface

    if operation.interface != interface:
        return APIResponse(404, {'error': "Operation Doesn't belong to the Port's Interface"})

    ref = ArxmlModels.OperationRef(operation=operation, port=port)
    ref.save()
    ref.port.swc.Rewrite()
    return HttpResponse(ref.id)


@api_view(['POST'])
@access_error_wrapper
def remove_port_operation(request):
    operation_ref = ArxmlModels.OperationRef.objects.get(pk=request.POST['operation_ref_id'])
    if request.user.is_staff or operation_ref.port.swc.package.user == request.user:
        swc = operation_ref.port.swc
        operation_ref.delete()
        swc.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied


@api_view(['POST'])
@access_error_wrapper
def remove_interface(request):
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if request.user.is_staff or interface.package.project.user == request.user:
        package = interface.package
        interface.delete()
        package.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied


@api_view(['POST'])
@access_error_wrapper
def rename_interface(request):
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])
    if request.user.is_staff or interface.package.project.user == request.user:
        interface.name = request.POST['name']
        interface.save()
        interface.package.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied

### datatype


@api_view(['POST'])
@access_error_wrapper
def add_datatype(request):
    project = GetProjectIfOwns(request.user, request.POST['project_id'])

    if request.POST['type'] not in { "Boolean", "Float", "SInt8", "UInt8", "SInt16", "UInt16", "SInt32", "UInt32" }:
        return APIResponse(404, { 'error' : "Unsupported Type" })

    data_type = ArxmlModels.DataType(type=request.POST['type'], package=project.package)
    data_type.save()
    project.package.Rewrite()
    return HttpResponse(data_type.id)


@api_view(['POST'])
@access_error_wrapper
def remove_datatype(request):
    data_type = ArxmlModels.DataType.objects.get(pk=request.POST['datatype_id'])

    if request.user.is_staff or data_type.package.project.user == request.user:
        data_type.delete()
        data_type.package.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied


### Operation
@api_view(['POST'])
@access_error_wrapper
def add_operation(request):
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])

    if interface is None or not hasattr(interface, 'clientserverinterface'):
        return APIResponse(404, { 'error' : "Invalid Interface" })
    if not request.user.is_staff or interface.package.project.user != request.user:
        raise PermissionDenied

    operation = ArxmlModels.DataElement(name=request.POST['name'], interface=interface.clientserverinterface)
    operation.save()
    interface.package.Rewrite()
    return HttpResponse(operation.id)


### Argument
@api_view(['POST'])
@access_error_wrapper
def add_argument(request):
    operation = ArxmlModels.Operation.objects.get(pk=request.POST['operation_id'])

    if not request.user.is_staff or operation.interface.interface.package.project.user != request.user:
        raise PermissionDenied

    data_type = ArxmlModels.DataType.objects.get(pk=request.POST['datatype_id'])
    if data_type is None:
        return APIResponse(404, { 'error' : "Invalid Type" })
    if not request.user.is_staff or data_type.package.project.user != request.user:
        raise PermissionDenied

    if request.POST['direction'] not in ['IN', 'OUT']:
        return APIResponse(404, { 'error' : "Argument direction is not correct" })

    argument = ArxmlModels.DataElement(name=request.POST['name'], interface=operation.interface.clientserverinterface, type=data_type, direction=request.POST['name'])
    argument.save()
    operation.interface.interface.package.Rewrite()
    return HttpResponse(argument.id)


### Error
@api_view(['POST'])
@access_error_wrapper
def add_application_error(request):
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])

    if not request.user.is_staff or interface.package.project.user != request.user:
        raise PermissionDenied

    if not hasattr(interface, 'clientserverinterface'):
        return APIResponse(404, { 'error' : "Invalid Interface" })

    error = ArxmlModels.ApplicationError(name=request.POST['name'], error_code=request.POST['code'], interface=interface.clientserverinterface)
    error.save()
    interface.package.Rewrite()
    return HttpResponse(error.id)


### data element


@api_view(['POST'])
@access_error_wrapper
def add_dataelement(request):
    interface = ArxmlModels.Interface.objects.get(pk=request.POST['interface_id'])

    if interface is None or not hasattr(interface, 'senderreceiverinterface'):
        return APIResponse(404, { 'error' : "Invalid Interface" })
    if not request.user.is_staff or interface.package.project.user != request.user:
        raise PermissionDenied
    
    data_type = ArxmlModels.DataType.objects.get(pk=request.POST['datatype_id'])
    if data_type is None:
        return APIResponse(404, { 'error' : "Invalid Type" })
    if not request.user.is_staff or data_type.package.project.user != request.user:
        raise PermissionDenied

    if data_type.package != interface.package:
        return APIResponse(404, { 'error' : "DataType and Interface don't belong to the same Project" })

    element = ArxmlModels.DataElement(name=request.POST['name'], interface=interface.senderreceiverinterface, type=data_type)
    element.save()
    interface.package.Rewrite()
    return HttpResponse(element.id)


@api_view(['POST'])
@access_error_wrapper
def rename_dataelement(request):
    element = ArxmlModels.DataElement.objects.get(pk=request.POST['dataElement_id'])
    if request.user.is_staff or element.interface.interface.package.project.user == request.user:
        element.name = request.POST['name']
        element.save()
        element.interface.interface.package.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied


@api_view(['POST'])
@access_error_wrapper
def remove_dataelement(request):
    element = ArxmlModels.DataElement.objects.get(pk=request.POST['dataElement_id'])
    if request.user.is_staff or element.interface.interface.package.project.user == request.user:
        package = element.interface.interface.package
        element.delete()
        package.Rewrite()
        return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def set_dataelement_type(request):
    element = ArxmlModels.DataElement.objects.get(pk=request.POST['dataElement_id'])
    package = element.interface.interface.package
    if request.user.is_staff or request.user == package.project.user:
        for data_type in package.datatype_set.all():
            if data_type.type == request.POST['type']:
                element.type = data_type
                element.save()
                element.interface.interface.package.Rewrite()
                return HttpResponse("True")
        
        return APIResponse(404, { 'error' : "Datatype is not supported in the current project" })

    raise PermissionDenied


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


@api_view(['POST'])
@access_error_wrapper
def set_runnable_concurrent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable.swc == swc:
        runnable.concurrent = bool(request.POST['concurrent'])
        runnable.save()
        swc.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied

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


@api_view(['POST'])
@access_error_wrapper
def set_timingEvent_runnable(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.TimingEvent.objects.get(pk=request.POST['timingEvent_id'])
    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if event.swc == swc and runnable.swc == swc:
        event.runnable = runnable
        event.save()
        swc.Rewrite()   
        return HttpResponse("True")

    raise PermissionDenied


@api_view(['POST'])
@access_error_wrapper
def set_timingEvent_period(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.TimingEvent.objects.get(pk=request.POST['timingEvent_id'])
    if event.swc == swc:
        event.period = float(request.POST['period'])
        event.save()
        swc.Rewrite()   
        return HttpResponse("True")

    raise PermissionDenied


### Operation Invoked events


@api_view(['POST'])
@access_error_wrapper
def add_operationInvokedEvent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    operationRef = ArxmlModels.OperationRef.objects.get(pk=request.POST['operation_ref_id'])
    if operationRef is None or operationRef.port.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Operation Reference" })

    event = ArxmlModels.OperationInvokedEvent(name=request.POST['name'], runnable=runnable, swc=swc, operation_ref=operationRef)
    event.save()
    swc.Rewrite()
    return HttpResponse(event.id)


@api_view(['POST'])
@access_error_wrapper
def rename_operationInvokedEvent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.OperationInvokedEvent.objects.get(pk=request.POST['operationInvokedEvent_id'])
    event.name = request.POST['name']
    event.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_operationInvokedEvent(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.OperationInvokedEvent.objects.get(pk=request.POST['operationInvokedEvent_id'])
    event.delete()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def set_operationInvokedEvent_runnable(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    event = ArxmlModels.OperationInvokedEvent.objects.get(pk=request.POST['operationInvokedEvent_id'])
    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if event.swc == swc and runnable.swc == swc:
        event.runnable = runnable
        event.save()
        swc.Rewrite()   
        return HttpResponse("True")

    raise PermissionDenied


### data access


@api_view(['POST'])
@access_error_wrapper
def add_dataaccess(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    element = ArxmlModels.DataElementRef.objects.get(pk=request.POST['element_ref_id'])
    if element is None or element.port.swc != swc:
        return APIResponse(404, { 'error' : "Invalid DataElement Reference" })

    type = "DATA-READ-ACCESS"
    if element.port.type == "P-PORT-PROTOTYPE":
        type = "DATA-WRITE-ACCESS"

    access = ArxmlModels.DataAccess(name=request.POST['name'], runnable=runnable, data_element_ref=element, type=type)
    access.save()
    swc.Rewrite()
    return HttpResponse(access.id)


@api_view(['POST'])
@access_error_wrapper
def rename_dataaccess(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    access = ArxmlModels.DataAccess.objects.get(pk=request.POST['dataAccess_id'])
    access.name = request.POST['name']
    access.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_dataaccess(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    access = ArxmlModels.DataAccess.objects.get(pk=request.POST['dataAccess_id'])
    access.delete()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def set_dataaccess_element_ref(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    access = ArxmlModels.DataAccess.objects.get(pk=request.POST['dataAccess_id'])
    data_element_ref = ArxmlModels.DataElementRef.objects.get(pk=request.POST['element_ref_id'])
    if access.runnable.swc == swc:
        access.data_element_ref = data_element_ref
        access.save()
        swc.Rewrite()
        return HttpResponse("True")


### Call Point
@api_view(['POST'])
@access_error_wrapper
def add_callPoint(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    operation_ref = ArxmlModels.OperationRef.objects.get(pk=request.POST['operation_ref_id'])
    if operation_ref is None or operation_ref.port.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Operation Reference" })

    callPoint = ArxmlModels.ServerCallPoint(name=request.POST['name'], runnable=runnable, operation_ref=operation_ref)
    callPoint.save()
    swc.Rewrite()
    return HttpResponse(callPoint.id)


@api_view(['POST'])
@access_error_wrapper
def rename_callPoint(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    callPoint = ArxmlModels.ServerCallPoint.objects.get(pk=request.POST['callPoint_id'])
    callPoint.name = request.POST['name']
    callPoint.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_callPoint(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    callPoint = ArxmlModels.ServerCallPoint.objects.get(pk=request.POST['callPoint_id'])
    callPoint.delete()
    swc.Rewrite()
    return HttpResponse("True")


### Variable


@api_view(['POST'])
@access_error_wrapper
def add_variable(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    
    data_type = ArxmlModels.DataType.objects.get(pk=request.POST['datatype_id'])
    if data_type is None:
        return APIResponse(404, { 'error' : "Invalid Type" })
    if not request.user.is_staff or data_type.package.project.user != request.user:
        raise PermissionDenied

    variable = ArxmlModels.Variable(name=request.POST['name'], swc=swc, type=data_type)
    variable.save()
    swc.package.Rewrite()
    return HttpResponse(element.id)


@api_view(['POST'])
@access_error_wrapper
def rename_variable(request):
    variable = ArxmlModels.Variable.objects.get(pk=request.POST['variable_id'])
    if request.user.is_staff or variable.swc.package.project.user == request.user:
        variable.name = request.POST['name']
        variable.save()
        variable.swc.package.Rewrite()
        return HttpResponse("True")

    raise PermissionDenied


@api_view(['POST'])
@access_error_wrapper
def remove_variable(request):
    variable = ArxmlModels.Variable.objects.get(pk=request.POST['variable_id'])
    if request.user.is_staff or variable.swc.package.project.user == request.user:
        package = variable.swc.package
        variable.delete()
        package.Rewrite()
        return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def set_variable_type(request):
    variable = ArxmlModels.DataElement.objects.get(pk=request.POST['variable_id'])
    package = variable.swc.package
    if request.user.is_staff or request.user == package.project.user:
        for data_type in package.datatype_set.all():
            if data_type.type == request.POST['type']:
                variable.type = data_type
                variable.save()
                variable.swc.package.Rewrite()
                return HttpResponse("True")
        
        return APIResponse(404, { 'error' : "Datatype is not supported in the current project" })

    raise PermissionDenied

### Variable Write Ref


@api_view(['POST'])
@access_error_wrapper
def add_writeRef(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    variable = ArxmlModels.Variable.objects.get(pk=request.POST['variable_id'])
    if variable is None or variable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Variable" })

    ref = ArxmlModels.WriteVariableRef(name=request.POST['name'], runnable=runnable, variable=variable)
    ref.save()
    swc.Rewrite()
    return HttpResponse(access.id)


@api_view(['POST'])
@access_error_wrapper
def rename_writeRef(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    ref = ArxmlModels.WriteVariableRef.objects.get(pk=request.POST['writeRef_id'])
    ref.name = request.POST['name']
    ref.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_writeRef(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    ref = ArxmlModels.WriteVariableRef.objects.get(pk=request.POST['writeRef_id'])
    ref.delete()
    swc.Rewrite()
    return HttpResponse("True")


### Variable Read Ref


@api_view(['POST'])
@access_error_wrapper
def add_readRef(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])

    runnable = ArxmlModels.Runnable.objects.get(pk=request.POST['runnable_id'])
    if runnable is None or runnable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Runnable" })

    variable = ArxmlModels.Variable.objects.get(pk=request.POST['variable_id'])
    if variable is None or variable.swc != swc:
        return APIResponse(404, { 'error' : "Invalid Variable" })

    ref = ArxmlModels.ReadVariableRef(name=request.POST['name'], runnable=runnable, variable=variable)
    ref.save()
    swc.Rewrite()
    return HttpResponse(access.id)


@api_view(['POST'])
@access_error_wrapper
def rename_readRef(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    ref = ArxmlModels.ReadVariableRef.objects.get(pk=request.POST['readRef_id'])
    ref.name = request.POST['name']
    ref.save()
    swc.Rewrite()
    return HttpResponse("True")


@api_view(['POST'])
@access_error_wrapper
def remove_readRef(request):
    swc = GetSoftwareComponentIfOwns(request.user, request.POST['swc_id'])
    ref = ArxmlModels.ReadVariableRef.objects.get(pk=request.POST['readRef_id'])
    ref.delete()
    swc.Rewrite()
    return HttpResponse("True")


### connector


@api_view(['POST'])
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
