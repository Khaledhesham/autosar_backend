from rest_framework import serializers
from arxml.models import SoftwareComponent, TimingEvent, Port, Connector, Composition, DataAccess, DataElement, DataType, Interface, Runnable


class CompositionSerializer(serializers.HyperlinkedModelSerializer):
    components = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = ('components')

    def get_components(self, obj):
        items = []
        for item_component in obj.component_set.all():
            items.append(ComponentSerializer(instance=item_component).data)
        return items


class ComponentSerializer(serializers.HyperlinkedModelSerializer):
    serverId = serializers.SerializerMethodField()
    ports = serializers.SerializerMethodField()

    class Meta:
        model = SoftwareComponent
        fields = ('name', 'x', 'y', 'serverId', 'ports')

    def get_serverId(self,obj):
        return obj.id

    def get_ports(self, obj):
        items = []
        for item_port in obj.port_set.all():
            items.append(PortSerializer(instance=item_port).data)
        return items


class PortSerializer(serializers.HyperlinkedModelSerializer):
    portId = serializers.SerializerMethodField()

    class Meta:
        model = SoftwareComponent
        fields = ('name', 'x', 'y', 'type', 'portId')

    def get_portId(self,obj):
        return obj.id