import xml.etree.ElementTree as ET
import uuid as guid

autosar_org = "http://autosar.org/3.2.1"
autosar_schema_instance = "http://www.w3.org/2001/XMLSchema-instance"
autosar_schema_location = "http://autosar.org/3.2.1 autosar_3-2-1.xsd"

swc_path = "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/APPLICATION-SOFTWARE-COMPONENT-TYPE"
behavior_path = "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/INTERNAL-BEHAVIOR"

integer_types = {
    "SInt8": { "lower": "-128", "upper": "127" },
    "UInt8": { "lower": "0", "upper": "255" },
    "SInt16": { "lower": "-32768", "upper": "32767" },
    "UInt16": { "lower": "0", "upper": "65535" },
    "SInt32": { "lower": "-2147483648", "upper": "2147483647" },
    "UInt32": { "lower": "0", "upper": "4294967295" } }

class ArxmlWrapper:
    root = ET.Element

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
                ArxmlWrapper.Indent(subelem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem

    def AddAdminData(self, node):
        admin_data = ET.SubElement(node, "ADMIN-DATA")
        sdgs = ET.SubElement(admin_data, "SDGS")
        ET.SubElement(sdgs, "SDG", GID="AutosarStudio::IdentifiableOptions")

    def __str__(self):
        ArxmlWrapper.Indent(self.root)
        return ET.tostring(self.root).decode("utf-8")

class SoftwareComponentARXML(ArxmlWrapper):
    def __init__(self, swc, directory):
        ### Basic ARXML
        ET.register_namespace("", autosar_schema_instance)
        root = ET.Element("AUTOSAR", { "xmlns":autosar_org, "xmlns:xsi":autosar_schema_instance, "xsi:schemaLocation":autosar_schema_location })

        admin_data = ET.SubElement(root, "ADMIN-DATA")

        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::AutosarOptions")
        ET.SubElement(sdg, "SD", GID="GENDIR").text = directory

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE", UUID=swc.package_uid)
        ET.SubElement(package, "SHORT_NAME").text = swc.name + "_pkg"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=swc.subpackage_uid)
        ET.SubElement(package, "SHORT_NAME").text = swc.name + "_swc"

        elements = ET.SubElement(package, "ELEMENTS")
        ###

        ### DataTypes
        for datatype in swc.datatype_set.all():
            if datatype.type == "Boolean":
                data_type = ET.SubElement(elements, "BOOLEAN-TYPE")
                ET.SubElement(data_type, "SHORT-NAME").text = type
            elif datatype.type == "Float":
                data_type = ET.SubElement(elements, "REAL-TYPE")
                ET.SubElement(data_type, "SHORT-NAME").text = type
                ET.SubElement(data_type, "SW-DATA-DEF-PROPS")
                ET.SubElement(data_type, "LOWER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } )
                ET.SubElement(data_type, "UPPER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } )
            else:
                data_type = ET.SubElement(elements, "INTEGER-TYPE")
                ET.SubElement(data_type, "SHORT-NAME").text = type
                ET.SubElement(data_type, "SW-DATA-DEF-PROPS")
                ET.SubElement(data_type, "LOWER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } ).text = integer_types[type]["lower"]
                ET.SubElement(data_type, "UPPER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } ).text = integer_types[type]["upper"]
        ###

        ### Software Component
        swc_element = ET.SubElement(elements, "APPLICATION-SOFTWARE-COMPONENT-TYPE", UUID=swc.uid)
        ET.SubElement(swc_element, "SHORT_NAME").text = swc.name

        self.AddAdminData(swc_element)
        ###

        ### Ports
        ports = ET.SubElement(swc_element, "PORTS")

        for swc_port in swc.port_set.all():
            port = ET.SubElement(ports, swc_port.type, UUID=swc_port.uid)
            ET.SubElement(port, "SHORT_NAME").text = swc_port.name

            self.AddAdminData(port)

            interface_path = ""
            if port.interface is not None:
                interface_path = "/" + swc.name + "_pkg" + "/" + swc.name + "_swc/" + port.interface.name

            if type == "R-PORT-PROTOTYPE":
                ET.SubElement(port, "REQUIRED_INTERFACE-TREF", DEST="SENDER-RECEIVER-INTERFACE").text = interface_path
            else:
                ET.SubElement(port, "PROVIDED-INTERFACE-TREF", DEST="SENDER-RECEIVER-INTERFACE").text = interface_path
        ###

        ### Behavior
        behavior = ET.SubElement(elements, "INTERNAL-BEHAVIOR", UUID=swc.behavior_uid)
        ET.SubElement(behavior, "SHORT-NAME").text = swc.name + "Behavior"

        self.AddAdminData(behavior)

        events = ET.SubElement(behavior, "EVENTS")

        for event in swc.timingevent_set.all():
            timing_event = ET.SubElement(events, "TIMING-EVENT", UUID=event.uid)
            ET.SubElement(timing_event, "SHORT-NAME").text = event.name

            self.AddAdminData(timing_event)

            ET.SubElement(timing_event, "START-ON-EVENT-REF", DEST="RUNNABLE-ENTITY").text =  "/" + swc.name + "_pkg/" + swc.name + "_swc/" + swc.name + "Behavior/" + event.runnable.name
            ET.SubElement(timing_event, "PERIOD").text = str(event.period)

        runnables = ET.SubElement(behavior, "RUNNABLES")

        for runnable in swc.runnable_set.all():
            run = ET.SubElement(runnables, "RUNNABLE-ENTITY", UUID=runnable.uid)
            ET.SubElement(run, "SHORT-NAME").text = runnable.name

            if runnable.concurrent:
                ET.SubElement(run, "CAN-BE-INVOKED-CONCURRENTLY").text = "true"
            else:
                ET.SubElement(run, "CAN-BE-INVOKED-CONCURRENTLY").text = "false"

            ET.SubElement(run, "SYMBOL").text = runnable.name

            data_read = ET.SubElement(run, "DATA-READ-ACCESSS")
            data_write = ET.SubElement(run, "DATA-WRITE-ACCESSS")

            for acc in runnable.dataaccess_set.all():
                if acc.type == "DATA-WRITE-ACCESSS":
                    node = data_write
                else:
                    node = data_read

                prototype_ref =  "/" + swc.name + "_pkg/" + swc.name + "_swc/" + swc.name + "/" + acc.port.name
                data_element_ref =  "/" + swc.name + "_pkg/" + swc.name + "_swc/" + acc.data_element.interface.name + "/" + acc.data_element.name

                access_node = ET.SubElement(node, acc.type)
                ET.SubElement(access_node, "SHORT-NAME").text = acc.name

                data_element = ET.SubElement(access_node, "DATA-ELEMENT-IREF")

                ET.SubElement(data_element, acc.port.type + "-REF", DEST=acc.port.type).text = prototype_ref
                ET.SubElement(data_element, "DATA-ELEMENT-PROTOTYPE-REF", DEST="DATA-ELEMENT-PROTOTYPE-REF").text = data_element_ref

        ET.SubElement(behavior, "COMPONTENT-REF", DEST="APPLICATION-SOFTWARE-COMPONENT-TYPE").text = "/" + swc.name + "_pkg/" + swc.name + "_swc/" + swc.name
        ###

        ### Implementation
        impl = ET.SubElement(elements, "SWC-IMPLEMENTATION", uuid=swc.implementation_uid)
        ET.SubElement(impl, "SHORT-NAME").text = swc.name + "Implementation"

        self.AddAdminData(impl)

        ET.SubElement(impl, "BEHAVIOR-REF", DEST="INTERNAL-BEHAVIOR").text = "/" + swc.name + "_pkg/" + swc.name + "_swc/" + swc.name + "Behavior"
        ###

        ### Interfaces
        for swc_interface in swc.interface_set.all():
            interface = ET.SubElement(elements, "SENDER-RECEIVER-INTERFACE", UUID=swc_interface.uid)

            ET.SubElement(interface, "SHORT-NAME").text = swc_interface.name

            self.AddAdminData(interface)

            data_elements = ET.SubElement(interface, "DATA-ELEMENTS")

            for data_ele in swc_interface.dataelement_set.all():
                data_element = ET.SubElement(interface, "DATA-ELEMENT-PROTOTYPE", UUID=data_ele.uid)

                ET.SubElement(data_element, "SHORT-NAME").text = data_ele.name

                self.AddAdminData(data_element)

                if data_ele.type.name == "Boolean":
                    ET.SubElement(data_element, "TYPE-TREF", DEST="BOOLEAN-TYPE").text = "/" + swc.name + "_pkg/" + swc.name + "_swc/" + data_ele.type.name
                elif data_ele.type.name == "Float":
                    ET.SubElement(data_element, "TYPE-TREF", DEST="REAL-TYPE").text =  "/" + swc.name + "_pkg/" + swc.name + "_swc/" + data_ele.type.name
                else:
                    ET.SubElement(data_element, "TYPE-TREF", DEST="INTEGER-TYPE").text =  "/" + swc.name + "_pkg/" + swc.name + "_swc/" + data_ele.type.name
        ###
        
        self.root = root

class CompositionARXML(ArxmlWrapper):
    def __init__(self, composition):
        ### Basic ARXML
        ET.register_namespace("", autosar_schema_instance)
        root = ET.Element("AUTOSAR", { "xmlns":autosar_org, "xmlns:xsi":autosar_schema_instance, "xsi:schemaLocation":autosar_schema_location })

        admin_data = ET.SubElement(root, "ADMIN-DATA")

        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::AutosarOptions")
        ET.SubElement(sdg, "SD", GID="GENDIR").text = composition.project.directory.GetPath()
        ###

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE")
        ET.SubElement(package, "SHORT_NAME").text = "CrossControl"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE")
        ET.SubElement(package, "SHORT_NAME").text = "SoftwareComponents"

        elements = ET.SubElement(package, "ELEMENTS")

        composition_type = ET.SubElement(elements, "COMPOSITION-TYPE")

        ET.SubElement(composition_type, "SHORT_NAME").text = composition.project.name + "Composition"

        ### Components
        components = ET.SubElement(composition_type, "COMPONENTS")

        for swc in composition.softwarecomponent_set.all():
            component_prototype = ET.SubElement(components, "COMPONENT-PROTOTYPE")
            ET.SubElement(component_prototype, "SHORT_NAME").text = swc.name
            ET.SubElement(component_prototype, "TYPE-TREF", DEST="APPLICATION-SOFTWARE-COMPONENT-TYPE").text =  "/" + swc.name + "_pkg/" + swc.name + "_swc/" + swc.name
        ###

        ### Connectors
        connectors = ET.SubElement(composition_type, "CONNECTORS")

        for connector in composition.connector_set.all():
            assembly_connector_prototype = ET.SubElement(connectors, "ASSEMBLY-CONNECTOR-PROTOTYPE", UUID=connector.uid)

            ET.SubElement(assembly_connector_prototype, "SHORT_NAME").text = connectpr.p_port.name + "Composition"

            p_component_path =  "/" + connector.p_port.swc.name + "_pkg/" + connector.p_port.swc.name + "_swc/" + connector.p_port.swc.name
            r_component_path =  "/" + connector.r_port.swc.name + "_pkg/" + connector.r_port.swc.name + "_swc/" + connector.r_port.swc.name

            provider_iref = ET.SubElement(assembly_connector_prototype, "PROVIDER-IREF")
            ET.SubElement(provider_iref, "COMPONENT-PROTOTYPE-REF", DEST="COMPONENT-PROTOTYPE").text = "/CrossControl/SoftwareComponents/" + composition.project.name + "Composition" + "/" + connector.p_port.swc.name
            ET.SubElement(provider_iref, "P-PORT-PROTOTYPE-REF", DEST="P-PORT-PROTOTYPE").text = p_component_path + "/" + connector.p_port.name

            requester_iref = ET.SubElement(assembly_connector_prototype, "REQUESTER-IREF")
            ET.SubElement(requester_iref, "COMPONENT-PROTOTYPE-REF", DEST="COMPONENT-PROTOTYPE").text = "/CrossControl/SoftwareComponents/" + composition.project.name + "Composition" + "/" + connector.r_port.swc.name
            ET.SubElement(requester_iref, "R-PORT-PROTOTYPE-REF", DEST="R-PORT-PROTOTYPE").text = r_component_path + "/" + connector.r_port.name
        ###
        
        self.root = root