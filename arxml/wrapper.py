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

data_type_typedef = {
    "Boolean": "boolean_T",
    "Float": "real_T",
    "SInt8": "int8_T",
    "UInt8": "uint8_T",
    "SInt16": "int16_T",
    "UInt16": "uint16_T",
    "SInt32": "int32_T",
    "UInt32": "uint32_T" }

class DataTypeHFile:
    def __init__(self, file, swc):
        file.truncate()

        print("/*", file=file)
        print("   Code generated by Autosar Studio for software Component:", file=file)
        print("   " + swc.name, file=file)
        print("*/", file=file)
        print("", file=file)
        print("#ifndef RTE_HEADER_Data_Type_h_", file=file)
        print("#define RTE_HEADER_Data_Type_h_", file=file)
        print("", file=file)
        print("#include \"rtetypes.h\"", file=file)
        print("", file=file)
        print("/*", file=file)
        print("   This file contains defintions for the DataTypes supported", file=file)
        print("   by the Software Component (" + swc.name + ")", file=file)
        print("*/", file=file)
        print("", file=file)

        for data_type in swc.datatype_set.all():
            print("typedef " + data_type_typedef[data_type.type] + " " + data_type.type, file=file)

        print("", file=file)
        print("#endif", file=file)

        file.close()

class RteHFile:
    def __init__(self, file, swc):
        file.truncate()

        print("/*", file=file)
        print("   Code generated by Autosar Studio for software Component:", file=file)
        print("   " + swc.name, file=file)
        print("*/", file=file)
        print("", file=file)
        print("#ifndef RTE_HEADER_" + swc.name + "_h_", file=file)
        print("#define RTE_HEADER_" + swc.name + "_h_", file=file)
        print("", file=file)
        print("#include \"datatypes.h\"", file=file)
        print("", file=file)
        print("/*", file=file)
        print("   This file contains prototypes for the runnables and data access points", file=file)
        print("   used by the Software Component (" + swc.name + ")", file=file)
        print("*/", file=file)
        print("", file=file)

        for runnable in swc.runnable_set.all():
            for access in runnable.dataaccess_set.all():
                if access.type == "DATA-READ-ACCESSS":
                    print(data_type_typedef[access.data_element_ref.data_element.type.type] + " " + "Rte_IRead_" + swc.name + "_" + runnable.name + "_" + access.data_element_ref.port.name + "_" + access.data_element_ref.data_element.name + "(void);", file=file)
                else:
                    print("void " + "Rte_IWrite_" + swc.name + "_" + runnable.name + "_" + access.data_element_ref.port.name + "_" + access.data_element_ref.data_element.name + "(" + data_type_typedef[access.data_element_ref.data_element.type.type] + "u);", file=file)
 
                print("", file=file)

        for runnable in swc.runnable_set.all():
            print("extern void " + runnable.name + "(void);", file=file)

        print("", file=file)
        print("#endif", file=file)

        file.close()

class RunnableCFile:
    def __init__(self, file, swc):
        include =  '#include \"' + swc.name + '_rte.h\"'

        print("/*", file=file)
        print("   Code generated by Autosar Studio for software Component:", file=file)
        print("   " + swc.name, file=file)
        print("", file=file)
        print("   This file should contain definitions for the runnables.", file=file)
        print("   Prototypes for the runnable functions and data access methods", file=file)
        print("", file=file)
        print("   Example:", file=file)
        print("   real_T Rte_IRead_swc_Runnable_Step_Port1_DataElement1();", file=file)
        print("", file=file)
        print("   extern void Runnable_Step(void);", file=file)
        print("", file=file)
        print("   Refer to" + swc.name + "_rte.h to find the current supported", file=file)
        print("   function headers", file=file)
        print("*/", file=file)
        print("", file=file)
        print(include, file=file)
        print("", file=file)
        print("/* WRITE YOUR CODE DOWN HERE */", file=file)
        print("", file=file)

        file.close()

