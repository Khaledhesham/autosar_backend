import xml.etree.ElementTree as ET
import uuid as guid

autosar_org = "http://autosar.org/3.2.1"
autosar_schema_instance = "http://www.w3.org/2001/XMLSchema-instance"
autosar_schema_location = "http://autosar.org/3.2.1 autosar_3-2-1.xsd"

swc_type = "APPLICATION-SOFTWARE-COMPONENT-TYPE"

class arxml:
    tree = ET.ElementTree()

    def __init__(self, file):
        self.tree = ET.parse(file)

    def CreateDefaultARXML(name):
        root = ET.Element("AUTOSAR", { "xmlns":autosar_org, "xmlns:xsi":autosar_schema_instance, "xsi:schemaLocation":autosar_schema_location })

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")
        admin_data = ET.SubElement(root, "ADMIN-DATA")

        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::AutosarOptions")
        ET.SubElement(sdg, "SD", GID="GENDIR").text = name

        return ET.tostring(root, encoding='utf8', method='xml')

    def CreateArPackage(self):
        root = self.tree.getroot()
        package = ET.SubElement(root, "AR-PACKAGE", uuid=guid.uuid1())
        ET.SubElement(package, "SHORT_NAME").text = self.name + "Package"
        sub = ET.SubElement(package, "SUB-PACKAGES")
        return sub

    def CreateSoftwareComponent(self, name):
        sub = CreateArPackage(self)

        swc = ET.SubElement(sub, swc_type, uuid=sub.get('uuid'))
        ET.SubElement(swc, "SHORT_NAME").text = name

        admin_data = ET.SubElement(swc, "ADMIN-DATA")
        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

        port = ET.SubElement(swc, "PORTS")

    def AddPort(self, swc_uuid, port_type, name, interface):
        root = self.tree.getroot()

        for swc in root.findall(swc_type):
            if swc.get('uuid') == swc_uuid:
                port = ET.SubElement(swc, port_type, uuid=guid.uuid1())
                ET.SubElement(port, "SHORT_NAME").text = name

                admin_data = ET.SubElement(swc, "ADMIN-DATA")
                sdgs = ET.SubElement(admin_data, "SDGS")
                sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

                ET.SubElement(port, "REQUIRED_INTERFACE-TREF", dest=interface)

    def RemoveSoftwareComponent(self, uuid):
        root = self.tree.getroot()
        for arpkg in root.findall('AR-PACKAGE'):
            for swc in arpkg.findall(swc_type):
                if swc.get('uuid') == uuid:
                    root.remove(arpkg)

    def __str__(self):
        return ET.tostring(self.tree.getroot())