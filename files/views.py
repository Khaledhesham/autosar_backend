import os
import shutil
import arxml.models as ArxmlModels
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .serializers import ProjectSerializer
from arxml.serializers import CompositionSerializer
from autosar_studio.helpers import APIResponse, access_error_wrapper, OwnsFile
from files.models import File, Project
from django.core.exceptions import PermissionDenied
from registration_system.models import MakeProject, CreateDefaultsForUser
import json


@api_view(['GET'])
@access_error_wrapper
def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    if OwnsFile(file, request.user) is True:
        return HttpResponse(file.Read())
    return APIResponse(550)


@api_view(['POST'])
@access_error_wrapper
def get_multiple_files(request):
    l = json.loads(request.POST['file_ids'])
    d = dict()

    for f in l:
        file = File.objects.get(id=f)
        if OwnsFile(file, request.user) is True:
            d[f] = file.Read().decode("utf-8")

    return JsonResponse(d)


@api_view(['POST'])
@access_error_wrapper
def generate_project(request, project_name):
    req_user = request.user
    project = MakeProject(project_name, req_user)
    factory = APIRequestFactory()
    request = factory.get('/')
    ser = ProjectSerializer(instance=project, context={ 'request': Request(request) })
    return Response(ser.data)


# project


@api_view(['GET'])
@access_error_wrapper
def get_user_projects(request):
    projects = Project.objects.filter(user=request.user).order_by('-id')
    serializer = ProjectSerializer(projects, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@access_error_wrapper
def delete_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.user.is_staff or project.user == request.user:
        project.delete()
        return HttpResponse("Done")
    return APIResponse(550)


@api_view(['POST'])
def serialize_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.user.is_staff or project.user == request.user:
        composition = ArxmlModels.Composition.objects.get(project=project)
        serializer = CompositionSerializer(instance=composition, context={'request': request})
        return Response(serializer.data)
    return APIResponse(550)


@api_view(['GET'])
def download_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    if request.user.is_staff or project.user == request.user:
        ignore = shutil.ignore_patterns('*.exe', '*.o', '*.txt')
        shutil.rmtree("files/tmp/" + project.name + "-" + project_id, ignore_errors=True)
        shutil.copytree(project.directory.GetPath(),"files/tmp/" + project.name + "-" + project_id,ignore=ignore)
        shutil.make_archive("files/tmp-zip/"+project.name + "-" + project_id, 'zip', "files/tmp/"+project.name + "-" + project_id)
        zip = open("files/tmp-zip/" + project.name + "-" + project_id + ".zip", 'rb')
        response = HttpResponse(content=zip)
        response['Content-Type'] = 'application/zip, application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' \
                                          % project.name
        shutil.rmtree("files/tmp/" + project.name + "-" + project_id, ignore_errors=True)
        os.remove("files/tmp-zip/" + project.name + "-" + project_id + ".zip")
        return response
    return APIResponse(550)


@api_view(['POST'])
@access_error_wrapper
def update_c_file(request):
    file = File.objects.get(pk=request.POST['file_id'])

    if request.user.is_staff or request.user == file.directory.GetProject().user:
        file.Write(request.POST['content'])
        return HttpResponse("True")

    raise PermissionDenied


### Debug
@api_view(['POST'])
def create_defaults(request):
    CreateDefaultsForUser(request.user)
    return HttpResponse("True")
