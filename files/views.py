from django.shortcuts import render
from .models import File,Directory,Project
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.models import User
import time

current_milli_time = lambda: int(round(time.time() * 1000))

# Create your views here.

def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    return HttpResponse(file.get_str())

def generate_project(request, project_name, user_id):
    directory_name = project_name + current_milli_time
    main_directory = Directory(name=directory_name)
    arxml_file = File(name=project_name, file_type = "arxml", directory= main_directory )
    sub_directory = Directory(name=directory_name, parent=main_directory)
    c_file = File(name="components", file_type="c", directory=sub_directory)
    h_file = File(name="components", file_type="h", directory=sub_directory)
    req_user = User.objects.get(id=user_id)
    project = Project(name="project_name", user=req_user)

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))