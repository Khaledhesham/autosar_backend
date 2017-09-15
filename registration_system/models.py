from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from files.models import File, Project, Directory
from arxml.models import Package, Composition, SoftwareComponent, TimingEvent, Runnable, Port, SenderReceiverInterface, Interface, DataElement, DataAccess, DataElementRef, DataType

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# Create your models here.

def MakeProject(project_name, req_user):
    project = Project(name=project_name, user=req_user)
    project.save()
    directory_name = project_name + str("-") + str(project.id)
    main_directory = Directory(name=directory_name, project=project)
    main_directory.save()
    arxml_file = File(name="Composition", file_type="arxml", directory=main_directory)
    arxml_file.save()
    interfaces_file = File(name="DataTypesAndInterfaces", file_type="arxml", directory=main_directory)
    interfaces_file.save()
    package = Package(project=project, interfaces_file=interfaces_file)
    package.save()
    package.Rewrite()
    composition = Composition(file=arxml_file, project=project)
    composition.save()
    composition.Rewrite()
    return project

def CreateDefaultsForUser(user):
    ### Blink
    project = MakeProject("Blinker", user)
    swc = SoftwareComponent.Make(project, "Blinker", 33.4, 40.57)
    runnable = Runnable(name="BlinkerRunnable", concurrent=True, swc=swc)
    runnable.save()
    event = TimingEvent(name="TimingEvent", runnable=runnable, period=1, swc=swc)
    event.save()
    interface = Interface(name="Blink", package=project.package, type="SENDER-RECEIVER-INTERFACE")
    interface.save()
    blinker_interface = SenderReceiverInterface(interface=interface)
    blinker_interface.save()
    led_port = Port(name="Led", swc=swc, type="P-PORT-PROTOTYPE", interface=interface, x=18.5, y=2.4)
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
    project.composition.Rewrite()
    swc.runnables_file.Write(open("files/default-projects/Blinker/Blinker/Blinker_runnables.c").read())

    ###
