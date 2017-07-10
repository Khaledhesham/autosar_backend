#include "DoubleBlink/DoubleBlink_rte.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

Boolean dataChanged = false;

Boolean BottomLed;
Boolean Toggle;
Boolean TopLed;

Boolean Rte_IRead_DoubleBlink_TopRunnable_Switch_Toggle(void)
{
    return Toggle;
}

void Rte_IWrite_DoubleBlink_TopRunnable_TopLed_TopLed(Boolean u)
{
    TopLed = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement TopLed changed.\n");
    fclose(file);
    dataChanged = true;
}

void Rte_IWrite_DoubleBlink_BottomRunnable_BottomLed_BottomLed(Boolean u)
{
    BottomLed = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement BottomLed changed.\n");
    fclose(file);
    dataChanged = true;
}

Boolean Rte_IRead_DoubleBlink_BottomRunnable_Switch_Toggle(void)
{
    return Toggle;
}

pthread_mutex_t event_mutex = PTHREAD_MUTEX_INITIALIZER;

void Rewrite()
{
    if (!dataChanged)
        return;
    FILE* file;
    file = fopen("outputs.txt", "w+");
    fprintf(file, "{");
    printf("BottomLed ");
    printf("%d\n", BottomLed);
    fprintf(file, "\"BottomLed\" : \"%s\"", BottomLed ? "True" : "False");
    fprintf(file, ",");
    printf("TopLed ");
    printf("%d\n", TopLed);
    fprintf(file, "\"TopLed\" : \"%s\"", TopLed ? "True" : "False");
    fprintf(file, "}");
    fclose(file);
}

void Reread()
{
    FILE* file = NULL;

    while(file == NULL)
        file = fopen("inputs.txt", "r");

    int Toggle_t;

    fscanf(file, "%d,",&Toggle_t);

    Toggle = Toggle_t;
    printf("%d\n",Toggle_t);

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

    struct TimingEventArgs TopEvent;
    TopEvent.runnable = TopRunnable;
    TopEvent.period = 2000;
    TopEvent.runnable_name = "TopRunnable";
    pthread_t TopEvent_thread;
    pthread_create(&TopEvent_thread, NULL, TimerThread, (void*)&TopEvent);

    struct TimingEventArgs BottomEvent;
    BottomEvent.runnable = BottomRunnable;
    BottomEvent.period = 2000;
    BottomEvent.runnable_name = "BottomRunnable";
    pthread_t BottomEvent_thread;
    pthread_create(&BottomEvent_thread, NULL, TimerThread, (void*)&BottomEvent);

    pthread_t timeout_thread;
    pthread_create(&timeout_thread, NULL, Timeout, (void*)0);
    pthread_join(timeout_thread, NULL);

    pthread_mutex_destroy(&event_mutex);

    file;
    file = fopen("log.txt", "a+");
    fprintf(file, "Simulation time ended.");
    fclose(file);
}
