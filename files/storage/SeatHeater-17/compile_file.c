#include "SeatHeatingController/SeatHeatingController_rte.h"
#include "SeatSensorLeft/SeatSensorLeft_rte.h"
#include "SeatSensorRight/SeatSensorRight_rte.h"
#include "HeatRegulator/HeatRegulator_rte.h"
#include "SeatHeater/SeatHeater_rte.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

Boolean dataChanged = false;

Boolean LeftSensorValue;
Boolean PassengerOnLeftSeat;
Boolean PassengerOnRightSeat;
Boolean RightSensorValue;
UInt32 LeftHeatLevel;
UInt32 LeftHeaterValue;
UInt32 Position;
UInt32 RegulatorValue;
UInt32 RightHeatLevel;
UInt32 RightHeaterValue;

UInt32 Rte_IRead_SeatHeatingController_UpdateHeating_RegulatorPosition_Position(void)
{
    return Position;
}

void Rte_IWrite_SeatHeatingController_UpdateHeating_HeaterLevels_RightHeatLevel(UInt32 u)
{
    RightHeatLevel = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement RightHeatLevel changed.\n");
    fclose(file);
    dataChanged = true;
}

void Rte_IWrite_SeatHeatingController_UpdateHeating_HeaterLevels_LeftHeatLevel(UInt32 u)
{
    LeftHeatLevel = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement LeftHeatLevel changed.\n");
    fclose(file);
    dataChanged = true;
}

Boolean Rte_IRead_SeatHeatingController_UpdateHeating_RightSeatStatus_PassengerOnRightSeat(void)
{
    return PassengerOnRightSeat;
}

Boolean Rte_IRead_SeatHeatingController_UpdateHeating_LeftSeatStatus_PassengerOnLeftSeat(void)
{
    return PassengerOnLeftSeat;
}

void Rte_IWrite_SeatSensorLeft_SeatSensorRunnableLeft_StatusLeft_PassengerOnLeftSeat(Boolean u)
{
    PassengerOnLeftSeat = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement PassengerOnLeftSeat changed.\n");
    fclose(file);
    dataChanged = true;
}

Boolean Rte_IRead_SeatSensorLeft_SeatSensorRunnableLeft_SensorLeftIO_LeftSensorValue(void)
{
    return LeftSensorValue;
}

void Rte_IWrite_SeatSensorRight_SeatSensorRunnableRight_StatusRight_PassengerOnRightSeat(Boolean u)
{
    PassengerOnRightSeat = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement PassengerOnRightSeat changed.\n");
    fclose(file);
    dataChanged = true;
}

Boolean Rte_IRead_SeatSensorRight_SeatSensorRunnableRight_SensorRightIO_RightSensorValue(void)
{
    return RightSensorValue;
}

void Rte_IWrite_HeatRegulator_HeatRegulatorRunnable_RegulatorPosition_Position(UInt32 u)
{
    Position = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement Position changed.\n");
    fclose(file);
    dataChanged = true;
}

UInt32 Rte_IRead_HeatRegulator_HeatRegulatorRunnable_RegulatorIO_RegulatorValue(void)
{
    return RegulatorValue;
}

UInt32 Rte_IRead_SeatHeater_SeatHeaterRunnable_Levels_LeftHeatLevel(void)
{
    return LeftHeatLevel;
}

UInt32 Rte_IRead_SeatHeater_SeatHeaterRunnable_Levels_RightHeatLevel(void)
{
    return RightHeatLevel;
}

void Rte_IWrite_SeatHeater_SeatHeaterRunnable_LeftSeaterIO_LeftHeaterValue(UInt32 u)
{
    LeftHeaterValue = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement LeftHeaterValue changed.\n");
    fclose(file);
    dataChanged = true;
}

void Rte_IWrite_SeatHeater_SeatHeaterRunnable_RightSeaterIO_RightHeaterValue(UInt32 u)
{
    RightHeaterValue = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement RightHeaterValue changed.\n");
    fclose(file);
    dataChanged = true;
}

pthread_mutex_t event_mutex = PTHREAD_MUTEX_INITIALIZER;

void Rewrite()
{
    if (!dataChanged)
        return;
    FILE* file;
    file = fopen("outputs.txt", "w+");
    fprintf(file, "{");
    printf("LeftHeaterValue ");
    printf("%d\n", LeftHeaterValue);
    fprintf(file, "\"LeftHeaterValue\" : \"%d\"", LeftHeaterValue);
    fprintf(file, ",");
    printf("RightHeaterValue ");
    printf("%d\n", RightHeaterValue);
    fprintf(file, "\"RightHeaterValue\" : \"%d\"", RightHeaterValue);
    fprintf(file, "}");
    fclose(file);
}

