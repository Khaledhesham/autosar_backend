import os
import shutil
import arxml.models as ArxmlModels
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .serializers import ProjectSerializer
from arxml.serializers import CompositionSerializer
from autosar_studio.helpers import APIResponse, access_error_wrapper, OwnsFile
from files.models import File, Directory, Project
from django.core.exceptions import PermissionDenied


@api_view(['GET'])
@access_error_wrapper
def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    if OwnsFile(file, request.user) is True:
        return HttpResponse(file.Read())
    return APIResponse(550)


@api_view(['POST'])
@access_error_wrapper
def generate_project(request, project_name):
    req_user = request.user
    project = Project(name=project_name , user=req_user)
    project.save()
    directory_name = project_name + str("-") + str(project.id)
    main_directory = Directory(name=directory_name, project=project)
    main_directory.save()
    arxml_file = File(name="Composition", file_type="arxml", directory=main_directory)
    arxml_file.save()
    interfaces_file = File(name="DataTypesAndInterfaces", file_type="arxml", directory=main_directory)
    interfaces_file.save()
    package = ArxmlModels.Package(project=project, interfaces_file=interfaces_file)
    package.save()
    package.Rewrite()
    composition = ArxmlModels.Composition(file=arxml_file, project=project)
    composition.save()
    composition.Rewrite()
    factory = APIRequestFactory()
    request = factory.get('/')
    ser = ProjectSerializer(instance=project, context={ 'request': Request(request) })
    return Response(ser.data)


# project


@api_view(['GET'])
@access_error_wrapper
def get_user_projects(request):
    projects = Project.objects.filter(user=request.user)
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


@api_view(['POST'])
@access_error_wrapper
def update_c_file(request):
    file = File.objects.get(pk=request.POST['file_id'])

    if request.user.is_staff or request.user == file.directory.GetProject():
        file.Write(request.POST['content'])
        return HttpResponse("True")

    raise PermissionDenied
