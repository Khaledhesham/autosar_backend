from autosar_studio.helpers import access_error_wrapper
from django.http import HttpResponse
from django.template import loader
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework.decorators import api_view

@api_view(['POST'])
def check(request):
    return HttpResponse(str(request.user))

def index(request):
    template = loader.get_template('registration/index.html')
    return HttpResponse(template.render(request))

@api_view(['GET'])
@access_error_wrapper
def userInfo(request):
    ser = UserSerializer(instance=request.user, context={'request': Request(request)})
    return Response(ser.data)