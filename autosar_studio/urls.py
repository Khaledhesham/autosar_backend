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
from files import views as file_views
from registration_system import views as reg_views
from arxml import views as arxml_views
from simulator import views as simulator_views
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
    url(r'^files/storage/(?P<file_id>[0-9]+)/?$', file_views.access_file),
    url(r'^admin/?', admin.site.urls),
    url(r'^users/token/?$', auth_views.obtain_auth_token),
    url(r'^api-auth/?', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^projects/generate/(?P<project_name>[A-Za-z0-9_-]+)/?$', file_views.generate_project),
    url(r'^arxml/swc/add/?$', arxml_views.add_software_component),
    url(r'^arxml/swc/rename/?$', arxml_views.rename_softwareComponent),
    url(r'^arxml/swc/delete/?$', arxml_views.delete_softwareComponent),
    url(r'^arxml/swc/move/?$', arxml_views.move_softwareComponent),
    url(r'^arxml/interface/add/?$', arxml_views.add_interface),
    url(r'^arxml/interface/rename/?$', arxml_views.rename_interface),
    url(r'^arxml/interface/delete/?$', arxml_views.remove_interface),
    url(r'^arxml/operation/add/?$', arxml_views.add_operation),
    url(r'^arxml/argument/add/?$', arxml_views.add_argument),
    url(r'^arxml/error/add/?$', arxml_views.add_application_error),
    url(r'^arxml/port/add/?$', arxml_views.add_port),
    url(r'^arxml/port/set_interface/?$', arxml_views.set_port_interface),
    url(r'^arxml/port/add_data_element/?$', arxml_views.add_port_dataelement),
    url(r'^arxml/port/remove_data_element/?$', arxml_views.remove_port_dataelement),
    url(r'^arxml/port/rename/?$', arxml_views.rename_port),
    url(r'^arxml/port/delete/?$', arxml_views.remove_port),
    url(r'^arxml/datatype/add/?$', arxml_views.add_datatype),
    url(r'^arxml/datatype/delete/?$', arxml_views.remove_datatype),
    url(r'^arxml/dataelement/add/?$', arxml_views.add_dataelement),
    url(r'^arxml/dataelement/rename/?$', arxml_views.rename_dataelement),
    url(r'^arxml/dataelement/delete/?$', arxml_views.remove_dataelement),
    url(r'^arxml/dataelement/set_type/?$', arxml_views.set_dataelement_type),
    url(r'^arxml/runnable/add/?$', arxml_views.add_runnable),
    url(r'^arxml/runnable/rename/?$', arxml_views.rename_runnable),
    url(r'^arxml/runnable/delete/?$', arxml_views.remove_runnable),
    url(r'^arxml/runnable/set_concurrent/?$', arxml_views.set_runnable_concurrent),
    url(r'^arxml/timing_event/add/?$', arxml_views.add_timingEvent),
    url(r'^arxml/timing_event/rename/?$', arxml_views.rename_timingEvent),
    url(r'^arxml/timing_event/delete/?$', arxml_views.remove_timingEvent),
    url(r'^arxml/timing_event/set_runnable/?$', arxml_views.set_timingEvent_runnable),
    url(r'^arxml/timing_event/set_period/?$', arxml_views.set_timingEvent_period),
    url(r'^arxml/data_access/add/?$', arxml_views.add_dataaccess),
    url(r'^arxml/data_access/rename/?$', arxml_views.rename_dataaccess),
    url(r'^arxml/data_access/delete/?$', arxml_views.remove_dataaccess),
    url(r'^arxml/data_access/set_element_ref/?$', arxml_views.set_dataaccess_element_ref),
    url(r'^arxml/connector/add/?$', arxml_views.add_connector),
    url(r'^arxml/connector/delete/?$', arxml_views.remove_connector),
    url(r'^users/projects/?$',file_views.get_user_projects),
    url(r'^projects/delete/(?P<project_id>[0-9]+)/?$', file_views.delete_project),
    url(r'^projects/download/(?P<project_id>[0-9]+)/?$', file_views.download_project),
    url(r'^projects/serialize/(?P<project_id>[0-9]+)/?$', file_views.serialize_project),
    url(r'^simulate/get/?$', simulator_views.get_input_output_list),
    url(r'^simulate/start/?$', simulator_views.start_simulation),
    url(r'^simulate/setvalues/?$', simulator_views.set_simulation_values),
    url(r'^simulate/getvalues/?$', simulator_views.get_simulation_values),
    url(r'^check_token/?$', reg_views.check),
    url(r'^files/update/?$', file_views.update_c_file),
    url(r'^userInfo/?$', reg_views.userInfo),
    url(r'^files/defaults/?$', file_views.create_defaults),
    url(r'^arxml/fix/?$', arxml_views.fix_broken_seat_heaters),
    url(r'^', include(router.urls)),
]
