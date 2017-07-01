from __future__ import unicode_literals

from django.db import models
import uuid as guid
from files.models import File, Project, Directory
from arxml.wrapper import CompositionARXML, SoftwareComponentARXML, DataTypeHFile, RteHFile
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import re

def GetUUID():
    return str(guid.uuid1())


class SoftwareComponent(models.Model):
    name = models.CharField(max_length=100, default='SoftwareComponent')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    implementation_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    behavior_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    package_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    subpackage_uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    composition = models.ForeignKey('Composition', on_delete=models.DO_NOTHING)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='file')
    rte_datatypes_file = models.ForeignKey(File, on_delete=models.DO_NOTHING, related_name='rte_datatypes_file')
    datatypes_file = models.ForeignKey(File, on_delete=models.DO_NOTHING, related_name='datatypes_file')
    rte_file = models.ForeignKey(File, on_delete=models.DO_NOTHING, related_name='rte_file')
    runnables_file = models.ForeignKey(File, on_delete=models.DO_NOTHING, related_name='runnables_file')
    child_directory = models.ForeignKey(Directory, on_delete=models.DO_NOTHING)

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

    def PrepareCompileFile(self):
        rte_datatypes_str = self.rte_datatypes_file.Read()
        datatypes_str = re.sub("#include \"rtetypes.h\"", rte_datatypes, self.datatypes_file.Read())
        rte_str = re.sub("#include \"" + self.name + "_datatypes.h\"", datatypes_str, self.rte_file.Read())
        return re.sub("#include \"" + self.name + "_rte.h\"", rte_str, self.runnables_file.Read())


@receiver(pre_delete, sender=SoftwareComponent)
def swc_pre_delete_handler(sender, **kwargs):
    swc = kwargs['instance']
    swc.child_directory.delete()

class Port(models.Model):
    name = models.CharField(max_length=100, default='Port')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    type = models.CharField(max_length=40)
    interface = models.ForeignKey('Interface', on_delete=models.DO_NOTHING, blank=True, null=True)

    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)

    def validate_unique(self, exclude=None):
        qs = Port.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exists():
            raise ValidationError('Port name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(Port, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TimingEvent(models.Model):
    name = models.CharField(max_length=100, default='TimingEvent')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    runnable = models.ForeignKey('Runnable', on_delete=models.CASCADE)
    period = models.FloatField()

    def validate_unique(self, exclude=None):
        qs = TimingEvent.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exists():
            raise ValidationError('Event name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(TimingEvent, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Runnable(models.Model):
    name = models.CharField(max_length=100, default='Runnable')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    concurrent = models.BooleanField()

    def validate_unique(self, exclude=None):
        qs = Runnable.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exists():
            raise ValidationError('Runnable name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(Runnable, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Interface(models.Model):
    name = models.CharField(max_length=100, default='Interface')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    type = models.CharField(max_length=40, default='SENDER-RECEIVER-INTERFACE')

    def validate_unique(self, exclude=None):
        qs = Interface.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exists():
            raise ValidationError('Interface name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(Interface, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class DataType(models.Model):
    type = models.CharField(max_length=10)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('type', 'swc'),)


class DataElement(models.Model):
    name = models.CharField(max_length=100, default='DataElement')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    type = models.ForeignKey(DataType, on_delete=models.CASCADE)

    def validate_unique(self, exclude=None):
        qs = DataElement.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exists():
            raise ValidationError('Data Element name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(DataElement, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class DataElementRef(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE)
    data_element = models.ForeignKey(DataElement, on_delete=models.CASCADE)
    timeout = models.FloatField(default=60.0)

    class Meta:
        unique_together = (('port', 'data_element'),)


class DataAccess(models.Model):
    name = models.CharField(max_length=100, default='DataAccess')
    uid = models.CharField(max_length=20, default=GetUUID, unique=True)
    runnable = models.ForeignKey(Runnable, on_delete=models.CASCADE)
    data_element_ref = models.ForeignKey(DataElementRef, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)

    def validate_unique(self, exclude=None):
        qs = DataAccess.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exists():
            raise ValidationError('Data Access name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()

        super(DataAccess, self).save(*args, **kwargs)

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

    class Meta:
        unique_together = (('p_port', 'composition'),('r_port', 'composition'),)
