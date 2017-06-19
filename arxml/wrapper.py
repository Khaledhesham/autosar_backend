import xml.etree.ElementTree as ET
import uuid as guid
from django.core.files.base import ContentFile

autosar_org = "http://autosar.org/3.2.1"
autosar_schema_instance = "http://www.w3.org/2001/XMLSchema-instance"
autosar_schema_location = "http://autosar.org/3.2.1 autosar_3-2-1.xsd"

swc_type = "APPLICATION-SOFTWARE-COMPONENT-TYPE"

swc_path = "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/APPLICATION-SOFTWARE-COMPONENT-TYPE"
behavior_path = "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/INTERNAL-BEHAVIOR"

class Arxml:
    tree = ET.ElementTree
    directory = ''

    def __init__(self, s, directory):
        ET.register_namespace("", autosar_schema_instance)

        if s != '':
            self.tree = ET.ElementTree(ET.fromstring(s))

        self.directory = directory

    @staticmethod
    def Indent(elem, level=0):
        i = "\n" + level*"  "
        j = "\n" + (level-1)*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                Arxml.Indent(subelem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem

    def CreateDefaultARXML(self):
        ET.register_namespace("", autosar_schema_instance)
        root = ET.Element("AUTOSAR", { "xmlns":autosar_org, "xmlns:xsi":autosar_schema_instance, "xsi:schemaLocation":autosar_schema_location })

        admin_data = ET.SubElement(root, "ADMIN-DATA")

        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::AutosarOptions")
        ET.SubElement(sdg, "SD", GID="GENDIR").text = self.directory

        self.tree = ET.ElementTree(root)

    def AddAdminData(self, node):
        admin_data = ET.SubElement(node, "ADMIN-DATA")
        sdgs = ET.SubElement(admin_data, "SDGS")
        ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

    def CreateSoftwareComponent(self, name, pos_x, pos_y):
        self.CreateDefaultARXML()

        root = self.tree.getroot()

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE", UUID=str(guid.uuid1()))
        ET.SubElement(package, "SHORT_NAME").text = name + "_pkg"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=str(guid.uuid1()))
        ET.SubElement(package, "SHORT_NAME").text = name + "_swc"

        elements = ET.SubElement(package, "ELEMENTS")
        
        swc = ET.SubElement(elements, swc_type, UUID=str(guid.uuid1()), x=str(pos_x), y=str(pos_y))
        ET.SubElement(swc, "SHORT_NAME").text = name

        self.AddAdminData(swc)

        port = ET.SubElement(swc, "PORTS")

        behavior = ET.SubElement(elements, "INTERNAL-BEHAVIOR", UUID=str(guid.uuid1()))
        ET.SubElement(behavior, "SHORT-NAME").text = name + "Behavior"

        self.AddAdminData(behavior)

        ET.SubElement(behavior, "EVENTS")
        ET.SubElement(behavior, "RUNNABLES")

        ET.SubElement(behavior, "COMPONTENT-REF", DEST=swc_type).text = "/" + name + "_pkg/" + name + "_swc/" + name

        impl = ET.SubElement(elements, "SWC-IMPLEMENTATION", uuid = str(guid.uuid1()))
        ET.SubElement(impl, "SHORT-NAME").text = name + "Implementation"

        self.AddAdminData(impl)

        ET.SubElement(impl, "BEHAVIOR-REF", DEST="INTERNAL-BEHAVIOR").text = "/" + name + "_pkg/" + name + "_swc/" + name + "Behavior"

        uid = swc.get('UUID')
        
        return uid

    def AddTimingEvent(self, name, runnable, period, swc_name):
        root = self.tree.getroot()

        events = root.find(behavior_path + "/EVENTS")

        timing_event = ET.SubElement(events, "TIMING-EVENT", UUID=str(guid.uuid1()))
        ET.SubElement(timing_event, "SHORT-NAME").text = name

        self.AddAdminData(timing_event)

        ET.SubElement(timing_event, "START-ON-EVENT-REF", DEST="RUNNABLE-ENTITY").text =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "Behavior/" + runnable
        ET.SubElement(timing_event, "PERIOD").text = str(period)

        return timing_event.get('UUID')

    def AddRunnable(self, name, data_access, swc_name, concurrent):
        root = self.tree.getroot()

        runnables = root.find(behavior_path + "/RUNNABLES")

        runnable = ET.SubElement(runnables, "RUNNABLE-ENTITY", UUID=str(guid.uuid1()))
        ET.SubElement(runnable, "SHORT-NAME").text = name

        if concurrent:
            ET.SubElement(runnable, "CAN-BE-INVOKED-CONCURRENTLY").text = "true"
        else:
            ET.SubElement(runnable, "CAN-BE-INVOKED-CONCURRENTLY").text = "false"

        ET.SubElement(runnable, "SYMBOL").text = name

        data_read = ET.SubElement(runnable, "DATA-READ-ACCESSS")
        data_write = ET.SubElement(runnable, "DATA-WRITE-ACCESSS")

        for access in data_access:
            node = data_read
            access_type = "DATA-READ-ACCESSS"

            if access['type'] == "WRITE":
                node = data_write
                access_type = "DATA-WRITE-ACCESSS"
            
            access_node = ET.SubElement(node, access_type)
            ET.SubElement(access_node, "SHORT-NAME").text = ""

            data_element = ET.SubElement(access_node, "DATA-ELEMENT-IREF")

            if access["port"]["type"] == "R":
                ET.SubElement(data_element, "R-PORT-PROTOTYPE-REF", DEST="R-PORT-PROTOTYPE").text =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "/" + access["port"]["name"]
            else:
                ET.SubElement(data_element, "P-PORT-PROTOTYPE-REF", DEST="P-PORT-PROTOTYPE").text =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "/" + access["port"]["name"]
            
            ET.SubElement(data_element, "DATA-ELEMENT-PROTOTYPE-REF", DEST="DATA-ELEMENT-PROTOTYPE-REF").text =  "/" + swc_name + "_pkg/" + swc_name + "_if/" + access["data"]["interface"] + "/" + access["data"]["name"]

    #def AddDatatype(self, type):
        
    def AddPort(self, swc_uuid, port_type, name, interface):
        root = self.tree.getroot()

        for swc in root.findall(swc_path):
            if swc.get('UUID') == swc_uuid:
                port = ET.SubElement(swc, port_type, UUID=str(guid.uuid1()))
                ET.SubElement(port, "SHORT_NAME").text = name
                self.AddAdminData(port)
                ET.SubElement(port, "REQUIRED_INTERFACE-TREF", DEST=interface)
                self.tree = ET.ElementTree(root)

    def CreateComposition(self,name):
        self.CreateDefaultARXML()
        root = self.tree.getroot()

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE", UUID=str(guid.uuid1()))
        ET.SubElement(package, "SHORT_NAME").text = "CrossControl"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=str(guid.uuid1()))
        ET.SubElement(package, "SHORT_NAME").text = "SoftwareComponents"

        elements = ET.SubElement(package, "ELEMENTS")

        composition_type = ET.SubElement(elements, "COMPOSITION-TYPE")
        ET.SubElement(composition_type, "SHORT_NAME").text = name + "Composition"

        components = ET.SubElement(composition_type, "COMPONENTS")
        connectors = ET.SubElement(composition_type, "CONNECTORS")

    def __str__(self):
        indented = Arxml.Indent(self.tree.getroot())
        return ET.tostring(indented)