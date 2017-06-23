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

class Arxml:
    tree = ET.ElementTree
    directory = ''
    build = False

    def __init__(self, s, directory):

        if s != '':
            s = s.replace(' xmlns="http://autosar.org/3.2.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/3.2.1 autosar_3-2-1.xsd"',"")
            self.tree = ET.ElementTree(ET.fromstring(s))
        else:
            self.build = True
            ET.register_namespace("", autosar_schema_instance)

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

    def Remove(self, parent_path, child_type, child_uid):
        root = self.tree.getroot()

        parent = root.find(parent_path)

        for child in parent.findall(child_type):
            if child.get('UUID') == child_uid:
                parent.remove(child)
                return True

        return False

    def CreateSoftwareComponent(self, name):
        self.CreateDefaultARXML()

        root = self.tree.getroot()

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE", UUID=str(guid.uuid1()))
        ET.SubElement(package, "SHORT_NAME").text = name + "_pkg"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE", UUID=str(guid.uuid1()))
        ET.SubElement(package, "SHORT_NAME").text = name + "_swc"

        elements = ET.SubElement(package, "ELEMENTS")
        
        swc = ET.SubElement(elements, "APPLICATION-SOFTWARE-COMPONENT-TYPE", UUID=str(guid.uuid1()))
        ET.SubElement(swc, "SHORT_NAME").text = name

        self.AddAdminData(swc)

        port = ET.SubElement(swc, "PORTS")

        behavior = ET.SubElement(elements, "INTERNAL-BEHAVIOR", UUID=str(guid.uuid1()))
        ET.SubElement(behavior, "SHORT-NAME").text = name + "Behavior"

        self.AddAdminData(behavior)

        ET.SubElement(behavior, "EVENTS")
        ET.SubElement(behavior, "RUNNABLES")

        ET.SubElement(behavior, "COMPONTENT-REF", DEST="APPLICATION-SOFTWARE-COMPONENT-TYPE").text = "/" + name + "_pkg/" + name + "_swc/" + name

        impl = ET.SubElement(elements, "SWC-IMPLEMENTATION", uuid = str(guid.uuid1()))
        ET.SubElement(impl, "SHORT-NAME").text = name + "Implementation"

        self.AddAdminData(impl)

        ET.SubElement(impl, "BEHAVIOR-REF", DEST="INTERNAL-BEHAVIOR").text = "/" + name + "_pkg/" + name + "_swc/" + name + "Behavior"
        
        return swc.get('UUID')

    def AddTimingEvent(self, name, runnable_name, period, swc_name):
        root = self.tree.getroot()

        events = root.find(behavior_path + "/EVENTS")

        for event in list(events):
            if event.find("SHORT-NAME").text == name:
                return ''

        timing_event = ET.SubElement(events, "TIMING-EVENT", UUID=str(guid.uuid1()))
        ET.SubElement(timing_event, "SHORT-NAME").text = name

        self.AddAdminData(timing_event)

        ET.SubElement(timing_event, "START-ON-EVENT-REF", DEST="RUNNABLE-ENTITY").text =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "Behavior/" + runnable_name
        ET.SubElement(timing_event, "PERIOD").text = str(period)

        return timing_event.get('UUID')

    def RemoveTimingEvent(self, event_uid):
        return self.Remove(behavior_path + "/EVENTS", "TIMING-EVENT", event_uid)

    def AddRunnable(self, name, concurrent):
        root = self.tree.getroot()

        runnables = root.find(behavior_path + "/RUNNABLES")

        for runnable in list(runnables):
            if runnable.find("SHORT-NAME").text == name:
                return ''

        runnable = ET.SubElement(runnables, "RUNNABLE-ENTITY", UUID=str(guid.uuid1()))
        ET.SubElement(runnable, "SHORT-NAME").text = name

        if concurrent:
            ET.SubElement(runnable, "CAN-BE-INVOKED-CONCURRENTLY").text = "true"
        else:
            ET.SubElement(runnable, "CAN-BE-INVOKED-CONCURRENTLY").text = "false"

        ET.SubElement(runnable, "SYMBOL").text = name

        data_read = ET.SubElement(runnable, "DATA-READ-ACCESSS")
        data_write = ET.SubElement(runnable, "DATA-WRITE-ACCESSS")
        
        return runnable.get('UUID')

    def RemoveRunnable(self, runnable_uid):
        return self.Remove(behavior_path + "/RUNNABLES", "RUNNABLE-ENTITY", runnable_uid)

    def AddDataAccess(self, name, runnable_uid, type, port_type, swc_name, port_name, interface, data_element):
        root = self.tree.getroot()

        runnables = root.find(behavior_path + "/RUNNABLES")

        for runnable in runnables.findall("RUNNABLE-ENTITY"):
            if runnable.get('UUID') == runnable_uid:
                node = ET.Element
                access_type = ""

                if type == "WRITE":
                    node = runnable.find("DATA-WRITE-ACCESSS")
                    access_type = "DATA-WRITE-ACCESSS"
                else:
                    node = runnable.find("DATA-READ-ACCESSS")
                    access_type = "DATA-READ-ACCESSS"

                prototype_ref =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "/" + port_name
                data_element_ref =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + interface + "/" + data_element

                ### Validation
                for a in list(node):
                    if port_type == "R":
                        if a.find("DATA-ELEMENT-IREF/R-PORT-PROTOTYPE-REF").text == prototype_ref:
                            return False
                    else:
                        if a.find("DATA-ELEMENT-IREF/P-PORT-PROTOTYPE-REF").text == prototype_ref:
                            return False
                    
                    if a.find("DATA-ELEMENT-IREF/DATA-ELEMENT-PROTOTYPE-REF").text == data_element_ref:
                        return False

                for a in list(runnable.find("DATA-WRITE-ACCESSS")):
                    if a.find("SHORT-NAME").text == name:
                        return False

                for a in list(runnable.find("DATA-READ-ACCESSS")):
                    if a.find("SHORT-NAME").text == name:
                        return False
                ###

                access_node = ET.SubElement(node, access_type)
                ET.SubElement(access_node, "SHORT-NAME").text = name

                data_element = ET.SubElement(access_node, "DATA-ELEMENT-IREF")

                if port_type == "R":
                    ET.SubElement(data_element, "R-PORT-PROTOTYPE-REF", DEST="R-PORT-PROTOTYPE").text = prototype_ref
                else:
                    ET.SubElement(data_element, "P-PORT-PROTOTYPE-REF", DEST="P-PORT-PROTOTYPE").text = prototype_ref
                
                ET.SubElement(data_element, "DATA-ELEMENT-PROTOTYPE-REF", DEST="DATA-ELEMENT-PROTOTYPE-REF").text = data_element_ref

                return True

        return False

    def RemoveDataAccess(self, runnable_uid, name):
        root = self.tree.getroot()

        runnables = root.find(behavior_path + "/RUNNABLES")

        for runnable in runnables.findall("RUNNABLE-ENTITY"):
            if runnable.get('UUID') == runnable_uid:
                access = runnable.find("DATA-WRITE-ACCESSS")

                for a in list(access):
                    if a.find("SHORT-NAME").text == name:
                        access.remove(a)
                        return True

                access = runnable.find("DATA-READ-ACCESSS")

                for a in list(access):
                    if a.find("SHORT-NAME").text == name:
                        access.remove(a)
                        return True
                
        return False
    
    def AddDatatype(self, type):
        root = self.tree.getroot()

        elements = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS")

        for data_type in list(elements):
            d = data_type.find("SHORT-NAME")
            if d is not None and d.text == type:
                return False

        if type == "Boolean":
            data_type = ET.SubElement(elements, "BOOLEAN-TYPE")
            ET.SubElement(data_type, "SHORT-NAME").text = type
        elif type == "Float":
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
        return True

    def RemoveDataType(self, type):
        child_type = ''

        if type == "Bolean":
            child_type = "BOOLEAN-TYPE"
        elif type == "Float":
            child_type = "REAL-TYPE"
        else:
            child_type = "INTEGER-TYPE"

        root = self.tree.getroot()

        parent = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS")

        for child in parent.findall(child_type):
            if child.text == type:
                parent.remove(child)
                return True

        return False


    def AddInterface(self, name):
        root = self.tree.getroot()

        elements = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS")

        for interface in elements.findall("SENDER-RECEIVER-INTERFACE"):
            if interface.find("SHORT-NAME").text == name:
                return ''

        interface = ET.SubElement(elements, "SENDER-RECEIVER-INTERFACE", UUID=str(guid.uuid1()))

        ET.SubElement(interface, "SHORT-NAME").text = name

        self.AddAdminData(interface)

        ET.SubElement(interface, "DATA-ELEMENTS")

        return interface.get('UUID')

    def RemoveInterface(self, interface_uid):
        return self.Remove("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS", "SENDER-RECEIVER-INTERFACE", interface_uid)

    def AddDataElement(self, interface_uid, name, type, swc_name):
        root = self.tree.getroot()
        
        for interface in root.findall("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/SENDER-RECEIVER-INTERFACE"):
            if interface.get('UUID') == str(interface_uid):
                elements = interface.find("DATA-ELEMENTS")
                print(elements)

                for element in elements.findall("DATA-ELEMENT-PROTOTYPE"):
                    print(element.find("SHORT-NAME").text)
                    if element.find("SHORT-NAME").text == name:
                        return ''

                elements = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS")

                found = False

                for data_type in list(elements):
                    d = data_type.find("SHORT-NAME")
                    if d is not None and d.text == type:
                        found = True

                if found is False:
                    return ''

                element = ET.SubElement(interface, "DATA-ELEMENT-PROTOTYPE", UUID=str(guid.uuid1()))

                ET.SubElement(element, "SHORT-NAME").text = name

                self.AddAdminData(element)

                if type == "Boolean":
                    ET.SubElement(element, "TYPE-TREF", DEST="BOOLEAN-TYPE").text = "/" + swc_name + "_pkg/" + swc_name + "_swc/" + type
                elif type == "Float":
                    ET.SubElement(element, "TYPE-TREF", DEST="REAL-TYPE").text =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + type
                else:
                    ET.SubElement(element, "TYPE-TREF", DEST="INTEGER-TYPE").text =  "/" + swc_name + "_pkg/" + swc_name + "_swc/" + type

                return element.get('UUID')
        
        return ''

    def RemoveDataElement(self, interface_uid, element_uid):
        root = self.tree.getroot()
        
        for interface in root.findall("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/SENDER-RECEIVER-INTERFACE"):
            if interface.get('UUID') == str(interface_uid):
                elements = interface.find("DATA-ELEMENTS")
                
                for element in elements.findall("DATA-ELEMENT-PROTOTYPE"):
                    if element.find("SHORT-NAME").text == name:
                        elements.remove(element)
                        return True

        return False

    def AddPort(self, port_type, swc_name, name, interface_name):
        root = self.tree.getroot()

        ports = root.find(swc_path + "/PORTS")

        for port in list(ports):
            if port.find("SHORT-NAME").text == name:
                return ''
                print("hay")
        print(swc_name)
        elements = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS")

        found = False
        for interface in elements.findall("SENDER-RECEIVER-INTERFACE"):
            if interface.find("SHORT-NAME").text == interface_name:
                found = True
                print("mar7ba")

        if found is False:
            return ''

        port = "R-PORT-PROTOTYPE"
        if port_type == "Provider":
            port = "P-PORT-PROTOTYPE"

        ports_container = elements.find("APPLICATION-SOFTWARE-COMPONENT-TYPE/PORTS")

        port = ET.SubElement(ports_container, port, UUID=str(guid.uuid1()))
        ET.SubElement(port, "SHORT_NAME").text = name

        self.AddAdminData(port)

        if type == "R":
            ET.SubElement(port, "REQUIRED_INTERFACE-TREF", DEST="SENDER-RECEIVER-INTERFACE").text = "/" + swc_name + "_pkg" + "/" + swc_name + "_swc/" + interface_name
        else:
            ET.SubElement(port, "PROVIDED-INTERFACE-TREF", DEST="SENDER-RECEIVER-INTERFACE").text = "/" + swc_name + "_pkg" + "/"  + swc_name + "_swc/" + interface_name

        return port.get('UUID')

    def RemovePort(self, port_uid):
        root = self.tree.getroot()

        ports = root.find(swc_path + "/PORTS")
        name = ""

        for port in list(ports):
            if port.get('UUID') == port_uid:
                name = port.find("SHORT-NAME").text
                ports.remove(port)
                return True, name

        return False, name

    def CreateComposition(self,name):
        self.CreateDefaultARXML()
        root = self.tree.getroot()

        packages = ET.SubElement(root, "TOP-LEVEL-PACKAGES")

        package = ET.SubElement(packages, "AR-PACKAGE")
        ET.SubElement(package, "SHORT_NAME").text = "CrossControl"
        sub = ET.SubElement(package, "SUB-PACKAGES")

        package = ET.SubElement(sub, "AR-PACKAGE")
        ET.SubElement(package, "SHORT_NAME").text = "SoftwareComponents"

        elements = ET.SubElement(package, "ELEMENTS")

        composition_type = ET.SubElement(elements, "COMPOSITION-TYPE")
        ET.SubElement(composition_type, "SHORT_NAME").text = name + "Composition"

        components = ET.SubElement(composition_type, "COMPONENTS")
        connectors = ET.SubElement(composition_type, "CONNECTORS")

    def AddComponentToComposition(self,name,path):
        root = self.tree.getroot()
        components = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/COMPONENTS")

        component_prototype = ET.SubElement(components, "COMPONENT-PROTOTYPE")

        ET.SubElement(component_prototype, "SHORT_NAME").text = name + "Prototype"

        ET.SubElement(component_prototype, "TYPE-TREF", DEST="APPLICATION-SOFTWARE-COMPONENT-TYPE").text = path

    def AddConnector(self,p_port,p_port_component,r_port,r_port_component):
        root = self.tree.getroot()
        project_name = root.find(
            "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/SHORT-NAME").text
        p_component_path =  "/" + p_port_component + "_pkg/" + p_port_component + "_swc/" + p_port_component
        r_component_path =  "/" + r_port_component + "_pkg/" + r_port_component + "_swc/" + r_port_component

        connectors = root.find(
            "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/CONNECTORS")
        uid = guid.uuid1()
        assembly_connector_prototype = ET.SubElement(connectors, "ASSEMBLY-CONNECTOR-PROTOTYPE", uuid = str(uid))

        ET.SubElement(assembly_connector_prototype, "SHORT_NAME").text = p_port + "Composition"

        provider_iref = ET.SubElement(assembly_connector_prototype, "PROVIDER-IREF")
        ET.SubElement(provider_iref, "COMPONENT-PROTOTYPE-REF", DEST="COMPONENT-PROTOTYPE").text = "/CrossControl/SoftwareComponents/"+project_name+"/"+p_port_component+"Prototype"
        ET.SubElement(provider_iref, "P-PORT-PROTOTYPE-REF", DEST="P-PORT-PROTOTYPE").text = p_component_path + "/" + p_port

        requester_iref = ET.SubElement(assembly_connector_prototype, "REQUESTER-IREF")
        ET.SubElement(requester_iref, "COMPONENT-PROTOTYPE-REF",
                      DEST="COMPONENT-PROTOTYPE").text = "/CrossControl/SoftwareComponents/" + project_name + "/" + r_port_component + "Prototype"
        ET.SubElement(requester_iref, "R-PORT-PROTOTYPE-REF", DEST="R-PORT-PROTOTYPE").text = r_component_path + "/" + r_port
        return uid

    def RemoveComponentFromComposition(self,name):
        check = False
        root = self.tree.getroot()
        project_name = root.find(
            "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/SHORT-NAME").text
        for component_prototype in root.findall(
            "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/COMPONENTS/COMPONENT-PROTOTYPE"):
            if component_prototype.find("SHORT-NAME").text == name + "Prototype":
                root.remove(component_prototype)
                check = True
        if check:
            for connector_prototype in root.findall(
                    "TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/CONNECTORS/ASSEMBLY-CONNECTOR-PROTOTYPE"):
                p = connector_prototype.find("PROVIDER-IREF/COMPONENT-PROTOTYPE-REF").text
                r = connector_prototype.find("REQUESTER-IREF/COMPONENT-PROTOTYPE-REF").text
                if p == "/CrossControl/SoftwareComponents/"+project_name+"/"+name+"Prototype" or r == "/CrossControl/SoftwareComponents/"+project_name+"/"+name+"Prototype" :
                    root.remove(connector_prototype)
        return check

    def RemoveConnector(self,uid):
        return self.Remove("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/CONNECTORS", "ASSEMBLY-CONNECTOR-PROTOTYPE", uid)

    def RemoveConnectorByPort(self, port_name, swc_name):
        root = self.tree.getroot()
        connectors = root.find("TOP-LEVEL-PACKAGES/AR-PACKAGE/SUB-PACKAGES/AR-PACKAGE/ELEMENTS/COMPOSITION-TYPE/CONNECTORS")

        for connector in connectors.findall("ASSEMBLY-CONNECTOR-PROTOTYPE"):
            for p_iref in connector.findall("PROVIDER-IREF"):
                if p_iref.find("P-PORT-PROTOTYPE-REF").text == "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "/" + port_name:
                    connectors.remove(connector)
                    return True

            for r_iref in connector.findall("REQUESTER-IREF"):
                if r_iref.find("R-PORT-PROTOTYPE-REF").text == "/" + swc_name + "_pkg/" + swc_name + "_swc/" + swc_name + "/" + port_name:
                    connectors.remove(connector)
                    return True

        return False

    def __str__(self):
        if not self.build:
            root = self.tree.getroot()
            root.set("xmlns",autosar_org)
            root.set("xmlns:xsi",autosar_schema_instance)
            root.set("xsi:schemaLocation",autosar_schema_location)
        indented = Arxml.Indent(self.tree.getroot())
        return ET.tostring(self.tree.getroot()).decode("utf-8")