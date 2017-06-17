from rest_framework import serializers
from files.models import Project,File,Directory
from registration_system.serializers import UserSerializer

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class FileSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ('name', 'id', 'type')

    def get_type(self,obj):
        return obj.file_type

class DirectorySerializer(serializers.HyperlinkedModelSerializer):
    children = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Directory
        # fields = ('name', 'id', 'file_set' , 'directory_set')
        fields = ('name', 'id', 'children', 'type')

    def get_type(self,obj):
        return "directory"

    def get_children(self, obj):
        items = []
        for item_file in obj.file_set.all():
            items.append(FileSerializer(instance=item_file).data)
        for item_dir in obj.directory_set.all():
            items.append(DirectorySerializer(instance=item_dir).data)
        return items

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'id', 'directory', 'user')
    directory = DirectorySerializer()
    user = UserSerializer()
