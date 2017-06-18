import xml.etree.ElementTree as ET
import uuid as guid
from django.core.files.base import ContentFile

autosar_org = "http://autosar.org/3.2.1"
autosar_schema_instance = "http://www.w3.org/2001/XMLSchema-instance"
autosar_schema_location = "http://autosar.org/3.2.1 autosar_3-2-1.xsd"

swc_type = "APPLICATION-SOFTWARE-COMPONENT-TYPE"

swc_path = "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/APPLICATION-SOFTWARE-COMPONENT-TYPE"

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

    def CreateSoftwareComponent(self, name, pos_x, pos_y):
        self.CreateDefaultARXML()

        root = self.tree.getroot()

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")
        uid = str(guid.uuid1())
        package = ET.SubElement(packages, "AR-PACKAGE", uuid=uid)
        ET.SubElement(package, "SHORT_NAME").text = "name" + "_pkg"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        uid = str(guid.uuid1())
        package = ET.SubElement(sub, "AR-PACKAGE", uuid=uid)
        ET.SubElement(package, "SHORT_NAME").text = "name" + "_swc"

        elements = ET.SubElement(package, "ELEMENTS")
        
        uid = str(guid.uuid1())
        swc = ET.SubElement(elements, swc_type, uuid=uid, x=str(pos_x), y=str(pos_y))
        ET.SubElement(swc, "SHORT_NAME").text = name

        admin_data = ET.SubElement(swc, "ADMIN-DATA")
        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

        port = ET.SubElement(swc, "PORTS")

        uid = swc.get('uuid')
        
        return uid
    
    #def AddDatatype(self, type):
        
    def AddPort(self, swc_uuid, port_type, name, interface):
        root = self.tree.getroot()

        for swc in root.findall(swc_path):
            if swc.get('uuid') == swc_uuid:
                port = ET.SubElement(swc, port_type, uuid=str(guid.uuid1()))
                ET.SubElement(port, "SHORT_NAME").text = name

                admin_data = ET.SubElement(swc, "ADMIN-DATA")
                sdgs = ET.SubElement(admin_data, "SDGS")
                sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

                ET.SubElement(port, "REQUIRED_INTERFACE-TREF", dest=interface)
                self.tree = ET.ElementTree(root)

    def __str__(self):
        indented = Arxml.Indent(self.tree.getroot())
        return ET.tostring(indented)