class RunnableCompileFile:
    def __init__(self, file, runnable):
        print("", file=file)

        data_elements_set = set()
        input_data_elements = set()
        output_data_elements = set()

        for access in runnable.dataaccess_set.all():
            data_elements_set.add(access.data_element_ref.data_element.type + " " + access.data_element_ref.data_element.name + ";")

            if access.type == "DATA-READ-ACCESSS":
                input_data_elements.add(access.data_element_ref.data_element)
            else:
                output_data_elements.add(access.data_element_ref.data_element)

        for de in data_elements_set:
            print(de)

        print("", file=file)

        for access in runnable.dataaccess_set.all():
            if access.type == "DATA-READ-ACCESSS":
                print(access.data_element_ref.data_element.type + " " + "Rte_IRead_" + runnable.swc.name + "_" + runnable.name + "_" + access.data_element_ref.port.name + "_" + access.data_element_ref.data_element.name + "(void)", file=file)
                print("{", file=file)
                print("    return " + access.data_element_ref.data_element.name + ";", file=file)
                print("}", file=file)
            else:
                print("void " + "Rte_IWrite_" + runnable.swc.name + "_" + runnable.name + "_" + access.data_element_ref.port.name + "_" + access.data_element_ref.data_element.name + "(" + access.data_element_ref.data_element.type + "u)", file=file)
                print("{", file=file)
                print("    " + access.data_element_ref.data_element.name + " = u;", file=file)
                print("}", file=file)

            print("", file=file)

        print("int main()", file=file)
        print("{", file=file)

        for e in input_data_elements:
            print("    " + e.name + " = " + e.GetValue() + ";", file=file)

        print("", file=file)
        print("    " + runnable.name + "();", file=file)
        print("", file=file)

        print("    printf(\"{\")", file=file)

        for e in input_data_elements:
            name = r'\"e.name\"'
            s = r'\"%s\"'
            f = r'\"%f\"'
            d = r'\"%d\"'
            
            if e.type.name == "Boolean":
                print("    printf(\"" + name + "\": " + s + ",\", " + e.name + " ? \"True\" : \"False\")")
            elif e.type.name == "Float":
                print("    printf(\"" + name + "\": " + f + ",\", " + e.name + ")")
            else:
                print("    printf(\"" + name + "\": " + d + ",\", " + e.name + ")")

        print("    printf(\"}\")", file=file)

        print("}", file=file)

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

        package = ET.SubElement(packages, "AR-PACKAGE", UUID=swc.package.uid)
        ET.SubElement(package, "SHORT_NAME").text = swc.package.project.name
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=swc.package.subpackage_uid)
        ET.SubElement(package, "SHORT_NAME").text = swc.name + "_swc"

        elements = ET.SubElement(package, "ELEMENTS")
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
            if swc_port.interface is not None:
                interface_path = "/" + swc.name + "_pkg" + "/" + swc.name + "_swc/" + swc_port.interface.name

            # if type == "P-PORT-PROTOTYPE":
            req = ET.SubElement(port, "PROVIDED-COM-SPECS")
            spec = "UNQUEUED-PROVIDER-COM-SPEC"
            interface_t_ref = "PROVIDED-INTERFACE-TREF"

            if type == "R-PORT-PROTOTYPE":
                req = ET.SubElement(port, "REQUIRED-COM-SPECS")
                spec = "UNQUEUED-RECEIVER-COM-SPEC"
                interface_t_ref = "REQUIRED_INTERFACE-TREF"

            for data_element_ref in swc_port.dataelementref_set.all():
                    ref = ET.SubElement(req, spec)
                    ET.SubElement(ref, "DATA-ELEMENT-REF", DEST="DATA-ELEMENT-PROTOTYPE").text = "/" + swc.package.project.name + "/Interfaces/" + swc_port.interface.name + "/" + data_element_ref.data_element.name
                    ET.SubElement(ref, "ALIVE-TIMEOUT").text = str(data_element_ref.timeout)

            ET.SubElement(port, interface_t_ref, DEST="SENDER-RECEIVER-INTERFACE").text = interface_path
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

            ET.SubElement(timing_event, "START-ON-EVENT-REF", DEST="RUNNABLE-ENTITY").text =  "/" + swc.package.project.name + "/" + swc.name + "_swc/" + swc.name + "Behavior/" + event.runnable.name
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

                prototype_ref =  "/" + swc.package.project.name + "/" + swc.name + "_swc/" + swc.name + "/" + acc.data_element_ref.port.name
                data_element_ref =  "/" + swc.package.project.name + "/Interfaces/" + acc.data_element_ref.data_element.interface.name + "/" + acc.data_element_ref.data_element.name

                access_node = ET.SubElement(node, acc.type)
                ET.SubElement(access_node, "SHORT-NAME").text = acc.name

                data_element = ET.SubElement(access_node, "DATA-ELEMENT-IREF")

                ET.SubElement(data_element, acc.data_element_ref.port.type + "-REF", DEST=acc.data_element_ref.port.type).text = prototype_ref
                ET.SubElement(data_element, "DATA-ELEMENT-PROTOTYPE-REF", DEST="DATA-ELEMENT-PROTOTYPE-REF").text = data_element_ref

        ET.SubElement(behavior, "COMPONTENT-REF", DEST="APPLICATION-SOFTWARE-COMPONENT-TYPE").text = "/" + swc.package.project.name + "/" + swc.name + "_swc/" + swc.name
        ###

        ### Implementation
        impl = ET.SubElement(elements, "SWC-IMPLEMENTATION", uuid=swc.implementation_uid)
        ET.SubElement(impl, "SHORT-NAME").text = swc.name + "Implementation"

        self.AddAdminData(impl)

        ET.SubElement(impl, "BEHAVIOR-REF", DEST="INTERNAL-BEHAVIOR").text = "/" + swc.package.project.name + "/" + swc.name + "_swc/" + swc.name + "Behavior"
        ###
        
        self.root = root

