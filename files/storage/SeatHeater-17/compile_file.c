#include "SeatHeatingController/SeatHeatingController_rte.h"
#include "SeatSensorLeft/SeatSensorLeft_rte.h"
#include "SeatSensorRight/SeatSensorRight_rte.h"
#include "HeatRegulator/HeatRegulator_rte.h"
#include "SeatHeater/SeatHeater_rte.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

Boolean RightHeatLevel;
Boolean LeftSensorValue;
Boolean PassengerOnRightSeat;
UInt32 RegulatorValue;
Boolean Position;
Boolean LeftHeatLevel;
Boolean PassengerOnLeftSeat;

void SetValue(char* var, Boolean Boolean_val, UInt32 UInt32_val){
    if (var == "Position")
        Position = Boolean_val;
    if (var == "LeftHeatLevel")
        LeftHeatLevel = Boolean_val;
    if (var == "RightHeatLevel")
        RightHeatLevel = Boolean_val;
    if (var == "PassengerOnLeftSeat")
        PassengerOnLeftSeat = Boolean_val;
    if (var == "PassengerOnRightSeat")
        PassengerOnRightSeat = Boolean_val;
    if (var == "RegulatorValue")
        RegulatorValue = UInt32_val;
}

Boolean Rte_IRead_SeatHeatingController_UpdateHeating_RegulatorPosition_Position(void)
{
    return Position;
}

void Rte_IWrite_SeatHeatingController_UpdateHeating_HeaterLevels_RightHeatLevel(Boolean u)
{
    RightHeatLevel = u;
}

void Rte_IWrite_SeatHeatingController_UpdateHeating_HeaterLevels_LeftHeatLevel(Boolean u)
{
    LeftHeatLevel = u;
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
}

void Rte_IWrite_SeatSensorLeft_SeatSensorRunnableLeft_SensorLeftIO_LeftSensorValue(Boolean u)
{
    LeftSensorValue = u;
}

void Rte_IWrite_HeatRegulator_HeatRegulatorRunnable_RegulatorPosition_Position(Boolean u)
{
    Position = u;
}

UInt32 Rte_IRead_HeatRegulator_HeatRegulatorRunnable_RegulatorIO_RegulatorValue(void)
{
    return RegulatorValue;
}

Boolean Rte_IRead_SeatHeater_SeatHeaterRunnable_Levels_LeftHeatLevel(void)
{
    return LeftHeatLevel;
}

Boolean Rte_IRead_SeatHeater_SeatHeaterRunnable_Levels_RightHeatLevel(void)
{
    return RightHeatLevel;
}

pthread_mutex_t event_mutex = PTHREAD_MUTEX_INITIALIZER;

void Rewrite()
{
    FILE* file;
    file = fopen("outputs.txt", "w+");
    fprintf(file, "{");
    printf("Position ");
    printf("%d\n", Position);
    fprintf(file, "\"Position\" : \"%s\"", Position ? "True" : "False");
    fprintf(file, ",");
    printf("LeftHeatLevel ");
    printf("%d\n", LeftHeatLevel);
    fprintf(file, "\"LeftHeatLevel\" : \"%s\"", LeftHeatLevel ? "True" : "False");
    fprintf(file, ",");
    printf("RightHeatLevel ");
    printf("%d\n", RightHeatLevel);
    fprintf(file, "\"RightHeatLevel\" : \"%s\"", RightHeatLevel ? "True" : "False");
    fprintf(file, ",");
    printf("PassengerOnLeftSeat ");
    printf("%d\n", PassengerOnLeftSeat);
    fprintf(file, "\"PassengerOnLeftSeat\" : \"%s\"", PassengerOnLeftSeat ? "True" : "False");
    fprintf(file, ",");
    printf("LeftSensorValue ");
    printf("%d\n", LeftSensorValue);
    fprintf(file, "\"LeftSensorValue\" : \"%s\"", LeftSensorValue ? "True" : "False");
    fprintf(file, "}");
    fclose(file);
}

void Reread()
{
    FILE* file = NULL;

    while(file == NULL)
        file = fopen("inputs.txt", "r");

    int Position_t;
    int LeftHeatLevel_t;
    int RightHeatLevel_t;
    int PassengerOnLeftSeat_t;
    int PassengerOnRightSeat_t;
    int RegulatorValue_t;

    fscanf(file, "%d,%d,%d,%d,%d,%d,",&Position_t, &LeftHeatLevel_t, &RightHeatLevel_t, &PassengerOnLeftSeat_t, &PassengerOnRightSeat_t, &RegulatorValue_t);

    Position = Position_t;
    LeftHeatLevel = LeftHeatLevel_t;
    RightHeatLevel = RightHeatLevel_t;
    PassengerOnLeftSeat = PassengerOnLeftSeat_t;
    PassengerOnRightSeat = PassengerOnRightSeat_t;
    RegulatorValue = RegulatorValue_t;

    fclose(file);
}

typedef void (*Runnable)();

struct TimingEventArgs
{
    int period;
    Runnable runnable;
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
        (*args).runnable();
        Rewrite();
        pthread_mutex_unlock(&event_mutex);
    }
}

int main()
{
    pthread_mutex_init(&event_mutex, NULL);
    struct TimingEventArgs HeatingUpdateEvent;
    HeatingUpdateEvent.runnable = UpdateHeating;
    HeatingUpdateEvent.period = 0;
    pthread_t HeatingUpdateEvent_thread;
    pthread_create(&HeatingUpdateEvent_thread, NULL, TimerThread, (void*)&HeatingUpdateEvent);

    struct TimingEventArgs SeatSensorLeftUpdateTimer;
    SeatSensorLeftUpdateTimer.runnable = SeatSensorRunnableLeft;
    SeatSensorLeftUpdateTimer.period = 0;
    pthread_t SeatSensorLeftUpdateTimer_thread;
    pthread_create(&SeatSensorLeftUpdateTimer_thread, NULL, TimerThread, (void*)&SeatSensorLeftUpdateTimer);

    pthread_t timeout_thread;
    pthread_create(&timeout_thread, NULL, Timeout, (void*)0);
    pthread_join(timeout_thread, NULL);

    pthread_mutex_destroy(&event_mutex);
}
