from rest_framework import serializers
from files.models import Project,File,Directory
from registration_system.serializers import UserSerializer

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
        fields = ('name', 'id', 'directory', 'user')
    directory = DirectorySerializer()
    user = UserSerializer()
