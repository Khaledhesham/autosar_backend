from __future__ import unicode_literals

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
import os
from arxml.wrapper import Arxml

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100, default='Autosar')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField('Date Created', default=timezone.now)

    def __str__(self):
        return self.name

class Directory(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField('Date Created', default=timezone.now)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Directories"

    def __str__(self):
        return self.name

    def GetPath(self):
        if self.parent:
            return self.parent.GetPath() + "/" + self.name
        else:
            return "files/storage/" + self.name

    def GetProject(self):
        if self.parent:
            return self.parent.project
        else:
            return self.project

class File(models.Model):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=20)
    name = models.CharField(max_length=100, default='File')
    created_at = models.DateTimeField('Date Created', default=timezone.now)

    class Meta:
        unique_together = (('name', 'file_type', 'directory'),)

    def GetPath(self):
        return self.directory.GetPath() + '/' + self.name + '.' + self.file_type

    def Open(self, mode='rb'):
        return open(self.GetPath(), mode=mode)

    def Write(self, content):
        f = self.Open(mode="w+")
        f.write(content)
        f.close()

    def __str__(self):
        return self.name

    def GetAccessPath(self):
        return '../../../' + "files/storage/" + str(self.id)

    def Read(self):
        return self.Open().read()

class ArxmlFile(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    swc_uid = models.CharField(max_length=20, blank=True)

    def CreateSoftwareComponent(self, name, pos_x, pos_y):
        wrapper = Arxml(self.file.Read(), self.file.directory.GetPath())
        uuid = wrapper.CreateSoftwareComponent(name, pos_x, pos_y)
        self.file.Write(str(wrapper))
        self.swc_uid = uuid
        self.save()
        return uuid

@receiver(post_delete, sender=File)
def file_post_delete_handler(sender, **kwargs):
    file_model = kwargs['instance']
    try:
        path = file_model.directory.GetPath()
        if os.path.isdir(path) is True:
            path = path + '/' + file_model.name + '.' + file_model.file_type
            os.remove(path)
    except Directory.DoesNotExist:
        return

@receiver(post_save, sender=File)
def file_post_save_handler(sender, **kwargs):
    file_model = kwargs['instance']
    old_model = File.objects.get(pk=file_model.id)
    if old_model and os.path.isfile(old_model.GetPath()):
        path = file_model.directory.GetPath() + '/'
        old_name = path + old_model.name + '.' + old_model.file_type
        new_name = path + file_model.name + '.' + file_model.file_type
        if old_name != new_name:
            os.rename(old_name, new_name)
    else:
        file_model.Write('')

@receiver(post_save, sender=Directory)
def directory_post_save_handler(sender, **kwargs):
    directory = kwargs['instance']
    path = directory.GetPath()
    if os.path.isdir(path) is not True:
        os.makedirs(path)

@receiver(pre_delete, sender=Directory)
def directory_pre_delete_handler(sender, **kwargs):
    directory = kwargs['instance']

    for direc in directory.directory_set.all():
        direc.delete()

    for file in directory.file_set.all():
        file.delete()

    path = directory.GetPath()
    if os.path.isdir(path) is True:
        os.rmdir(path)