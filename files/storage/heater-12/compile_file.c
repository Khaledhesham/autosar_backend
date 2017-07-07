#include "Blinker/Blinker_rte.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

Boolean BlinkElement;

void SetValue(char* var, Float f_value , Boolean b_value, int i_value)
{
}

void Rte_IWrite_Blinker_BlinkerRunnable_Led_BlinkElement(Boolean u)
{
    BlinkElement = u;
}

pthread_mutex_t input_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t output_mutex = PTHREAD_MUTEX_INITIALIZER;

void Rewrite()
{
    pthread_mutex_lock(&output_mutex);
    FILE* file;
    file = fopen("outputs.txt", "w+");
    fprintf(file, "{");
    printf("%d", BlinkElement);
    fprintf(file, "\"BlinkElement\" : \"%s\"", BlinkElement ? "True" : "False");
    fprintf(file, "}");
    fclose(file);
    pthread_mutex_unlock(&output_mutex);
}

void Reread()
{
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
        Reread();
        nanosleep(&ts, NULL);
        (*args).runnable();
        Rewrite();
    }
}

int main()
{
    struct TimingEventArgs TimingEvent;
    TimingEvent.runnable = BlinkerRunnable;
    TimingEvent.period = 5000;
    pthread_t TimingEvent_thread;
    pthread_create(&TimingEvent_thread, NULL, TimerThread, (void*)&TimingEvent);
    pthread_t timeout_thread;
}
