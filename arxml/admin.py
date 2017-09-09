from django.contrib import admin

# Register your models here.

from .models import Package, SoftwareComponent, Interface, TimingEvent, Runnable, DataElement, DataType, DataAccess, DataElementRef, \
 Port, Composition, Connector, Operation, ClientServerInterface, SenderReceiverInterface, ApplicationError, Argument, PossibleError

class SoftwareComponentInline(admin.TabularInline):
    model = SoftwareComponent

class InterfaceInline(admin.TabularInline):
    model = Interface

class ClientServerInterfaceInline(admin.TabularInline):
    model = ClientServerInterface

class SenderReceiverInterfaceInline(admin.TabularInline):
    model = SenderReceiverInterface

class OperationInline(admin.TabularInline):
    model = Operation

class ApplicationErrorInline(admin.TabularInline):
    model = ApplicationError

class ArgumentInline(admin.TabularInline):
    model = Argument

class PossibleErrorInline(admin.TabularInline):
    model = PossibleError

class DataTypeInline(admin.TabularInline):
    model = DataType

class PackageAdmin(admin.ModelAdmin):
    model = Package
    inlines = (SoftwareComponentInline, InterfaceInline, DataTypeInline,)

class TimingEventInline(admin.TabularInline):
    model = TimingEvent

class RunnableInline(admin.TabularInline):
    model = Runnable

class SoftwareComponentAdmin(admin.ModelAdmin):
    model = SoftwareComponent
    inlines = (TimingEventInline, RunnableInline,)

class DataAccessInline(admin.TabularInline):
    model = DataAccess

class RunnableAdmin(admin.ModelAdmin):
    model = Runnable
    inlines = (DataAccessInline,)

class DataElementRefInline(admin.TabularInline):
    model = DataElementRef

class PortAdmin(admin.ModelAdmin):
    model = Port
    inlines = (DataElementRefInline,)

class ConnectorInline(admin.TabularInline):
    model = Connector

class CompositionAdmin(admin.ModelAdmin):
    model = Composition
    inlines = (ConnectorInline,)

class InterfaceAdmin(admin.ModelAdmin):
    model = Interface
    inlines = (ClientServerInterfaceInline, SenderReceiverInterfaceInline,)

class ClientServerInterfaceAdmin(admin.ModelAdmin):
    model = ClientServerInterface
    inlines = (OperationInline, ApplicationErrorInline,)

class SenderReceiverInterfaceAdmin(admin.ModelAdmin):
    model = SenderReceiverInterface
    inlines = (DataElement,)

class OperationAdmin(admin.ModelAdmin):
    model = Operation
    inlines = (ArgumentInline, PossibleErrorInline)


admin.site.register(Package, PackageAdmin)
admin.site.register(SoftwareComponent, SoftwareComponentAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(SenderReceiverInterfaceAdmin)
admin.site.register(ClientServerInterfaceAdmin)
admin.site.register(InterfaceAdmin)
admin.site.register(OperationAdmin)
admin.site.register(Argument)
admin.site.register(PossibleError)
admin.site.register(DataElement)
admin.site.register(DataElementRef)
admin.site.register(DataType)
admin.site.register(TimingEvent)
admin.site.register(Runnable, RunnableAdmin)
admin.site.register(DataAccess)
admin.site.register(Composition, CompositionAdmin)
admin.site.register(Connector)