#include "DoubleBlink/DoubleBlink_rte.h"
#include <stdio.h>
#include <time.h>

Boolean TopLed;
Boolean Toggle;
Boolean BottomLed;

void SetValue(char* var, Float f_value , Boolean b_value, int i_value)
{
    if (var == "Toggle")
        Toggle= b_value;
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
    struct TimingEvent TopEvent;
    TopEvent.runnable = TopRunnable;
    TopEvent.period = 0;
    TopEvent.trigger = clock() + 0;

    struct TimingEvent BottomEvent;
    BottomEvent.runnable = TopRunnable;
    BottomEvent.period = 0;
    BottomEvent.trigger = clock() + 0;

    Boolean save = true;

    while (1)
    {
        FILE* file;
        file = fopen("inputs.txt", "r");
        fscanf(file, "%d",&Toggle);
        fclose(file);
        if (Update(&TopEvent))
            save = true;
        if (Update(&BottomEvent))
            save = true;

        if (save)
        {
            FILE* file;
            file = fopen("outputs.txt", "w+");
            fprintf(file, "{");
            printf("%d", TopLed);
            fprintf(file, "\"TopLed\" : \"%s\"", TopLed ? "True" : "False");
            fprintf(",")
            printf("%d", BottomLed);
            fprintf(file, "\"BottomLed\" : \"%s\"", BottomLed ? "True" : "False");
            fprintf(file, "}");
            fclose(file);
        }

        save = false;
    }
}
