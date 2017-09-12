from __future__ import unicode_literals

from django.db import models
import uuid as guid
from files.models import File, Project, Directory
from arxml.wrapper import CompositionARXML, SoftwareComponentARXML, DataTypeHFile, RteHFile, DataTypesAndInterfacesARXML
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import subprocess
import psutil
import os
from simulator.compile import RunnableCompileFile
import sys

def GetUUID():
    return str(guid.uuid1())


class Package(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    subpackage_uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    interfaces_file = models.OneToOneField(File, on_delete=models.CASCADE)
    proc_id = models.IntegerField(default=0)

    def Rewrite(self):
        for swc in self.softwarecomponent_set.all():
            swc.Rewrite()

        arxml = DataTypesAndInterfacesARXML(self)
        self.interfaces_file.Write(str(arxml))

    def Compile(self):
        file = open(self.project.directory.GetPath() + "/compile_file.c", 'w+')
        RunnableCompileFile(file, self)

        file.close()

        gcc_str = "gcc " + self.project.directory.GetPath() + "/compile_file.c" 

        for swc in self.softwarecomponent_set.all():
            gcc_str = gcc_str + " " + self.project.directory.GetPath() + "/" + swc.name + "/" + swc.name + "_runnables.c"

        if os.name == 'nt':
            gcc_str = gcc_str + " -o " + self.project.directory.GetPath() + "/" + self.project.name + " -lpthread"
        else:
            gcc_str = gcc_str + " -o " + self.project.directory.GetPath() + "/" + self.project.name + ".o" + " -lpthread"

        if self.proc_id > 0 and psutil.pid_exists(self.proc_id):
            try:
                process = psutil.Process(self.proc_id)
                process.kill()
            except Exception:
                pass

            self.proc_id = 0

        file = open(self.project.directory.GetPath() + "/log.txt", 'w+')
        file.close()

        gcc_proc = subprocess.Popen(gcc_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = gcc_proc.communicate()
        exitcode = gcc_proc.returncode

        if exitcode == 0:
            proc = subprocess.Popen

            if os.name == 'nt':
                proc = subprocess.Popen(self.project.directory.GetPath() + "/" + self.project.name, cwd=self.project.directory.GetPath())
            else:
                proc = subprocess.Popen("./" + self.project.name + ".o", cwd=self.project.directory.GetPath())
                
            self.proc_id = proc.pid
            self.save()
            return True

        return err


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


class OperationInvokedEvent(models.Model):
    name = models.CharField(max_length=100, default='OperationInvokedEvent')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)
    runnable = models.ForeignKey('Runnable', on_delete=models.CASCADE)
    operation_ref = models.ForeignKey('OperationRef', on_delete=models.CASCADE)

    def validate_unique(self, exclude=None):
        qs = OperationInvokedEvent.objects.filter(name=self.name)
        if qs.filter(swc__composition=self.swc.composition).exclude(pk=self.pk).exists():
            raise ValidationError('Event name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(OperationInvokedEvent, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Variable(models.Model):
    name = models.CharField(max_length=100, default='Variable')
    type = models.ForeignKey('DataType', on_delete=models.CASCADE)
    comm = models.CharField(max_length=10, default="IMPLICIT")
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    swc = models.ForeignKey(SoftwareComponent, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('swc', 'name'),)

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


class WriteVariableRef(models.Model):
    runnable = models.ForeignKey(Runnable, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)

    def __str__(self):
        return self.runnable.name + ": " + self.variable.name


class ReadVariableRef(models.Model):
    runnable = models.ForeignKey(Runnable, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)

    def __str__(self):
        return self.runnable.name + ": " + self.variable.name


class Interface(models.Model):
    name = models.CharField(max_length=100, default='Interface')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    type = models.CharField(max_length=40, default='SENDER-RECEIVER-INTERFACE')
    provider = models.OneToOneField(Port, on_delete=models.SET_NULL, null=True, related_name="provided_interface")

    class Meta:
        unique_together = (('name', 'package'),)

    def __str__(self):
        return self.name


class SenderReceiverInterface(models.Model):
    interface = models.OneToOneField(Interface, on_delete=models.CASCADE)

    def __str__(self):
        return self.interface.name


class ClientServerInterface(models.Model):
    interface = models.OneToOneField(Interface, on_delete=models.CASCADE)

    def __str__(self):
        return self.interface.name


class Operation(models.Model):
    name = models.CharField(max_length=100, default='Operation')
    interface = models.ForeignKey(ClientServerInterface, on_delete=models.CASCADE)
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)

    def validate_unique(self, exclude=None):
        qs = Operation.objects.filter(name=self.name)
        if qs.filter(interface__package=self.interface.package).exclude(pk=self.pk).exists():
            raise ValidationError('Operation name must be unique per project')

    def __str__(self):
        return self.name


class Argument(models.Model):
    name = models.CharField(max_length=30, default='Arg')
    type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    direction = models.CharField(max_length=3, default='IN')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)

    class Meta:
        unique_together = (('name', 'type'),)

    def __str__(self):
        return self.name


class ApplicationError(models.Model):
    name = models.CharField(max_length=100, default='Operation')
    interface = models.ForeignKey(ClientServerInterface, on_delete=models.CASCADE)
    error_code = models.CharField(max_length=10, default='-1')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)

    def validate_unique(self, exclude=None):
        qs = ApplicationError.objects.filter(name=self.name)
        if qs.filter(interface__package=self.interface.package).exclude(pk=self.pk).exists():
            raise ValidationError('Application Error name must be unique per project')

    def __str__(self):
        return self.name


class PossibleError(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    application_error = models.ForeignKey(ApplicationError, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('operation', 'application_error'),)

    def __str__(self):
        return self.operation.name + ": " + self.application_error.name


class DataType(models.Model):
    type = models.CharField(max_length=10)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('type', 'package'),)

    def __str__(self):
        return self.type


class DataElement(models.Model):
    name = models.CharField(max_length=100, default='DataElement')
    uid = models.CharField(max_length=100, default=GetUUID, unique=True)
    interface = models.ForeignKey(SenderReceiverInterface, on_delete=models.CASCADE)
    type = models.ForeignKey(DataType, on_delete=models.CASCADE)

    def validate_unique(self, exclude=None):
        qs = DataElement.objects.filter(name=self.name)
        if qs.filter(interface__package=self.interface.package).exclude(pk=self.pk).exists():
            raise ValidationError('Data Element name must be unique per project')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(DataElement, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def  __lt__(self, other):
        return self.name < other.name
        

class DataElementRef(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE)
    data_element = models.ForeignKey(DataElement, on_delete=models.CASCADE)
    timeout = models.FloatField(default=60.0)

    class Meta:
        unique_together = (('port', 'data_element'),)

    def __str__(self):
        return self.port.name + ": " + self.data_element.name


class OperationRef(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.port.name + ": " + self.operation.name


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


class ServerCallPoint(models.Model):
    name = models.CharField(max_length=100, default='CallPoint', unique=True)
    operation_ref = models.ForeignKey(OperationRef, on_delete=models.CASCADE)
    runnable = models.ForeignKey(Runnable, on_delete=models.CASCADE)


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
    p_port = models.OneToOneField(Port, on_delete=models.CASCADE, related_name='p_port_connector')
    r_port = models.OneToOneField(Port, on_delete=models.CASCADE, related_name='r_port_connector')

    class Meta:
        unique_together = (('p_port', 'composition'),('r_port', 'composition'),)

    def __str__(self):
        return self.p_port.name + " - " + self.r_port.name
