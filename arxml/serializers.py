from rest_framework import serializers
from arxml.models import SoftwareComponent, TimingEvent, Port, Composition, DataAccess, DataElement, DataType, Interface, Runnable, DataElementRef


class CompositionSerializer(serializers.HyperlinkedModelSerializer):
    components = serializers.SerializerMethodField()
    connectors = serializers.SerializerMethodField()
    interfaces = serializers.SerializerMethodField()
    datatypes = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = ('components', 'connectors', 'interfaces', 'datatypes')

    def get_components(self, obj):
        items = []
        for item_component in obj.softwarecomponent_set.all():
            items.append(ComponentSerializer(instance=item_component).data)
        return items

    def get_interfaces(self, obj):
        items = []
        for item_interface in obj.project.package.interface_set.all():
            items.append(InterfaceSerializer(instance=item_interface).data)
        return items

    def get_datatypes(self, obj):
        items = []
        for item_datatype in obj.project.package.datatype_set.all():
            items.append(DataTypeserializer(instance=item_datatype).data)
        return items

    def get_connectors(self, obj):
        items = []
        for item_connector in obj.connector_set.all():
            conn = []
            first_port = {}
            second_port = {}
            wire = {}
            for index, item in enumerate(Port.objects.filter(swc=item_connector.p_port.swc)):
                if item == item_connector.p_port:
                    p_port_index = index
            for index, item in enumerate(SoftwareComponent.objects.filter(composition=item_connector.p_port.swc.composition)):
                if item == item_connector.p_port.swc:
                    p_port_component_index = index
            for index, item in enumerate(Port.objects.filter(swc=item_connector.r_port.swc)):
                if item == item_connector.r_port:
                    r_port_index = index
            for index, item in enumerate(SoftwareComponent.objects.filter(composition=item_connector.r_port.swc.composition)):
                if item == item_connector.r_port.swc:
                    r_port_component_index = index
            first_port['pathIndex'] = p_port_component_index
            first_port['portIndex'] = p_port_index
            second_port['pathIndex'] = r_port_component_index
            second_port['portIndex'] = r_port_index
            wire['wireId'] = item_connector.id
            conn.append(first_port)
            conn.append(second_port)
            conn.append(wire)
            items.append(conn)
        return items


class ComponentSerializer(serializers.HyperlinkedModelSerializer):
    serverId = serializers.SerializerMethodField()
    Ports = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    noOfPorts = serializers.SerializerMethodField()
    TimedEvents = serializers.SerializerMethodField()
    Runnables = serializers.SerializerMethodField()

    class Meta:
        model = SoftwareComponent
        fields = ('name', 'x', 'y', 'serverId', 'id', 'noOfPorts','Ports','TimedEvents','Runnables')

    def get_id(self,obj):
        for index, item in enumerate(SoftwareComponent.objects.filter(composition=obj.composition)):
            if item == obj:
                return index

    def get_noOfPorts(self,obj):
        return Port.objects.filter(swc=obj).count()

    def get_serverId(self,obj):
        return obj.id

    def get_Ports(self, obj):
        items = []
        for item_port in obj.port_set.all():
            items.append(PortSerializer(instance=item_port).data)
        return items

    def get_TimedEvents(self,obj):
        items = []
        for item_timedEvent in TimingEvent.objects.filter(swc=obj):
            items.append(TimedEventSerializer(instance=item_timedEvent).data)
        return items

    def get_Runnables(self,obj):
        items = []
        for item_runnable in Runnable.objects.filter(swc=obj):
            items.append(RunnableSerializer(instance=item_runnable).data)
        return items


class PortSerializer(serializers.HyperlinkedModelSerializer):
    portId = serializers.SerializerMethodField()
    portServerId = serializers.SerializerMethodField()
    portName = serializers.SerializerMethodField()
    portType = serializers.SerializerMethodField()
    selectedInterface = serializers.SerializerMethodField()
    dataElements = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ('portName', 'x', 'y', 'portType', 'portServerId','portId', 'selectedInterface', 'dataElements')

    def get_portId(self,obj):
        for index, item in enumerate(Port.objects.filter(swc=obj.swc)):
            if item == obj:
                return index

    def get_portServerId(self,obj):
        return obj.id

    def get_portName(self,obj):
        return obj.name

    def get_portType(self,obj):
        return obj.type

    def get_dataElements(self,obj):
        items = []
        for item_dataelementref in DataElementRef.objects.filter(port=obj):
            items.append(DataElementRefSerializer(instance=item_dataelementref).data)
        return items

    def get_selectedInterface(self,obj):
        if obj.interface is not None:
            for index, item in enumerate(Interface.objects.filter(package=obj.swc.package)):
                if item == obj.interface:
                    return index
        else:
            return -1

