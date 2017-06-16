from django.shortcuts import render
from .models import File,Directory,Project
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
import time

# Create your views here.

def access_file(request, file_id):
    if request.user.is_authenticated:
        file = File.objects.get(id=file_id)
        if file is None or file.directory.GetProject() is None:
            raise Http404("File doesn't exist")
        else:
            owner = file.directory.GetProject().user
            if request.user.is_staff or owner.id == request.user.id:
                return HttpResponse(file.get_str())
            else:
                raise PermissionDenied
    else:
        raise PermissionDenied
        
def generate_project(request, project_name, user_id):
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
    return HttpResponse("hello 2amr")

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))