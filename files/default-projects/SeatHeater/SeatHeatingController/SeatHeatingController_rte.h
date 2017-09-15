/*
   Code generated by Autosar Studio for software Component:
   SeatHeatingController
*/

#ifndef RTE_HEADER_SeatHeatingController_h_
#define RTE_HEADER_SeatHeatingController_h_

#include "SeatHeatingController_datatypes.h"

/*
   This file contains prototypes for the runnables and data access points
   used by the Software Component (SeatHeatingController)
*/

UInt32 Rte_IRead_SeatHeatingController_UpdateHeating_RegulatorPosition_Position(void);

void Rte_IWrite_SeatHeatingController_UpdateHeating_HeaterLevels_RightHeatLevel(UInt32 u);

void Rte_IWrite_SeatHeatingController_UpdateHeating_HeaterLevels_LeftHeatLevel(UInt32 u);

Boolean Rte_IRead_SeatHeatingController_UpdateHeating_RightSeatStatus_PassengerOnRightSeat(void);

Boolean Rte_IRead_SeatHeatingController_UpdateHeating_LeftSeatStatus_PassengerOnLeftSeat(void);

extern void UpdateHeating(void);


#endif