class DataTypeserializer(serializers.HyperlinkedModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = DataType
        fields = ('value', 'id')

    def get_value(self,obj):
        return obj.type


class InterfaceSerializer(serializers.HyperlinkedModelSerializer):
    dataElements = serializers.SerializerMethodField()
    interfaceId = serializers.SerializerMethodField()
    interfaceName = serializers.SerializerMethodField()

    class Meta:
        model = Interface
        fields = ('interfaceId','interfaceName','dataElements')

    def get_interfaceId(self,obj):
        return obj.id

    def get_interfaceName(self,obj):
        return obj.name

    def get_dataElements(self,obj):
        items = []
        for item_dataelement in DataElement.objects.filter(interface=obj.senderreceiverinterface):
            items.append(dataElementSerializer(instance=item_dataelement).data)
        return items


class dataElementSerializer(serializers.HyperlinkedModelSerializer):
    dataElementId = serializers.SerializerMethodField()
    dataElementName = serializers.SerializerMethodField()
    dataElementType = serializers.SerializerMethodField()

    class Meta:
        model = DataElement
        fields = ('dataElementId', 'dataElementName', 'dataElementType')

    def get_dataElementId(self, obj):
        return obj.id

    def get_dataElementName(self, obj):
        return obj.name

    def get_dataElementType(self,obj):
        return obj.type.type


class TimedEventSerializer(serializers.HyperlinkedModelSerializer):
    TimedEventId = serializers.SerializerMethodField()
    TimedEventName = serializers.SerializerMethodField()
    Period = serializers.SerializerMethodField()
    runnableId = serializers.SerializerMethodField()

    class Meta:
        model = TimingEvent
        fields =('TimedEventId','TimedEventName','Period', 'runnableId')

    def get_TimedEventId(self,obj):
        return obj.id

    def get_TimedEventName(self,obj):
        return obj.name

    def get_Period(self,obj):
        return obj.period

    def get_runnableId(self,obj):
        return obj.runnable.id


class RunnableSerializer(serializers.HyperlinkedModelSerializer):
    runnableName = serializers.SerializerMethodField()
    runnableId = serializers.SerializerMethodField()
    dataAccess = serializers.SerializerMethodField()

    class Meta:
        model = Runnable
        fields =('runnableName','runnableId', 'concurrent', 'dataAccess')

    def get_runnableName(self,obj):
        return obj.name

    def get_runnableId(self,obj):
        return obj.id

    def get_dataAccess(self, obj):
        items = []
        for item_dataAccess in DataAccess.objects.filter(runnable=obj):
            items.append(DataAccessSerializer(instance=item_dataAccess).data)
        return items


class DataAccessSerializer(serializers.HyperlinkedModelSerializer):
    dataAccessId = serializers.SerializerMethodField()
    dataAccessName = serializers.SerializerMethodField()
    portId = serializers.SerializerMethodField()
    dataElementId = serializers.SerializerMethodField()

    class Meta:
        model = DataAccess
        fields =('dataAccessId','dataAccessName', 'portId', 'dataElementId')

    def get_dataAccessId(self,obj):
        return obj.id

    def get_dataAccessName(self,obj):
        return obj.name

    def get_portId(self,obj):
        return obj.data_element_ref.port.id

    def get_dataElementId(self,obj):
        return obj.data_element_ref.data_element.id


class DataElementRefSerializer(serializers.HyperlinkedModelSerializer):
    dataElementName = serializers.SerializerMethodField()
    element_ref_id = serializers.SerializerMethodField()

    class Meta:
        model = DataElementRef
        fields =('dataElementName','element_ref_id')

    def get_dataElementName(self,obj):
        return obj.data_element.name

    def get_element_ref_id(self,obj):
        return obj.id