void Reread()
{
    FILE* file = NULL;

    while(file == NULL)
        file = fopen("inputs.txt", "r");

    int LeftSensorValue_t;
    int RegulatorValue_t;
    int RightSensorValue_t;

    fscanf(file, "%d,%d,%d,",&LeftSensorValue_t, &RegulatorValue_t, &RightSensorValue_t);

    LeftSensorValue = LeftSensorValue_t;
    RegulatorValue = RegulatorValue_t;
    RightSensorValue = RightSensorValue_t;
    printf("%d\n",LeftSensorValue_t);
    printf("%d\n",RegulatorValue_t);
    printf("%d\n",RightSensorValue_t);

    fclose(file);
}

typedef void (*Runnable)();

struct TimingEventArgs
{
    int period;
    Runnable runnable;
    char* runnable_name;
};

void* Timeout(void* arguments)
{
    sleep(60);
}

void* TimerThread(void* arguments)
{
    struct TimingEventArgs* args = (struct TimingEventArgs*) arguments;
    struct timespec ts;
    ts.tv_sec = (*args).period / 1000;
    ts.tv_nsec = ((*args).period % 1000) * 1000000;

    while(1)
    {
        nanosleep(&ts, NULL);
        pthread_mutex_lock(&event_mutex);
        Reread();
        FILE* file;
        file = fopen("log.txt", "a+");
        fprintf(file, "Runnable %s is starting.\n", (*args).runnable_name);
        (*args).runnable();
        fprintf(file, "Runnable %s executed.\n", (*args).runnable_name);
        fclose(file);
        Rewrite();
        pthread_mutex_unlock(&event_mutex);
    }
}

int main()
{
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "Compile successful, executable is running.\n");
    fclose(file);

    pthread_mutex_init(&event_mutex, NULL);

    struct TimingEventArgs HeatingUpdateEvent;
    HeatingUpdateEvent.runnable = UpdateHeating;
    HeatingUpdateEvent.period = 1000;
    HeatingUpdateEvent.runnable_name = "UpdateHeating";
    pthread_t HeatingUpdateEvent_thread;
    pthread_create(&HeatingUpdateEvent_thread, NULL, TimerThread, (void*)&HeatingUpdateEvent);

    struct TimingEventArgs SeatSensorLeftUpdateTimer;
    SeatSensorLeftUpdateTimer.runnable = SeatSensorRunnableLeft;
    SeatSensorLeftUpdateTimer.period = 1000;
    SeatSensorLeftUpdateTimer.runnable_name = "SeatSensorRunnableLeft";
    pthread_t SeatSensorLeftUpdateTimer_thread;
    pthread_create(&SeatSensorLeftUpdateTimer_thread, NULL, TimerThread, (void*)&SeatSensorLeftUpdateTimer);

    struct TimingEventArgs SeatSensorRightEvent;
    SeatSensorRightEvent.runnable = SeatSensorRunnableRight;
    SeatSensorRightEvent.period = 1000;
    SeatSensorRightEvent.runnable_name = "SeatSensorRunnableRight";
    pthread_t SeatSensorRightEvent_thread;
    pthread_create(&SeatSensorRightEvent_thread, NULL, TimerThread, (void*)&SeatSensorRightEvent);

    struct TimingEventArgs HeatRegulatorEvent;
    HeatRegulatorEvent.runnable = HeatRegulatorRunnable;
    HeatRegulatorEvent.period = 1000;
    HeatRegulatorEvent.runnable_name = "HeatRegulatorRunnable";
    pthread_t HeatRegulatorEvent_thread;
    pthread_create(&HeatRegulatorEvent_thread, NULL, TimerThread, (void*)&HeatRegulatorEvent);

    struct TimingEventArgs SeatHeaterEvent;
    SeatHeaterEvent.runnable = SeatHeaterRunnable;
    SeatHeaterEvent.period = 1000;
    SeatHeaterEvent.runnable_name = "SeatHeaterRunnable";
    pthread_t SeatHeaterEvent_thread;
    pthread_create(&SeatHeaterEvent_thread, NULL, TimerThread, (void*)&SeatHeaterEvent);

    pthread_t timeout_thread;
    pthread_create(&timeout_thread, NULL, Timeout, (void*)0);
    pthread_join(timeout_thread, NULL);

    pthread_mutex_destroy(&event_mutex);

    file;
    file = fopen("log.txt", "a+");
    fprintf(file, "Simulation time ended.");
    fclose(file);
}
