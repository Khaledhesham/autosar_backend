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
    children = serializers.SerializerMethodField()

    class Meta:
        model = Directory
        # fields = ('name', 'id', 'file_set' , 'directory_set')
        fields = ('name', 'id', 'children')

    def get_children(self, obj):
        items = []
        for item_file in obj.file_set.all():
            item_file.type = 'file'
            items.append(FileSerializer(instance=item_file).data)
        for item_dir in obj.directory_set.all():
            item_dir.type = 'folder'
            items.append(DirectorySerializer(instance=item_dir).data)
        return items

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'id', 'directory', 'user')
    directory = DirectorySerializer()
    user = UserSerializer()
