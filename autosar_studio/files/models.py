from __future__ import unicode_literals

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import os

#from projects.cf.models import Project

# Create your models here.

class Directory(models.Model):
    #project = models.ForeignKey(projects.Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField('Date Created', default=timezone.now)
  
    class Meta:
        verbose_name_plural = "Directories"

    def __str__(self):
        return self.name

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
        return '../../../files/storage/' + self.directory.name + '/' + str(self.id)

    def get_str(self):
        f = open('files/storage/' + self.directory.name + '/' + self.name + '.' + self.file_type)
        return f.read()

@receiver(post_delete, sender=File)
def file_post_delete_handler(sender, **kwargs):
    file_model = kwargs['instance']
    path = 'files/storage/' + file_model.directory.name + '/' + file_model.name + '.' + file_model.file_type
    os.remove(path)

@receiver(pre_save, sender=File)
def file_post_save_handler(sender, **kwargs):
    file_model = kwargs['instance']
    if file_model.saved_file:
        path = 'files/storage/' + file_model.directory.name + '/'
        old_name = path + file_model.saved_file.name
        new_name = path + file_model.name + '.' + file_model.file_type
        os.rename(old_name, new_name)
        file_model.saved_file.name = file_model.name + '.' + file_model.file_type
    else:
        def_string = """
        <?xml version="1.0" encoding="UTF-8"?>
        <AUTOSAR xmlns="http://autosar.org/3.2.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/3.2.1 autosar_3-2-1.xsd">
            <TOP-LEVEL-PACKAGES>
            </TOP-LEVEL-PACKAGES>
            <ADMIN-DATA>
                <SDGS>
                <SDG GID="Arccore::AutosarOptions">
                    <SD GID="GENDIR">/multiplier/config</SD>
                </SDG>
                </SDGS>
            </ADMIN-DATA>
        </AUTOSAR>"""

        file_model.saved_file.storage = FileSystemStorage(location='files/storage/' + file_model.directory.name)
        file_model.saved_file.save(file_model.name + '.' + file_model.file_type, ContentFile(def_string), save=False)

@receiver(post_save, sender=Directory)
def directory_post_save_handler(sender, **kwargs):
    directory = kwargs['instance']
    path = 'files//storage/' + directory.name
    if os.path.isdir(path) is not True:
        os.makedirs('files//storage/' + directory.name)

@receiver(post_delete, sender=Directory)
def directory_post_delete_handler(sender, **kwargs):
    directory = kwargs['instance']
    path = 'files//storage/' + directory.name
    if os.path.isdir(path) is True:
        os.rmdir(path)