class DataTypesAndInterfacesARXML(ArxmlWrapper):
    def __init__(self, package):
        ET.register_namespace("", autosar_schema_instance)
        root = ET.Element("AUTOSAR", { "xmlns":autosar_org, "xmlns:xsi":autosar_schema_instance, "xsi:schemaLocation":autosar_schema_location })

        admin_data = ET.SubElement(root, "ADMIN-DATA")

        sdgs = ET.SubElement(admin_data, "SDGS")
        sdg = ET.SubElement(sdgs, "SDG", GID="AutosarStudio::AutosarOptions")
        ET.SubElement(sdg, "SD", GID="GENDIR").text = directory

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE", UUID=package.uid)
        ET.SubElement(package, "SHORT_NAME").text = package.project.name
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=package.subpackage_uid)
        ET.SubElement(package, "SHORT_NAME").text = "DataTypes"

        elements = ET.SubElement(package, "ELEMENTS")

        ### DataTypes
        for datatype in package.datatype_set.all():
            if datatype.type == "Boolean":
                data_type = ET.SubElement(elements, "BOOLEAN-TYPE")
                ET.SubElement(data_type, "SHORT-NAME").text = datatype.type
            elif datatype.type == "Float":
                data_type = ET.SubElement(elements, "REAL-TYPE")
                ET.SubElement(data_type, "SHORT-NAME").text = datatype.type
                ET.SubElement(data_type, "SW-DATA-DEF-PROPS")
                ET.SubElement(data_type, "LOWER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } )
                ET.SubElement(data_type, "UPPER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } )
            else:
                data_type = ET.SubElement(elements, "INTEGER-TYPE")
                ET.SubElement(data_type, "SHORT-NAME").text = datatype.type
                ET.SubElement(data_type, "SW-DATA-DEF-PROPS")
                ET.SubElement(data_type, "LOWER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } ).text = integer_types[datatype.type]["lower"]
                ET.SubElement(data_type, "UPPER-LIMIT", { "INTERVAL-TYPE": "CLOSED" } ).text = integer_types[datatype.type]["upper"]
        ###

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=package.subpackage_uid)
        ET.SubElement(package, "SHORT_NAME").text = "Interfaces"

        elements = ET.SubElement(package, "ELEMENTS")

        ### Interfaces
        for pkg_interface in package.interface_set.all():
            interface = ET.SubElement(elements, "SENDER-RECEIVER-INTERFACE", UUID=pkg_interface.uid)

            ET.SubElement(interface, "SHORT-NAME").text = pkg_interface.name

            self.AddAdminData(interface)

            data_elements = ET.SubElement(interface, "DATA-ELEMENTS")

            for data_ele in pkg_interface.dataelement_set.all():
                data_element = ET.SubElement(interface, "DATA-ELEMENT-PROTOTYPE", UUID=data_ele.uid)

                ET.SubElement(data_element, "SHORT-NAME").text = data_ele.name

                self.AddAdminData(data_element)

                if data_ele.type.type == "Boolean":
                    ET.SubElement(data_element, "TYPE-TREF", DEST="BOOLEAN-TYPE").text = "/" + package.project.name + "/DataTypes/" + data_ele.type.type
                elif data_ele.type.type == "Float":
                    ET.SubElement(data_element, "TYPE-TREF", DEST="REAL-TYPE").text =  "/" + package.project.name + "/DataTypes/" + data_ele.type.type
                else:
                    ET.SubElement(data_element, "TYPE-TREF", DEST="INTEGER-TYPE").text =  "/" + package.project.name + "/DataTypes/" + data_ele.type.type
        ###


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
            ET.SubElement(component_prototype, "TYPE-TREF", DEST="APPLICATION-SOFTWARE-COMPONENT-TYPE").text =  "/" + swc.package.project.name + "/" + swc.name + "_swc/" + swc.name
        ###

        ### Connectors
        connectors = ET.SubElement(composition_type, "CONNECTORS")

        for connector in composition.connector_set.all():
            assembly_connector_prototype = ET.SubElement(connectors, "ASSEMBLY-CONNECTOR-PROTOTYPE", UUID=connector.uid)

            ET.SubElement(assembly_connector_prototype, "SHORT_NAME").text = connector.p_port.name + "Composition"

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