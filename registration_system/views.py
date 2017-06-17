from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import unicodedata

class ExampleView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': unicodedata(request.user),  # `django.contrib.auth.User` instance.
            'auth': unicodedata(request.auth),  # None
        }
        return Response(content)

def index(request):
    template = loader.get_template('registration/index.html')
    return HttpResponse(template.render(request))