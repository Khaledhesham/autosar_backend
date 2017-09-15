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
from arxml.models import SoftwareComponent, TimingEvent, Runnable, Port, SenderReceiverInterface, Interface, DataElement, DataAccess, DataElementRef, DataType
import shutil

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100, default='Autosar')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField('Date Created', default=timezone.now)

    class Meta:
        unique_together = (('name', 'user'),)

    def Make(project_name, req_user):
        project = Project(name=project_name, user=req_user)
        project.save()
        directory_name = project_name + str("-") + str(project.id)
        main_directory = Directory(name=directory_name, project=project)
        main_directory.save()
        arxml_file = File(name="Composition", file_type="arxml", directory=main_directory)
        arxml_file.save()
        interfaces_file = File(name="DataTypesAndInterfaces", file_type="arxml", directory=main_directory)
        interfaces_file.save()
        package = ArxmlModels.Package(project=project, interfaces_file=interfaces_file)
        package.save()
        package.Rewrite()
        composition = ArxmlModels.Composition(file=arxml_file, project=project)
        composition.save()
        composition.Rewrite()
        return project


    def CreateDefaultsForUser(user):
        ### Blink
        project = Project.Make("Blinker", user)
        swc = SoftwareComponent.Make(project, "Blinker", 33.4, 40.57)
        runnable = Runnable(name="BlinkerRunnable", concurrent=True, swc=swc)
        runnable.save()
        event = TimingEvent(name="TimingEvent", runnable=runnable, period=1)
        event.save()
        interface = Interface(name="Blink", package=project.package, type="SENDER-RECEIVER-INTERFACE")
        interface.save()
        blinker_interface = SenderReceiverInterface(interface=interface)
        blinker_interface.save()
        led_port = Port(name="Led", swc=swc, type="P-PORT-PROTOTYPE", interface=blinker_interface, x=18.5, y=2.4)
        led_port.save()
        type = DataType(package=project.package, type="Boolean")
        type.save()
        blink_element = DataElement(name="BlinkElement", interface=blinker_interface, type=type)
        blink_element.save()
        ref = DataElementRef(port=led_port, data_element=blink_element)
        ref.save()
        acc = DataAccess(name="BlinkerAccess", runnable=runnable, data_element_ref=ref, type="DATA-WRITE-ACCESS")
        acc.save()
        project.package.Rewrite()
        project.package.composition.Rewrite()
        swc.runnables_file.Write(open("files/default_projects/Blinker/Blinker/Blinker_runnables.c").read())

        ###


    def __str__(self):
        return self.name

    def GetSoftwareComponents(self):
        l = list()

        for file in self.directory.file_set.all():
            if hasattr(file, 'swc') and file.swc is not None:
                l.append(file.swc)
                    
        return l

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

@receiver(post_delete, sender=File)
def file_post_delete_handler(sender, **kwargs):
    file_model = kwargs['instance']
    try:
        path = file_model.directory.GetPath()
        if os.path.isdir(path) is True:
            path = path + '/' + file_model.name + '.' + file_model.file_type
            if os.path.isfile(path):
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

    shutil.rmtree(directory.GetPath(), ignore_errors=True)