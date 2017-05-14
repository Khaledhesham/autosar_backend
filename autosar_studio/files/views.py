from django.shortcuts import render
from .models import File
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.

def access_file(request, file_id):
    file = File.objects.get(id=file_id)
    return HttpResponse(file.get_str())