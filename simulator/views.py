import json
from autosar_studio.helpers import APIResponse, access_error_wrapper
from files.models import Project
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse


# Simulation

@api_view(['POST'])
@access_error_wrapper
def get_input_output_list(request):
    project = Project.objects.get(pk=request.POST['project_id'])

    if request.user.is_staff or request.user == project.user:
        d = dict()
        d['inputs'] = dict()
        d['outputs'] = dict()

        for swc in project.GetSoftwareComponents():
            for port in swc.port_set.all():
                if not hasattr(port, 'p_port_connector') and not hasattr(port, 'r_port_connector'):
                    l = list()

                    for de_ref in port.dataelementref_set.all():
                        l.append({ 'name': de_ref.data_element.name, 'type': de_ref.data_element.type.type, 'id': de_ref.data_element.id })

                    if len(l) > 0:
                        if port.type == "R-PORT-PROTOTYPE":
                            d['inputs'][port.name] = l
                        else:
                            d['outputs'][port.name] = l

        return JsonResponse(d)
    raise PermissionDenied


def set_values(project, d):
    user_values = set()

    for key in d:
        user_values.add(str(key))

    user_values = sorted(user_values)

    s = set()

    data = dict()
    data['events'] = dict()

    for swc in project.GetSoftwareComponents():
        for port in swc.port_set.all():
            for de_ref in port.dataelementref_set.all():
                if port.type == "R-PORT-PROTOTYPE":
                    if not hasattr(port, 'p_port_connector') and not hasattr(port,
                                                                             'r_port_connector'):
                        s.add(de_ref.data_element.name)

    s = sorted(s)

    if s != user_values:  # Validation
        return APIResponse(404, {'error': 'Some input values are missing'})

    inputs_file = open(project.directory.GetPath() + "/inputs.txt", 'w+')

    print(s)
    for i in s:
        out = str(d[i])
        if out == "False":
            out = "0"
        if out == "True":
            out = "1"

        print(out + ",", end="", file=inputs_file)

    inputs_file.close()

    return True


@api_view(['POST'])
def start_simulation(request):
    d = json.loads(request.POST['values'])
    project = Project.objects.get(pk=request.POST['project_id'])
    project.package.Rewrite()

    if request.user.is_staff or request.user == project.user:
        reply = set_values(project, d)
        if reply is True:
            return HttpResponse(project.package.Compile())
        else:
            return HttpResponse(reply)

    raise PermissionDenied


@api_view(['POST'])
def set_simulation_values(request):
    d = json.loads(request.POST['values'])
    project = Project.objects.get(pk=request.POST['project_id'])

    if request.user.is_staff or request.user == project.user:
        reply = set_values(project, d)
        if reply is True:
            return HttpResponse("True")
        else:
            return reply

    raise PermissionDenied


@api_view(['POST'])
def get_simulation_values(request):
    project = Project.objects.get(pk=request.POST['project_id'])

    if request.user.is_staff or request.user == project.user:
        file = open(project.directory.GetPath() + "/outputs.txt", 'r')
        s = file.read()
        file.close()

        file = open(project.directory.GetPath() + "/log.txt", 'r+')
        l = file.readlines()
        file.close()
        file = open(project.directory.GetPath() + "/log.txt", 'w+')
        file.close()

        return JsonResponse( {"output" : s, "logging" : l} )

    raise PermissionDenied

