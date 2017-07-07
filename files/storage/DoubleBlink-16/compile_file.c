#include "DoubleBlink/DoubleBlink_rte.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

Boolean Toggle;
Boolean BottomLed;
Boolean TopLed;

void SetValue(char* var, Boolean Boolean_val){
    if (var == "Toggle")
        Toggle = Boolean_val;
}

Boolean Rte_IRead_DoubleBlink_TopRunnable_Switch_Toggle(void)
{
    return Toggle;
}

void Rte_IWrite_DoubleBlink_TopRunnable_TopLed_TopLed(Boolean u)
{
    TopLed = u;
}

void Rte_IWrite_DoubleBlink_BottomRunnable_BottomLed_BottomLed(Boolean u)
{
    BottomLed = u;
}

Boolean Rte_IRead_DoubleBlink_BottomRunnable_Switch_Toggle(void)
{
    return Toggle;
}

pthread_mutex_t input_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t output_mutex = PTHREAD_MUTEX_INITIALIZER;

void Rewrite()
{
    pthread_mutex_lock(&output_mutex);
    FILE* file;
    file = fopen("outputs.txt", "w+");
    fprintf(file, "{");
    printf("%d", TopLed);
    fprintf(file, "\"TopLed\" : \"%s\"", TopLed ? "True" : "False");
    fprintf(file, ",");
    printf("%d", BottomLed);
    fprintf(file, "\"BottomLed\" : \"%s\"", BottomLed ? "True" : "False");
    fprintf(file, "}");
    fclose(file);
    pthread_mutex_unlock(&output_mutex);
}

void Reread()
{
    pthread_mutex_lock(&input_mutex);
    FILE* file;
    file = fopen("inputs.txt", "r");
    fscanf(file, "%d",&Toggle);
    fclose(file);
    pthread_mutex_unlock(&input_mutex);
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
        Reread();
        nanosleep(&ts, NULL);
        (*args).runnable();
        Rewrite();
    }
}

int main()
{
    struct TimingEventArgs TopEvent;
    TopEvent.runnable = TopRunnable;
    TopEvent.period = 1000;
    pthread_t TopEvent_thread;
    pthread_create(&TopEvent_thread, NULL, TimerThread, (void*)&TopEvent);
    struct TimingEventArgs BottomEvent;
    BottomEvent.runnable = BottomRunnable;
    BottomEvent.period = 1000;
    pthread_t BottomEvent_thread;
    pthread_create(&BottomEvent_thread, NULL, TimerThread, (void*)&BottomEvent);
    pthread_t timeout_thread;
    pthread_create(&timeout_thread, NULL, Timeout, (void*)0);
    pthread_join(timeout_thread, NULL);
}
