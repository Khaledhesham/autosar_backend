/*
   Code generated by Autosar Studio for software Component:
   Blinker

   This file should contain definitions for the runnables.
   Prototypes for the runnable functions and data access methods

   Example:
   real_T Rte_IRead_swc_Runnable_Step_Port1_DataElement1();

   extern void Runnable_Step(void);

   Refer toBlinker_rte.h to find the current supported
   function headers
*/

#include "Blinker_rte.h"

/* WRITE YOUR CODE DOWN HERE */

Boolean blink = false;

void BlinkerRunnable()
{
    blink = !blink;
    Rte_IWrite_Blinker_BlinkerRunnable_Led_BlinkElement(blink);
}