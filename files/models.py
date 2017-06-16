from __future__ import unicode_literals

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import os
from arxml.wrapper import Arxml

#from projects.cf.models import Project

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

class File(models.Model):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=20)
    saved_file = models.FileField(blank=True)
    name = models.CharField(max_length=100, default='File')
    created_at = models.DateTimeField('Date Created', default=timezone.now)

    class Meta:
        unique_together = (('name', 'file_type', 'directory'),)

    def __str__(self):
        return self.name

    def getPath(self):
        return '../../../' + self.directory.GetPath() + '/' + str(self.id)

    def get_str(self):
        f = open(self.directory.GetPath() + '/' + self.name + '.' + self.file_type)
        return f.read()

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
    if file_model.saved_file:
        path = file_model.directory.GetPath() + '/'
        old_name = path + file_model.saved_file.name
        new_name = path + file_model.name + '.' + file_model.file_type
        os.rename(old_name, new_name)
        file_model.saved_file.name = file_model.name + '.' + file_model.file_type
    else:
        def_str = ''

        if file_model.file_type == "arxml":
            def_str = Arxml.CreateDefaultARXML(file_model.directory.name)

        file_model.saved_file.storage = FileSystemStorage(location=file_model.directory.GetPath() + '/')
        file_model.saved_file.save(file_model.name + '.' + file_model.file_type, ContentFile(def_str), save=False)

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