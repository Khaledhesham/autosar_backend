from django.http import HttpResponse
from django.template import loader
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer
from django.contrib.auth import authenticate,login
from django.core.exceptions import PermissionDenied

from rest_framework.decorators import api_view

@api_view(['POST'])
def check(request):
    return HttpResponse(str(request.user))

def index(request):
    template = loader.get_template('registration/index.html')
    return HttpResponse(template.render(request))