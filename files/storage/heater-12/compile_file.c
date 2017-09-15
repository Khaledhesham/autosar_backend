#include "Blinker/Blinker_rte.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

Boolean dataChanged = false;

Boolean BlinkElement;


void Rte_IWrite_Blinker_BlinkerRunnable_Led_BlinkElement(Boolean u)
{
    BlinkElement = u;
    FILE* file;
    file = fopen("log.txt", "a+");
    fprintf(file, "DataElement BlinkElement changed.\n");
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
    printf("BlinkElement ");
    printf("%d\n", BlinkElement);
    fprintf(file, "\"BlinkElement\" : \"%s\"", BlinkElement ? "True" : "False");
    fprintf(file, "}");
    fclose(file);
}

void Reread()
{
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

    struct TimingEventArgs TimingEvent;
    TimingEvent.runnable = BlinkerRunnable;
    TimingEvent.period = 2000;
    TimingEvent.runnable_name = "BlinkerRunnable";
    pthread_t TimingEvent_thread;
    pthread_create(&TimingEvent_thread, NULL, TimerThread, (void*)&TimingEvent);

    pthread_t timeout_thread;
    pthread_create(&timeout_thread, NULL, Timeout, (void*)0);
    pthread_join(timeout_thread, NULL);

    pthread_mutex_destroy(&event_mutex);

    file;
    file = fopen("log.txt", "a+");
    fprintf(file, "Simulation time ended.");
    fclose(file);
}
