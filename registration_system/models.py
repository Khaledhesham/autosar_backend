from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from files.models import File, Project, Directory
from arxml.models import Package, Composition, SoftwareComponent, TimingEvent, Runnable, Port, SenderReceiverInterface, Interface, DataElement, DataAccess, DataElementRef, DataType, Connector

def create_user_defaults(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        CreateDefaultsForUser(instance)

signals.post_save.connect(create_user_defaults, sender=User)


# Create your models here.

def MakeProject(project_name, req_user):
    project = Project(name=project_name, user=req_user)
    project.save()
    directory_name = project_name + str("-") + str(project.id)
    main_directory = Directory(name=directory_name, project=project)
    main_directory.save()
    arxml_file = File(name="Composition", file_type="arxml", directory=main_directory)
    arxml_file.save()
    interfaces_file = File(name="DataTypesAndInterfaces", file_type="arxml", directory=main_directory)
    interfaces_file.save()
    package = Package(project=project, interfaces_file=interfaces_file)
    package.save()
    package.Rewrite()
    composition = Composition(file=arxml_file, project=project)
    composition.save()
    composition.Rewrite()
    return project

def CreateDefaultsForUser(user):
    runnables = list()
    events = list()
    interfaces = list()
    sr_interfaces = list()
    ports = list()
    data_types = list()
    data_elements = list()
    refs = list()
    accs = list()
    connectors = list()

    with transaction.atomic():
        ### Blink
        blink_project = MakeProject("Blinkerrrrrrr", user)
        blinker_swc = SoftwareComponent.Make(blink_project, "Blinker", 33.4, 40.57)

        ### Double Blink
        double_blinker_project = MakeProject("DoubleBlinkerrrrrrr", user)
        double_blinker_swc = SoftwareComponent.Make(double_blinker_project, "DoubleBlinker", 51.56, 40.2)

        ### Seat Heater
        seat_heater_project = MakeProject("SeatHeaterrrrrrr", user)
        seat_heating_controller_swc = SoftwareComponent.Make(seat_heater_project, "SeatHeatingController", 45.613, 31.477)
        seat_sensor_left_swc = SoftwareComponent.Make(seat_heater_project, "SeatSensorLeft", 16.06, 48.32)
        seat_sensor_Right_swc = SoftwareComponent.Make(seat_heater_project, "SeatSensorRight", 76.06, 47.75)
        heat_regulator_swc = SoftwareComponent.Make(seat_heater_project, "HeatRegulator", 15.838, 22.42)
        seat_heater_swc = SoftwareComponent.Make(seat_heater_project, "SeatHeater", 75.95, 22.89)

        ###
        ### Runnables
        ###

        runnable_pk = Runnable.objects.last().pk

        ### Blink
        runnable = Runnable(id=runnable_pk + 1, name="BlinkerRunnable", concurrent=True, swc=blinker_swc)
        runnables.append(runnable)
        ### Double Blink
        top = Runnable(id=runnable_pk + 2, name="TopRunnable", concurrent=True, swc=double_blinker_swc)
        runnables.append(top)
        bottom = Runnable(id=runnable_pk + 3, name="BottomRunnable", concurrent=True, swc=double_blinker_swc)
        runnables.append(bottom)
        ### Seat Heater
        update_heating_runnable = Runnable(id=runnable_pk + 4, name="UpdateHeating", concurrent=True, swc=seat_heating_controller_swc)
        runnables.append(update_heating_runnable)
        seat_sensor_runnable_left = Runnable(id=runnable_pk + 5, name="SeatSensorRunnableLeft", concurrent=True, swc=seat_sensor_left_swc)
        runnables.append(seat_sensor_runnable_left)
        seat_sensor_runnable_right = Runnable(id=runnable_pk + 6, name="SeatSensorRunnableRight", concurrent=True, swc=seat_sensor_Right_swc)
        runnables.append(seat_sensor_runnable_right)
        heat_regulator_runnable = Runnable(id=runnable_pk + 7, name="HeatRegulatorRunnable", concurrent=True, swc=heat_regulator_swc)
        runnables.append(heat_regulator_runnable)
        seat_heater_runnable = Runnable(id=runnable_pk + 8, name="SeatHeaterRunnable", concurrent=True, swc=seat_heater_swc)
        runnables.append(seat_heater_runnable)

        Runnable.objects.bulk_create(runnables)

        ###
        ### Timing Events
        ###

        ### Blink
        event = TimingEvent(name="TimingEvent", runnable=runnable, period=1, swc=blinker_swc)
        events.append(event)
        ### Double Blink
        top_event = TimingEvent(name="TopEvent", runnable=top, period=1, swc=double_blinker_swc)
        events.append(top_event)
        bottom_event = TimingEvent(name="BottomEvent", runnable=bottom, period=1, swc=double_blinker_swc)
        events.append(bottom_event)
        ### Seat Heater
        heating_update_event = TimingEvent(name="HeatingUpdateEvent", runnable=update_heating_runnable, period=1, swc=seat_heating_controller_swc)
        events.append(heating_update_event)
        seat_sensor_left_update_timer = TimingEvent(name="SeatSensorLeftUpdateTimer", runnable=seat_sensor_runnable_left, period=1, swc=seat_sensor_left_swc)
        events.append(seat_sensor_left_update_timer)
        seat_sensor_right_update_timer = TimingEvent(name="SeatSensorRightUpdateTimer", runnable=seat_sensor_runnable_right, period=1, swc=seat_sensor_Right_swc)
        events.append(seat_sensor_right_update_timer)
        heat_regulator_event = TimingEvent(name="HeatRegulatorEvent", runnable=heat_regulator_runnable, period=1, swc=heat_regulator_swc)
        events.append(heat_regulator_event)
        seat_heater_event = TimingEvent(name="SeatHeaterEvent", runnable=seat_heater_runnable, period=1, swc=seat_heater_swc)
        events.append(seat_heater_event)

        TimingEvent.objects.bulk_create(events)

        ###
        ### Interfaces
        ###

        interface_pk = Interface.objects.last().pk

        ### Blink
        blinker_interface = Interface(id=interface_pk + 1, name="Blink", package=blink_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(blinker_interface)
        ## Double Blinker
        input_interface = Interface(id=interface_pk + 2, name="Input", package=double_blinker_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(input_interface)
        bottom_interface = Interface(id=interface_pk + 3, name="Bottom", package=double_blinker_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(bottom_interface)
        top_interface = Interface(id=interface_pk + 4, name="Top", package=double_blinker_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(top_interface)
        ## Seat Heater
        regulator_position_interface = Interface(id=interface_pk + 5, name="RegulatorPosition", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(regulator_position_interface)
        heater_level_interface = Interface(id=interface_pk + 6, name="HeaterLevel", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(heater_level_interface)
        left_seat_status_interface = Interface(id=interface_pk + 7, name="LeftSeatStatusInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(left_seat_status_interface)
        right_seat_status_interface = Interface(id=interface_pk + 8, name="RightSeatStatusInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(right_seat_status_interface)
        left_sensor_io_interface = Interface(id=interface_pk + 9, name="LeftSensorIOInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(left_sensor_io_interface)
        right_sensor_io_interface = Interface(id=interface_pk + 10, name="RightSensorIOInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(right_sensor_io_interface)
        regulator_io_interface = Interface(id=interface_pk + 11, name="RegulatorIOInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(regulator_io_interface)
        left_seat_heater_io_interface = Interface(id=interface_pk + 12, name="LeftSeatHeaterIOInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(left_seat_heater_io_interface)
        right_seat_heater_io_interface = Interface(id=interface_pk + 13, name="RightSeatHeaterIOInterface", package=seat_heater_project.package, type="SENDER-RECEIVER-INTERFACE")
        interfaces.append(right_seat_heater_io_interface)

        Interface.objects.bulk_create(interfaces)

        ###
        ### Sender Receiver Interfaces
        ###

        sr_interface_pk = SenderReceiverInterface.objects.last().pk

        ### Blink
        blinker_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 1, interface=blinker_interface)
        sr_interfaces.append(blinker_sr_interface)
        ## Double Blinker
        input_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 2, interface=input_interface)
        sr_interfaces.append(input_sr_interface)
        bottom_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 3, interface=bottom_interface)
        sr_interfaces.append(bottom_sr_interface)
        top_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 4, interface=top_interface)
        sr_interfaces.append(top_sr_interface)
        ## Seat Heater
        regulator_position_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 5, interface=regulator_position_interface)
        sr_interfaces.append(regulator_position_sr_interface)
        heater_level_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 6, interface=heater_level_interface)
        sr_interfaces.append(heater_level_sr_interface)
        left_seat_status_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 7, interface=left_seat_status_interface)
        sr_interfaces.append(left_seat_status_sr_interface)
        right_seat_status_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 8, interface=right_seat_status_interface)
        sr_interfaces.append(right_seat_status_sr_interface)
        left_sensor_io_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 9, interface=left_sensor_io_interface)
        sr_interfaces.append(left_sensor_io_sr_interface)
        right_sensor_io_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 10, interface=right_sensor_io_interface)
        sr_interfaces.append(right_sensor_io_sr_interface)
        regulator_io_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 11, interface=regulator_io_interface)
        sr_interfaces.append(regulator_io_sr_interface)
        left_seat_heater_io_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 12, interface=left_seat_heater_io_interface)
        sr_interfaces.append(left_seat_heater_io_sr_interface)
        right_seat_heater_io_sr_interface = SenderReceiverInterface(id=sr_interface_pk + 13, interface=right_seat_heater_io_interface)
        sr_interfaces.append(right_seat_heater_io_sr_interface)

        SenderReceiverInterface.objects.bulk_create(sr_interfaces)

        ###
        ### Ports
        ###

        port_pk = Port.objects.last().pk

        ### Blink
        led_port = Port(id=port_pk + 1, name="Led", swc=blinker_swc, type="P-PORT-PROTOTYPE", interface=blinker_interface, x=18.5, y=2.4)
        ports.append(led_port)
        ### Double Blinker
        switch_port = Port(id=port_pk + 2, name="Switch", swc=double_blinker_swc, type="R-PORT-PROTOTYPE", interface=input_interface, x=-1.5, y=2.08)
        ports.append(switch_port)
        top_led_port = Port(id=port_pk + 3, name="TopLed", swc=double_blinker_swc, type="P-PORT-PROTOTYPE", interface=top_interface, x=18.5, y=2.4)
        ports.append(top_led_port)
        bottom_led_port = Port(id=port_pk + 4, name="BottomLed", swc=double_blinker_swc, type="P-PORT-PROTOTYPE", interface=bottom_interface, x=18.5, y=7.8)
        ports.append(bottom_led_port)
        ### Seat Heater
        regulator_position_port = Port(id=port_pk + 5, name="RegulatorPosition", swc=seat_heating_controller_swc, type="R-PORT-PROTOTYPE", interface=regulator_position_interface, x=-1.5, y=1.29)
        ports.append(regulator_position_port)
        heater_levels_port = Port(id=port_pk + 6, name="HeaterLevels", swc=seat_heating_controller_swc, type="P-PORT-PROTOTYPE", interface=heater_level_interface, x=18.5, y=1.99)
        ports.append(heater_levels_port)
        left_seat_status_port = Port(id=port_pk + 7, name="LeftSeatStatus", swc=seat_heating_controller_swc, type="R-PORT-PROTOTYPE", interface=left_seat_status_interface, x=-1.5, y=6.67)
        ports.append(left_seat_status_port)
        right_seat_status_port = Port(id=port_pk + 8, name="RightSeatStatus", swc=seat_heating_controller_swc, type="R-PORT-PROTOTYPE", interface=right_seat_status_interface, x=18.5, y=7.87)
        ports.append(right_seat_status_port)
        status_left_port = Port(id=port_pk + 9, name="StatusLeft", swc=seat_sensor_left_swc, type="P-PORT-PROTOTYPE", interface=left_seat_status_interface, x=18.5, y=1.73)
        ports.append(status_left_port)
        status_right_port = Port(id=port_pk + 10, name="StatusRight", swc=seat_sensor_Right_swc, type="P-PORT-PROTOTYPE", interface=right_seat_status_interface, x=-1.5, y=3.69)
        ports.append(status_right_port)
        sensor_left_io_port = Port(id=port_pk + 11, name="SensorLeftIO", swc=seat_sensor_left_swc, type="R-PORT-PROTOTYPE", interface=left_sensor_io_interface, x=-1.5, y=3.58)
        ports.append(sensor_left_io_port)
        sensor_right_io_port = Port(id=port_pk + 12, name="SensorRightIO", swc=seat_sensor_Right_swc, type="R-PORT-PROTOTYPE", interface=right_sensor_io_interface, x=18.5, y=2.42)
        ports.append(sensor_right_io_port)
        position_port = Port(id=port_pk + 13, name="Position", swc=heat_regulator_swc, type="P-PORT-PROTOTYPE", interface=regulator_position_interface, x=18.5, y=2.89)
        ports.append(position_port)
        regulator_io_port = Port(id=port_pk + 14, name="RegulatorIO", swc=heat_regulator_swc, type="R-PORT-PROTOTYPE", interface=regulator_io_interface, x=-1.5, y=3.12)
        ports.append(regulator_io_port)
        levels_port = Port(id=port_pk + 15, name="Levels", swc=seat_heater_swc, type="R-PORT-PROTOTYPE", interface=heater_level_interface, x=-1.5, y=2.66)
        ports.append(levels_port)
        left_seater_io_port = Port(id=port_pk + 16, name="LeftSeaterIO", swc=seat_heater_swc, type="P-PORT-PROTOTYPE", interface=left_seat_heater_io_interface, x=18.5, y=2.427)
        ports.append(left_seater_io_port)
        right_seater_io_port = Port(id=port_pk + 17, name="RightSeaterIO", swc=seat_heater_swc, type="P-PORT-PROTOTYPE", interface=right_seat_heater_io_interface, x=18.5, y=7.16)
        ports.append(right_seater_io_port)

        Port.objects.bulk_create(ports)

        ###
        ### Data Types
        ###

        data_type_pk = DataType.objects.last().pk

        ### Blink
        blinker_boolean = DataType(id=data_type_pk + 1, package=blink_project.package, type="Boolean")
        data_types.append(blinker_boolean)
        ### Double Blinker
        double_blinker_boolean = DataType(id=data_type_pk + 2, package=double_blinker_project.package, type="Boolean")
        data_types.append(double_blinker_boolean)
        ### Seat Heater
        boolean_type = DataType(id=data_type_pk + 3, package=seat_heater_project.package, type="Boolean")
        data_types.append(boolean_type)
        uint32_type = DataType(id=data_type_pk + 4, package=seat_heater_project.package, type="UInt32")
        data_types.append(uint32_type)

        DataType.objects.bulk_create(data_types)

        ###
        ### Data Elements
        ###

        data_element_pk = DataElement.objects.last().pk

        ### Blink
        blink_element = DataElement(id=data_element_pk + 1, name="BlinkElement", interface=blinker_sr_interface, type=blinker_boolean)
        data_elements.append(blink_element)
        ### Double Blink
        toggle = DataElement(id=data_element_pk + 2, name="Toggle", interface=input_sr_interface, type=double_blinker_boolean)
        data_elements.append(toggle)
        top_de = DataElement(id=data_element_pk + 3, name="TopLed", interface=top_sr_interface, type=double_blinker_boolean)
        data_elements.append(top_de)
        bottom_de = DataElement(id=data_element_pk + 4, name="BottomLed", interface=bottom_sr_interface, type=double_blinker_boolean)
        data_elements.append(bottom_de)
        ### Seat Heater
        position_de = DataElement(id=data_element_pk + 5, name="Position", interface=regulator_position_sr_interface, type=uint32_type)
        data_elements.append(position_de)
        left_heat_level_de = DataElement(id=data_element_pk + 6, name="LeftHeatLevel", interface=left_seat_heater_io_sr_interface, type=uint32_type)
        data_elements.append(left_heat_level_de)
        right_heat_level_de = DataElement(id=data_element_pk + 7, name="RightHeatLevel", interface=right_seat_heater_io_sr_interface, type=uint32_type)
        data_elements.append(right_heat_level_de)
        passenger_on_left_seat_de = DataElement(id=data_element_pk + 8, name="PassengerOnLeftSeat", interface=left_seat_status_sr_interface, type=boolean_type)
        data_elements.append(passenger_on_left_seat_de)
        passenger_on_right_seat_de = DataElement(id=data_element_pk + 9, name="PassengerOnRightSeat", interface=right_seat_status_sr_interface, type=boolean_type)
        data_elements.append(passenger_on_right_seat_de)
        left_sensor_value_de = DataElement(id=data_element_pk + 10, name="LeftSensorValue", interface=left_sensor_io_sr_interface, type=boolean_type)
        data_elements.append(left_sensor_value_de)
        right_sensor_value_de = DataElement(id=data_element_pk + 11, name="RightSensorValue", interface=right_sensor_io_sr_interface, type=boolean_type)
        data_elements.append(right_sensor_value_de)
        regulator_value_de = DataElement(id=data_element_pk + 12, name="RegulatorValue", interface=regulator_io_sr_interface, type=uint32_type)
        data_elements.append(regulator_value_de)
        left_heater_value_de = DataElement(id=data_element_pk + 13, name="LeftHeaterValue", interface=left_seat_heater_io_sr_interface, type=uint32_type)
        data_elements.append(left_heater_value_de)
        right_heater_value_de = DataElement(id=data_element_pk + 14, name="RightHeaterValue", interface=right_seat_heater_io_sr_interface, type=uint32_type)
        data_elements.append(right_heater_value_de)

        DataElement.objects.bulk_create(data_elements)

        ###
        ### Data Element Ref
        ###

        data_element_ref = DataElementRef.objects.last().pk

        ### Blink
        ref = DataElementRef(id=data_element_ref + 1, port=led_port, data_element=blink_element)
        refs.append(ref)
        ### Double Blink
        ref1 = DataElementRef(id=data_element_ref + 2, port=switch_port, data_element=toggle)
        refs.append(ref1)
        ref2 = DataElementRef(id=data_element_ref + 3, port=top_led_port, data_element=top_de)
        refs.append(ref2)
        ref3 = DataElementRef(id=data_element_ref + 4, port=bottom_led_port, data_element=bottom_de)
        refs.append(ref3)
        ### Seat Heater
        regulator_position_to_position_ref = DataElementRef(id=data_element_ref + 5, port=regulator_position_port, data_element=position_de)
        refs.append(regulator_position_to_position_ref)
        heater_levels_to_right_heat_level_ref = DataElementRef(id=data_element_ref + 6, port=heater_levels_port, data_element=right_heat_level_de)
        refs.append(heater_levels_to_right_heat_level_ref)
        heater_levels_to_left_heat_level_ref = DataElementRef(id=data_element_ref + 7, port=heater_levels_port, data_element=left_heat_level_de)
        refs.append(heater_levels_to_left_heat_level_ref)
        right_seat_status_to_passenger_on_right_seat_ref = DataElementRef(id=data_element_ref + 8, port=right_seat_status_port, data_element=passenger_on_right_seat_de)
        refs.append(right_seat_status_to_passenger_on_right_seat_ref)
        left_seat_status_to_passenger_on_left_seat_ref = DataElementRef(id=data_element_ref + 9, port=left_seat_status_port, data_element=passenger_on_left_seat_de)
        refs.append(left_seat_status_to_passenger_on_left_seat_ref)
        position_to_position_ref = DataElementRef(id=data_element_ref + 10, port=position_port, data_element=position_de)
        refs.append(position_to_position_ref)
        status_left_to_passenger_on_left_seat_ref = DataElementRef(id=data_element_ref + 11, port=status_left_port, data_element=passenger_on_left_seat_de)
        refs.append(status_left_to_passenger_on_left_seat_ref)
        status_right_to_passenger_on_right_seat_ref = DataElementRef(id=data_element_ref + 12, port=status_right_port, data_element=passenger_on_right_seat_de)
        refs.append(status_right_to_passenger_on_right_seat_ref)
        levels_to_left_heat_level_ref = DataElementRef(id=data_element_ref + 13, port=levels_port, data_element=left_heat_level_de)
        refs.append(levels_to_left_heat_level_ref)
        levels_to_right_heat_level_ref = DataElementRef(id=data_element_ref + 14, port=levels_port, data_element=right_heat_level_de)
        refs.append(levels_to_right_heat_level_ref)
        sensor_left_io_to_left_sensor_value_ref = DataElementRef(id=data_element_ref + 15, port=sensor_left_io_port, data_element=left_sensor_value_de)
        refs.append(sensor_left_io_to_left_sensor_value_ref)
        sensor_right_io_to_right_sensor_value_ref = DataElementRef(id=data_element_ref + 16, port=sensor_right_io_port, data_element=right_sensor_value_de)
        refs.append(sensor_right_io_to_right_sensor_value_ref)
        regulator_io_to_regulator_value_ref = DataElementRef(id=data_element_ref + 17, port=regulator_io_port, data_element=regulator_value_de)
        refs.append(regulator_io_to_regulator_value_ref)
        left_seater_io_to_left_heater_value_ref = DataElementRef(id=data_element_ref + 18, port=left_seater_io_port, data_element=left_heater_value_de)
        refs.append(left_seater_io_to_left_heater_value_ref)
        right_seater_io_to_right_heater_value_ref = DataElementRef(id=data_element_ref + 19, port=right_seater_io_port, data_element=right_heater_value_de)
        refs.append(right_seater_io_to_right_heater_value_ref)

        DataElementRef.objects.bulk_create(refs)

        ###
        ### Data Access
        ###

        ### Blink
        acc = DataAccess(name="BlinkerAccess", runnable=runnable, data_element_ref=ref, type="DATA-WRITE-ACCESS")
        accs.append(acc)
        ### Double Blink
        acc1 = DataAccess(name="TopInputAccess", runnable=top, data_element_ref=ref1, type="DATA-READ-ACCESS")
        accs.append(acc1)
        acc2 = DataAccess(name="BottomInputAccess2", runnable=bottom, data_element_ref=ref1, type="DATA-READ-ACCESS")
        accs.append(acc2)
        acc3 = DataAccess(name="TopOutputAccess", runnable=top, data_element_ref=ref2, type="DATA-WRITE-ACCESS")
        accs.append(acc3)
        acc4 = DataAccess(name="BottomOutputAccess", runnable=bottom, data_element_ref=ref3, type="DATA-WRITE-ACCESS")
        accs.append(acc4)
        ### Seat Heater
        regulator_position_access = DataAccess(name="RegulatorPositionAccess", runnable=update_heating_runnable, data_element_ref=regulator_position_to_position_ref, type="DATA-READ-ACCESS")
        accs.append(regulator_position_access)
        heater_right_level_access = DataAccess(name="HeaterRightLevelAccess", runnable=update_heating_runnable, data_element_ref=heater_levels_to_right_heat_level_ref, type="DATA-WRITE-ACCESS")
        accs.append(heater_right_level_access)
        heater_left_level_access = DataAccess(name="HeaterLeftLevelAccess", runnable=update_heating_runnable, data_element_ref=heater_levels_to_left_heat_level_ref, type="DATA-WRITE-ACCESS")
        accs.append(heater_left_level_access)
        right_seat_status_access = DataAccess(name="RightSeatStatusAccess", runnable=update_heating_runnable, data_element_ref=right_seat_status_to_passenger_on_right_seat_ref, type="DATA-READ-ACCESS")
        accs.append(right_seat_status_access)
        left_seat_status_access = DataAccess(name="LeftSeatStatusAccess", runnable=update_heating_runnable, data_element_ref=left_seat_status_to_passenger_on_left_seat_ref, type="DATA-READ-ACCESS")
        accs.append(left_seat_status_access)
        seat_sensor_left_status_access = DataAccess(name="SeatSensorLeftStatusAccess", runnable=seat_sensor_runnable_left, data_element_ref=status_left_to_passenger_on_left_seat_ref, type="DATA-WRITE-ACCESS")
        accs.append(seat_sensor_left_status_access)
        seat_sensor_right_status_access = DataAccess(name="SeatSensorRightStatusAccess", runnable=seat_sensor_runnable_right, data_element_ref=status_right_to_passenger_on_right_seat_ref, type="DATA-WRITE-ACCESS")
        accs.append(seat_sensor_right_status_access)
        heat_regulator_position_access = DataAccess(name="HeatRegulatorPositionAccess", runnable=heat_regulator_runnable, data_element_ref=regulator_position_to_position_ref, type="DATA-WRITE-ACCESS")
        accs.append(heat_regulator_position_access)
        heat_regulator_IO_access = DataAccess(name="HeatRegulatorIOAccess", runnable=heat_regulator_runnable, data_element_ref=regulator_io_to_regulator_value_ref, type="DATA-READ-ACCESS")
        accs.append(heat_regulator_IO_access)
        seat_heater_left_level_access = DataAccess(name="SeatHeaterLeftLevelAccess", runnable=seat_heater_runnable, data_element_ref=levels_to_left_heat_level_ref, type="DATA-READ-ACCESS")
        accs.append(seat_heater_left_level_access)
        seat_heater_right_level_access = DataAccess(name="SeatHeaterRightLevelAccess", runnable=seat_heater_runnable, data_element_ref=levels_to_right_heat_level_ref, type="DATA-READ-ACCESS")
        accs.append(seat_heater_right_level_access)
        seat_heater_left_io_access = DataAccess(name="SeatHeaterLeftIOAccess", runnable=seat_heater_runnable, data_element_ref=left_seater_io_to_left_heater_value_ref, type="DATA-WRITE-ACCESS")
        accs.append(seat_heater_left_io_access)
        seat_heater_right_io_access = DataAccess(name="SeatHeaterRightIOAccess", runnable=seat_heater_runnable, data_element_ref=right_seater_io_to_right_heater_value_ref, type="DATA-WRITE-ACCESS")
        accs.append(seat_heater_right_io_access)
        seat_sensor_left_io_access = DataAccess(name="SeatSensorLeftIOAccess", runnable=seat_sensor_runnable_left, data_element_ref=sensor_left_io_to_left_sensor_value_ref, type="DATA-READ-ACCESS")
        accs.append(seat_sensor_left_io_access)
        seat_sensor_right_io_access = DataAccess(name="SeatSensorRightIOAccess", runnable=seat_sensor_runnable_right, data_element_ref=sensor_right_io_to_right_sensor_value_ref, type="DATA-READ-ACCESS")
        accs.append(seat_sensor_right_io_access)

        DataAccess.objects.bulk_create(accs)

        ###
        ### Connectors
        ###

        ### Seat Heater
        connector1 = Connector(composition=seat_heater_project.composition, p_port=position_port, r_port=regulator_position_port)
        connectors.append(connector1)
        connector2 = Connector(composition=seat_heater_project.composition, p_port=status_left_port, r_port=left_seat_status_port)
        connectors.append(connector2)
        connector3 = Connector(composition=seat_heater_project.composition, p_port=status_right_port, r_port=right_seat_status_port)
        connectors.append(connector3)
        connector4 = Connector(composition=seat_heater_project.composition, p_port=levels_port, r_port=heater_levels_port)
        connectors.append(connector4)

        Connector.objects.bulk_create(connectors)

        blink_project.package.Rewrite()
        blink_project.composition.Rewrite()
        blinker_swc.runnables_file.Write(open("files/default-projects/Blinker/Blinker/Blinker_runnables.c").read())

        double_blinker_project.package.Rewrite()
        double_blinker_project.composition.Rewrite()
        double_blinker_swc.runnables_file.Write(open("files/default-projects/DoubleBlinker/DoubleBlinker/DoubleBlinker_runnables.c").read())

        seat_heater_project.package.Rewrite()
        seat_heater_project.composition.Rewrite()
        seat_heating_controller_swc.runnables_file.Write(open("files/default-projects/SeatHeater/SeatHeatingController/SeatHeatingController_runnables.c").read())
        seat_sensor_left_swc.runnables_file.Write(open("files/default-projects/SeatHeater/SeatSensorLeft/SeatSensorLeft_runnables.c").read())
        seat_sensor_Right_swc.runnables_file.Write(open("files/default-projects/SeatHeater/SeatSensorRight/SeatSensorRight_runnables.c").read())
        heat_regulator_swc.runnables_file.Write(open("files/default-projects/SeatHeater/HeatRegulator/HeatRegulator_runnables.c").read())
        seat_heater_swc.runnables_file.Write(open("files/default-projects/SeatHeater/SeatHeater/SeatHeater_runnables.c").read())
    