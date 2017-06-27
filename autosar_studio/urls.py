"""autosar_studio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.contrib import admin
from files import views
from registration_system import views as reg_views
from files.models import Project
from django.contrib.auth.models import User
from rest_framework import viewsets,routers
from files.serializers import ProjectSerializer
from registration_system.serializers import UserSerializer
from rest_framework.authtoken import views as auth_views
from rest_framework.permissions import AllowAny

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes_by_action = {'create': [AllowAny]}

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^files/storage/(?P<file_id>[0-9]+)/?$', views.access_file),
    url(r'^admin/?', admin.site.urls),
    url(r'^users/token/?$', auth_views.obtain_auth_token),
    url(r'^api-auth/?', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^projects/generate/(?P<project_name>[A-Za-z0-9_-]+)/?$',views.generate_project),
    url(r'^arxml/swc/add/?$',views.add_software_component),    
    url(r'^arxml/swc/delete/?$',views.delete_softwareComponent),    
    url(r'^arxml/interface/add/?$',views.add_interface),
    url(r'^arxml/port/add/?$',views.add_port),
    url(r'^arxml/port/delete/?$',views.remove_port),
    url(r'^arxml/port/set_interface/?$',views.set_port_interface),
    url(r'^arxml/datatype/add/?$',views.add_dataType),
    url(r'^arxml/dataelement/add/?$',views.add_dataElement),
    url(r'^arxml/runnable/add/?$',views.add_runnable),
    url(r'^arxml/timing_event/add/?$',views.add_timingEvent),
    url(r'^arxml/data_access/add/?$',views.add_dataAccess),
    url(r'^arxml/connector/add/?$', views.add_connector),
    url(r'^users/projects/(?P<user_id>[0-9]+)/?$',views.get_user_projects),
    url(r'^projects/delete/(?P<project_id>[0-9]+)/?$',views.delete_project),
    url(r'^check_token/?$',reg_views.check),
    url(r'^', include(router.urls)),
]
