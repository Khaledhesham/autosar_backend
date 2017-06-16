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
from files.models import Project,Directory,File
from django.contrib.auth.models import User
import time
from rest_framework import serializers, viewsets, routers

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'password', 'email')
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('name', 'id', 'file_type')

class DirectorySerializer(serializers.HyperlinkedModelSerializer):
    directory_set = RecursiveField(many=True,required=False)

    class Meta:
        model = Directory
        fields = ('name', 'id', 'file_set' , 'directory_set')

    file_set = FileSerializer(many=True, read_only=True)

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'id')
        
    def create(self,validated_data):
        req_user = User.objects.get(id=validated_data['id'])
        project = Project(name=validated_data['name'], user=req_user)
        project.save()
        directory_name = validated_data['name'] + str("-") + str(round(time.time() * 1000))
        main_directory = Directory(name=directory_name, project=project)
        main_directory.save()
        arxml_file = File(name=validated_data['name'], file_type="arxml", directory=main_directory)
        arxml_file.save()
        sub_directory = Directory(name=validated_data['name'], parent=main_directory)
        sub_directory.save()
        c_file = File(name="components", file_type="c", directory=sub_directory)
        c_file.save()
        h_file = File(name="components", file_type="h", directory=sub_directory)
        h_file.save()
        return project


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^files/storage/(?P<file_id>[0-9]+)$', views.access_file),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^generate/(?P<project_name>[A-Za-z0-9_-]+)/(?P<user_id>[0-9]+)/$',views.generate_project),
]
