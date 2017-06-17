from django.http import HttpResponse
from django.template import loader
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from django.contrib.auth import authenticate,login
from django.core.exceptions import PermissionDenied

@api_view(['GET', 'POST', ])
def check(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(username=username, password=password)
    if user is not None:
        data = UserSerializer(instance=user, context={'request': request}).data
        login(request,user)
        return Response(data)
    else:
        raise PermissionDenied

def index(request):
    template = loader.get_template('registration/index.html')
    return HttpResponse(template.render(request))