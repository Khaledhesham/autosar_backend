from django.contrib import admin

# Register your models here.

from .models import Package, SoftwareComponent, Interface, TimingEvent, Runnable, DataElement, DataType, DataAccess, DataElementRef, \
 Port, Composition, Connector

class SoftwareComponentInline(admin.TabularInline):
    model = SoftwareComponent

class InterfaceInline(admin.TabularInline):
    model = Interface

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


admin.site.register(Package, PackageAdmin)
admin.site.register(SoftwareComponent, SoftwareComponentAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(Interface)
admin.site.register(DataElement)
admin.site.register(DataElementRef)
admin.site.register(DataType)
admin.site.register(TimingEvent)
admin.site.register(Runnable, RunnableAdmin)
admin.site.register(DataAccess)
admin.site.register(Composition, CompositionAdmin)
admin.site.register(Connector)