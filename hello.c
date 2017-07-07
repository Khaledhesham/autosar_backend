#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

void *PrintHello(void *threadid)
{
    struct timespec ts;
    ts.tv_sec = 5;
    ts.tv_nsec = (5000 % 1000) * 1000000;
    nanosleep(&ts, NULL);
   long tid;
   tid = (long)threadid;
   printf("Hello World! It's me, thread #%ld!\n", tid);
   pthread_exit(NULL);
}


int main()
{
    pthread_t thread;
    pthread_create(&thread, NULL, PrintHello, (void *)1);
while(1);
}