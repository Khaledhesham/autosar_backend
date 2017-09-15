/*
   Code generated by Autosar Studio for software Component:
   HeatRegulator
*/

#ifndef RTE_HEADER_HeatRegulator_h_
#define RTE_HEADER_HeatRegulator_h_

#include "HeatRegulator_datatypes.h"

/*
   This file contains prototypes for the runnables and data access points
   used by the Software Component (HeatRegulator)
*/

void Rte_IWrite_HeatRegulator_HeatRegulatorRunnable_RegulatorPosition_Position(UInt32 u);

UInt32 Rte_IRead_HeatRegulator_HeatRegulatorRunnable_RegulatorIO_RegulatorValue(void);

extern void HeatRegulatorRunnable(void);


#endif
