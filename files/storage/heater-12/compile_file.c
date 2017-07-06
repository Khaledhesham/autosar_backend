#include "Blinker/Blinker_rte.h"
#include <stdio.h>
#include <time.h>

Boolean BlinkElement;

void SetValue(char* var, Float f_value , Boolean b_value, int i_value)
{
}

void Rte_IWrite_Blinker_BlinkerRunnable_Led_BlinkElement(Boolean u)
{
    BlinkElement = u;
}

typedef void (*Runnable)();

struct TimingEvent
{
    clock_t trigger;
    int period;
    Runnable runnable;
};

Boolean Update(struct TimingEvent* event)
{

    if (clock() >= event->trigger)
    {
        event->runnable();
        event->trigger = clock() + event->period;
        return true;
    }

    return false;
}

int main()
{
    struct TimingEvent TimingEvent;
    TimingEvent.runnable = BlinkerRunnable;
    TimingEvent.period = 5000;
    TimingEvent.trigger = clock() + 5000;

    Boolean save = true;

    while (1)
    {
        if (Update(&TimingEvent))
            save = true;

        if (save)
        {
            FILE* file;
            file = fopen("outputs.txt", "w+");
            fprintf(file, "{");
            printf("%d", BlinkElement);
            fprintf(file, "\"BlinkElement\" : \"%s\"", BlinkElement ? "True" : "False");
            fprintf(file, "}");
            fclose(file);
        }

        save = false;
    }
}
