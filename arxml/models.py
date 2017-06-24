from __future__ import unicode_literals

from django.db import models
import uuid as guid
from files.models import File, Project
from wrapper import CompositionARXML, SoftwareComponentARXML

def GetUUID():
    return str(guid.uuid1())

class SoftwareComponent(models.Model):
    name = models.CharField(max_length=100, default='SoftwareComponent', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    implementation_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    behavior_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    behavior_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    package_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    subpackage_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    composition = models.ForeignKey('Composition', on_delete=models.DO_NOTHING)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

    def Rewrite(self):
        arxml = SoftwareComponentARXML(self, self.file.directory.GetPath())
        self.file.Write(str(arxml))

    def __str__(self):
        return self.name

class Port(models.Model):
    name = models.CharField(max_length=100, default='Port', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    type = models.CharField(max_length=40)
    interface = models.ForeignKey('Interface', on_delete=models.DO_NOTHING, blank=True)

    def __str__(self):
        return self.name

class TimingEvent(models.Model):
    name = models.CharField(max_length=100, default='TimingEvent', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    runnable = models.ForeignKey('Runnable', on_delete=models.CASCADE)
    period = models.FloatField()

    def __str__(self):
        return self.name

class Runnable(models.Model):
    name = models.CharField(max_length=100, default='Runnable', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    concurrent = models.BooleanField()

    def __str__(self):
        return self.name

class Interface(models.Model):
    name = models.CharField(max_length=100, default='Interface', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    type = models.CharField(max_length=40, default='SENDER-RECEIVER-INTERFACE')

    def __str__(self):
        return self.name

class DataType(models.Model):
    type = models.CharField(max_length=10, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)

class DataElement(models.Model):
    name = models.CharField(max_length=100, default='DataElement', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    type = models.ForeignKey(DataType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DataAccess(models.Model):
    name = models.CharField(max_length=100, default='DataAccess', unique=True)
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    runnable = models.ForeignKey(Runnable, on_delete=models.CASCADE)
    data_element = models.ForeignKey(DataElement, on_delete=models.CASCADE)
    port = models.ForeignKey(Port, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Composition(models.Model):
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    file = models.OneToOneField(File, on_delete=models.CASCADE)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)

    def Rewrite(self):
        arxml = CompositionARXML(self)
        self.file.Write(str(arxml))

class Connector(models.Model):
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    p_port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='p_port')
    r_port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='r_port')
