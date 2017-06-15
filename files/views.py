from django.shortcuts import render
from .models import File
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

# Create your views here.

def access_file(request, file_id):
    if request.user.is_authenticated:
        file = File.objects.get(id=file_id)
        if file.directory.project.user == request.user.id:
            return HttpResponse(file.get_str())
        else:
           raise PermissionDenied
    else:
        raise PermissionDenied

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))