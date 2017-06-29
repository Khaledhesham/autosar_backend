from rest_framework import serializers
from arxml.models import SoftwareComponent, TimingEvent, Port, Connector, Composition, DataAccess, DataElement, DataType, Interface, Runnable


class CompositionSerializer(serializers.HyperlinkedModelSerializer):
    components = serializers.SerializerMethodField()
    connectors = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = ('components','connectors')

    def get_components(self, obj):
        items = []
        for item_component in obj.softwarecomponent_set.all():
            items.append(ComponentSerializer(instance=item_component).data)
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

    class Meta:
        model = SoftwareComponent
        fields = ('name', 'x', 'y', 'serverId', 'Ports', 'id', 'noOfPorts')

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


class PortSerializer(serializers.HyperlinkedModelSerializer):
    portId = serializers.SerializerMethodField()
    portServerId = serializers.SerializerMethodField()
    portName = serializers.SerializerMethodField()
    portType = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ('portName', 'x', 'y', 'portType', 'portServerId','portId')

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
