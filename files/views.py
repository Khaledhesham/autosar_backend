from django.shortcuts import render
from .models import File,Directory,Project
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.models import User
import time

# Create your views here.

def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    return HttpResponse(file.get_str())

def generate_project(request, project_name, user_id):
    directory_name = project_name + str("-") + str(round(time.time() * 1000))
    main_directory = Directory(name=directory_name)
    main_directory.save()
    arxml_file = File(name=project_name, file_type = "arxml", directory= main_directory )
    arxml_file.save()
    sub_directory = Directory(name=project_name, parent=main_directory)
    sub_directory.save()
    c_file = File(name="components", file_type="c", directory=sub_directory)
    c_file.save()
    h_file = File(name="components", file_type="h", directory=sub_directory)
    h_file.save()
    req_user = User.objects.get(id=user_id)
    project = Project(name="project_name", directory = main_directory , user=req_user)
    project.save()
    return HttpResponse("hello 2amr")

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))