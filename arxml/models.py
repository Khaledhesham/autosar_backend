from __future__ import unicode_literals

from django.db import models
import uuid as guid
from files.models import File, Project, Directory
from arxml.wrapper import CompositionARXML, SoftwareComponentARXML, DataTypeHFile, RteHFile, RunnableCompileFile, DataTypesAndInterfacesARXML
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import re
import os
import requests
import json

def GetUUID():
    return str(guid.uuid1())

class Package(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    subpackage_uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    interfaces_file = models.OneToOneField(File, on_delete=models.CASCADE)

    def Rewrite(self):
        for swc in self.softwarecomponent_set.all():
            swc.Rewrite()

        arxml = DataTypesAndInterfacesARXML(self)
        self.interfaces_file.Write(str(arxml))


class SoftwareComponent(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='SoftwareComponent')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    implementation_uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    behavior_uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    composition = models.ForeignKey('Composition', on_delete=models.DO_NOTHING)
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='swc')
    rte_datatypes_file = models.OneToOneField(File, on_delete=models.DO_NOTHING, related_name='rte_datatypes_file')
    datatypes_file = models.OneToOneField(File, on_delete=models.DO_NOTHING, related_name='datatypes_file')
    rte_file = models.OneToOneField(File, on_delete=models.DO_NOTHING, related_name='rte_file')
    runnables_file = models.OneToOneField(File, on_delete=models.DO_NOTHING, related_name='runnables_file')
    child_directory = models.OneToOneField(Directory, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('name', 'composition'),)

    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)

    def Rewrite(self):
        arxml = SoftwareComponentARXML(self, self.file.directory.GetPath())
        DataTypeHFile(self.datatypes_file.Open('w+'), self)
        RteHFile(self.rte_file.Open('w+'), self)
        self.file.Write(str(arxml))

    def __str__(self):
        return self.name

    def PreprocessHeaders(self):
        rte_datatypes_str = self.rte_datatypes_file.Open('r').read()
        datatypes_str = re.sub("#include \"rtetypes.h\"", rte_datatypes_str, self.datatypes_file.Open('r').read())
        rte_str = re.sub("#include \"" + self.name + "_datatypes.h\"", datatypes_str, self.rte_file.Open('r').read())
        return re.sub("#include \"" + self.name + "_rte.h\"", rte_str, self.runnables_file.Open('r').read())


@receiver(pre_delete, sender=SoftwareComponent)
def swc_pre_delete_handler(sender, **kwargs):
    swc = kwargs['instance']
    swc.child_directory.delete()

class Port(models.Model):
    name = models.CharField(max_length=100, default='Port')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    type = models.CharField(max_length=40)
    interface = models.ForeignKey('Interface', on_delete=models.DO_NOTHING, blank=True, null=True)

    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)

    def validate_unique(self, exclude=None):
        qs = Port.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exclude(pk=self.pk).exists():
            raise ValidationError('Port name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(Port, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TimingEvent(models.Model):
    name = models.CharField(max_length=100, default='TimingEvent')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    runnable = models.ForeignKey('Runnable', on_delete=models.CASCADE)
    period = models.FloatField()

    def validate_unique(self, exclude=None):
        qs = TimingEvent.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exclude(pk=self.pk).exists():
            raise ValidationError('Event name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(TimingEvent, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Runnable(models.Model):
    name = models.CharField(max_length=100, default='Runnable')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    concurrent = models.BooleanField()

    def validate_unique(self, exclude=None):
        qs = Runnable.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exclude(pk=self.pk).exists():
            raise ValidationError('Runnable name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(Runnable, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def Compile(self):
        header = self.swc.PreprocessHeaders()
        file = open("/files/storage/" + self.id + "_compile_file.c", 'w+')
        file.write(header)
        RunnableCompileFile(file, self)

        data = {
            'client_secret': "41bf8ec32d2743d1fd40bace3893cb8c31870f2d",
            'async': 0,
            'source': file.read(),
            'lang': "C",
            'time_limit': 3,
            'memory_limit': 1024,
        }

        r = requests.post(u'http://api.hackerearth.com/code/run/', data=data)

        outputs = json.loads(r.text)["run_status"]["output"]

        for access in self.dataaccess_set.all():
            if access.type == "DATA-WRITE-ACCESSS" and access.data_element_ref.data_element.name in outputs:
                access.data_element_ref.data_element.SetValue(outputs[access.data_element_ref.data_element.name])

        file.close()
        os.remove("/files/storage/" + self.id + "_compile_file.c")

        return outputs


class Interface(models.Model):
    name = models.CharField(max_length=100, default='Interface')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    type = models.CharField(max_length=40, default='SENDER-RECEIVER-INTERFACE')

    class Meta:
        unique_together = (('name', 'package'),)

    def __str__(self):
        return self.name


class DataType(models.Model):
    type = models.CharField(max_length=10)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('type', 'package'),)


class DataElement(models.Model):
    name = models.CharField(max_length=100, default='DataElement')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    type = models.ForeignKey(DataType, on_delete=models.CASCADE)

    bool_value = models.BooleanField(default=False)
    float_value = models.FloatField(default=0.0)
    int_value = models.IntegerField(default=0)

    def validate_unique(self, exclude=None):
        qs = DataElement.objects.filter(name=self.name)
        if qs.filter(interface__package=self.interface.package).exclude(pk=self.pk).exists():
            raise ValidationError('Data Element name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(DataElement, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def Reset(self):
        self.bool_value = False
        self.float_value = 0.0
        self.int_value = 0
        
    def SetValue(self, val):
        if self.type.type == "Boolean":
            self.bool_value = bool(val)
        elif self.type.type == "Float":
            self.float_value = float(val)
        else:
            self.int_value = int(val)

    def GetValue(self):
        if self.type.type == "Boolean":
            return self.bool_value
        elif self.type.type == "Float":
            return self.float_value
        else:
            return self.int_value


class DataElementRef(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE)
    data_element = models.ForeignKey(DataElement, on_delete=models.CASCADE)
    timeout = models.FloatField(default=60.0)

    class Meta:
        unique_together = (('port', 'data_element'),)


class DataAccess(models.Model):
    name = models.CharField(max_length=100, default='DataAccess')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    runnable = models.ForeignKey(Runnable, on_delete=models.CASCADE)
    data_element_ref = models.ForeignKey(DataElementRef, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)

    def validate_unique(self, exclude=None):
        qs = DataAccess.objects.filter(name=self.name)
        if qs.filter(runnable__swc__composition=self.runnable.swc.composition).exclude(pk=self.pk).exists():
            raise ValidationError('Data Access name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(DataAccess, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Composition(models.Model):
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    file = models.OneToOneField(File, on_delete=models.CASCADE)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)

    def Rewrite(self):
        arxml = CompositionARXML(self)
        self.file.Write(str(arxml))


class Connector(models.Model):
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    p_port = models.OneToOneField(Port, on_delete=models.CASCADE, related_name='p_port')
    r_port = models.OneToOneField(Port, on_delete=models.CASCADE, related_name='r_port')

    class Meta:
        unique_together = (('p_port', 'composition'),('r_port', 'composition'),)
