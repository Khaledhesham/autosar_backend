import xml.etree.ElementTree as ET
import uuid as guid
from files.models import File
from django.core.files.base import ContentFile

autosar_org = "http://autosar.org/3.2.1"
autosar_schema_instance = "http://www.w3.org/2001/XMLSchema-instance"
autosar_schema_location = "http://autosar.org/3.2.1 autosar_3-2-1.xsd"

swc_type = "APPLICATION-SOFTWARE-COMPONENT-TYPE"

class Arxml:
    file = File
    tree = ET.ElementTree

    def __init__(self, file):
        ET.register_namespace("", autosar_schema_instance)
        self.tree = ET.ElementTree(ET.fromstring(file.Read()))
        self.file = file

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

    @staticmethod
    def CreateDefaultARXML(directory):
        ET.register_namespace("", autosar_schema_instance)
        root = ET.Element("AUTOSAR", { "xmlns":autosar_org, "xmlns:xsi":autosar_schema_instance, "xsi:schemaLocation":autosar_schema_location })

        admin_data = ET.SubElement(root, "ADMIN-DATA")

        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::AutosarOptions")
        ET.SubElement(sdg, "SD", GID="GENDIR").text = directory

        indented = Arxml.Indent(root)
        return ET.tostring(indented)

    def CreateArPackage(self):
        root = self.tree.getroot()
        packages = root.find("TOP-LEVEL-PACKAGES")
        if packages is None:
            packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")
        uid = str(guid.uuid1())
        package = ET.SubElement(packages, "AR-PACKAGE", uuid=uid)
        ET.SubElement(package, "SHORT_NAME").text = "Package"
        sub = ET.SubElement(package, "SUB-PACKAGES")
        self.tree = ET.ElementTree(root)
        return uid

    def CreateSoftwareComponent(self, name, pos_x, pos_y):
        uid = self.CreateArPackage()
        root = self.tree.getroot()

        packages = root.find("TOP-LEVEL-PACKAGES")
        for package in packages.findall("AR-PACKAGE"):
            if str(package.get("uuid")) == uid:
                sub = package.find("SUB-PACKAGES")
                swc = ET.SubElement(sub, swc_type, uuid=str(package.get('uuid')), x=str(pos_x), y=str(pos_y))
                ET.SubElement(swc, "SHORT_NAME").text = name

                admin_data = ET.SubElement(swc, "ADMIN-DATA")
                sdgs = ET.SubElement(admin_data, "SDGS")
                sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

                port = ET.SubElement(swc, "PORTS")
                self.tree = ET.ElementTree(root)
                return swc.get('uuid')
        return False

    def AddPort(self, swc_uuid, port_type, name, interface):
        root = self.tree.getroot()

        for swc in root.findall(swc_type):
            if swc.get('uuid') == swc_uuid:
                port = ET.SubElement(swc, port_type, uuid=str(guid.uuid1()))
                ET.SubElement(port, "SHORT_NAME").text = name

                admin_data = ET.SubElement(swc, "ADMIN-DATA")
                sdgs = ET.SubElement(admin_data, "SDGS")
                sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

                ET.SubElement(port, "REQUIRED_INTERFACE-TREF", dest=interface)
                self.tree = ET.ElementTree(root)

    def Save(self):
        indented = Arxml.Indent(self.tree.getroot())
        s = ET.tostring(indented)
        self.file.Write(s)

    def RemoveSoftwareComponent(self, uuid):
        root = self.tree.getroot()
        for arpkg in root.findall('AR-PACKAGE'):
            for swc in arpkg.findall(swc_type):
                if swc.get('uuid') == uuid:
                    root.remove(arpkg)

    def __str__(self):
        indented = Arxml.Indent(self.tree.getroot())
        return ET.tostring(indented)