class RunnableCompileFile:
    def __init__(self, file, package):
        for swc in package.softwarecomponent_set.all():
            print("#include \"" + swc.name + "/" + swc.name + "_rte.h\"", file=file)

        print("#include <stdio.h>", file=file)
        print("#include <time.h>", file=file)
        print("#include <unistd.h>", file=file)
        print("#include <pthread.h>", file=file)
        
        print("", file=file)
        print("Boolean dataChanged = false;", file=file)
        print("", file=file)

        data_elements_set = set()
        input_data_elements = set()
        output_data_elements = set()
        variable_set = set()

        for swc in package.softwarecomponent_set.all():
            for runnable in swc.runnable_set.all():
                for access in runnable.dataaccess_set.all():
                    data_elements_set.add(access.data_element_ref.data_element.type.type + " " + access.data_element_ref.data_element.name + ";")

                    if not hasattr(access.data_element_ref.port, "p_port_connector") \
                            and not hasattr(access.data_element_ref.port, "r_port_connector"):
                        if access.type == "DATA-READ-ACCESS":
                            input_data_elements.add(access.data_element_ref.data_element)
                        else:
                            output_data_elements.add(access.data_element_ref.data_element)

                for writeRef in runnable.writevariableref_set.all():
                    variable_set.add(writeRef.variable.type.type + " " + writeRef.variable.name + ";")

                for readRef in runnable.readvariableref_set.all():
                    variable_set.add(readRef.variable.type.type + " " + readRef.variable.name + ";")

        data_elements_set = sorted(data_elements_set)
        input_data_elements = sorted(input_data_elements)
        output_data_elements = sorted(output_data_elements)

        for de in data_elements_set:
            print(de, file=file)

        print("", file=file)

        for v in variable_set:
            print(v, file=file)

        print("", file=file)

        for swc in package.softwarecomponent_set.all():
            for runnable in swc.runnable_set.all():
                for access in runnable.dataaccess_set.all():
                    if access.type == "DATA-READ-ACCESS":
                        print(access.data_element_ref.data_element.type.type + " " + "Rte_IRead_" + runnable.swc.name + "_" + runnable.name + "_" + access.data_element_ref.port.name + "_" + access.data_element_ref.data_element.name + "(void)", file=file)
                        print("{", file=file)
                        print("    return " + access.data_element_ref.data_element.name + ";", file=file)
                        print("}", file=file)
                    else:
                        print("void " + "Rte_IWrite_" + runnable.swc.name + "_" + runnable.name + "_" + access.data_element_ref.port.name + "_" + access.data_element_ref.data_element.name + "(" + access.data_element_ref.data_element.type.type + " u)", file=file)
                        print("{", file=file)
                        print("    " + access.data_element_ref.data_element.name + " = u;", file=file)
                        print("    FILE* file;", file=file)
                        print("    file = fopen(\"log.txt\", \"a+\");", file=file)
                        print("    fprintf(file, \"DataElement " + access.data_element_ref.data_element.name + " changed.\\n\");", file=file)
                        print("    fclose(file);", file=file)
                        print("    dataChanged = true;", file=file)
                        print("}", file=file)

                    print("", file=file)

                for writeRef in runnable.writevariableref_set.all():
                    print("void " + "Rte_IrvIWrite_" + swc.name + "_" + runnable.name + "_" + writeRef.variable.name + "(" + writeRef.variable.type.type + " u)", file=file)
                    print("{", file=file)
                    print("    " + writeRef.variable.name + " = u;", file=file)
                    print("}", file=file)
                    print("", file=file)

                for readRef in runnable.readvariableref_set.all():
                    print(readRef.variable.type.type + " Rte_IrvIRead_" + swc.name + "_" + runnable.name + "_" + readRef.variable.name + "(void);", file=file)
                    print("{", file=file)
                    print("    return " + readRef.variable.name + ";", file=file)
                    print("{", file=file)
                    print("", file=file)

                for callPoint in runnable.servercallpoint_set.all():
                    s = "void Rte_Call_" + swc.name + "_" + callPoint.operation_ref.port.name + "_" callPoint.operation_ref.operation.name + "(", file=file)
                    
                    first = True

                    for arg in callPoint.operation_ref.operation.argument_set:
                        if not first:
                            s += ", "
                            first = False
                        s += arg.type.type + " " + arg.name

                    s += ")"

                    print(s, file=file)
                    print("{", file=file)

                    invoked_runnable = callPoint.operation_ref.operationinvokedevent.runnable

                    if invoked_runnable is not None:
                        s = "    " + invoked_runnable.name + "("

                        first = True

                        for arg in callPoint.operation_ref.operation.argument_set:
                            if not first:
                                s += ", "
                                first = False
                            s += arg.name
                        s += ");"

                        print("    FILE* file;", file=file)
                        print("    file = fopen(\"log.txt\", \"a+\");", file=file)
                        print("    fprintf(file, \"Runnable " + invoked_runnable.name + " is invoked by " + runnable.name + ".\\n\");", file=file)
                        print("    fprintf(file, \"Runnable " + invoked_runnable.name + " is starting.\\n\");", file=file)
                        print(s, file=file)
                        print("    fprintf(file, \"Runnable " + invoked_runnable.name + " executed.\\n\");", file=file)
                        print("    fclose(file);", file=file)

                    print("}", file=file)
                    print("", file=file)


        print("pthread_mutex_t event_mutex = PTHREAD_MUTEX_INITIALIZER;", file=file)
        print("", file=file)

        print("void Rewrite()", file=file)
        print("{", file=file)
        print("    if (!dataChanged)", file=file)
        print("        return;", file=file)

        start = True

        if output_data_elements:
            print("    FILE* file;", file=file)
            print("    file = fopen(\"outputs.txt\", \"w+\");", file=file)
            print("    fprintf(file, \"{\");", file=file)

            for e in output_data_elements:
                quote = r'"'
                escaped_quote = r'\"'
                s = r'\"%s\"'
                f = r'\"%f\"'
                d = r'\"%d\"'

                if not start:
                    print("    fprintf(file, \",\");", file=file)

                print("    printf(\"" + e.name + " \");", file=file)
                print("    printf(\"%d\\n\", " + e.name + ");", file=file)

                if e.type.type == "Boolean":
                    print("    fprintf(file, \"" + escaped_quote + e.name + escaped_quote + " : " + s + "\", " + e.name + " ? " + quote + "True" + quote + " : " + quote + "False" + quote + ");", file=file)
                elif e.type.type == "Float":
                    print("    fprintf(file, \"" + escaped_quote + e.name + escaped_quote + " : " + f + "\", " + e.name + ");", file=file)
                else:
                    print("    fprintf(file, \"" + escaped_quote + e.name + escaped_quote + " : " + d + "\", " + e.name + ");", file=file)

                start = False

            print("    fprintf(file, \"}\");", file=file)
            print("    fclose(file);", file=file)

        print("}", file=file)

        print("", file=file)
        print("void Reread()", file=file)
        print("{", file=file)

        if input_data_elements:
            print("    FILE* file = NULL;", file=file)
            print("", file=file)
            print("    while(file == NULL)", file=file)
            print("        file = fopen(\"inputs.txt\", \"r\");", file=file)
            print("", file=file)

            for e in input_data_elements:
                if e.type.type == "Float":
                    print("    float " + e.name + "_t;", file=file)
                else:
                    print("    int " + e.name + "_t;", file=file)

            print("", file=file)

            print("    fscanf(file, \"", end="", file=file)

            first = True

            for e in input_data_elements:
                if e.type.type == "Boolean" or e.type.type != "Float":
                    print("%d", end="", file=file)
                else:
                    print("%f", end="", file=file)

                print(",", end="", file=file)

            print("\",", end="", file=file)

            for e in input_data_elements:
                if not first:
                    print(", ", end="", file=file)

                print("&" + e.name + "_t", end="", file=file)

                first = False

            print(");", file=file)

            print("", file=file)

            for e in input_data_elements:
                print("    " + e.name + " = " + e.name + "_t;", file=file)

            for e in input_data_elements:
                print("    printf(\"%d\\n\"," + e.name + "_t);", file=file)

            print("", file=file)
            print("    fclose(file);", file=file)

        print("}", file=file)

        print("", file=file)
        print("typedef void (*Runnable)();", file=file)
        print("", file=file)

        print("struct TimingEventArgs", file=file)
        print("{", file=file)
        print("    int period;", file=file)
        print("    Runnable runnable;", file=file)
        print("    char* runnable_name;", file=file)
        print("};", file=file)
        print("", file=file)

        print("void* Timeout(void* arguments)", file=file)
        print("{", file=file)
        print("    sleep(60);", file=file)
        print("}", file=file)
        print("", file=file)

        print("void* TimerThread(void* arguments)", file=file)
        print("{", file=file)
        print("    struct TimingEventArgs* args = (struct TimingEventArgs*) arguments;", file=file)
        print("    struct timespec ts;", file=file)
        print("    ts.tv_sec = (*args).period / 1000;", file=file)
        print("    ts.tv_nsec = ((*args).period % 1000) * 1000000;", file=file)
        print("", file=file)
        print("    while(1)", file=file)
        print("    {", file=file)
        print("        nanosleep(&ts, NULL);", file=file)
        print("        pthread_mutex_lock(&event_mutex);", file=file)
        print("        Reread();", file=file)
        print("        FILE* file;", file=file)
        print("        file = fopen(\"log.txt\", \"a+\");", file=file)
        print("        fprintf(file, \"Runnable %s is starting.\\n\", (*args).runnable_name);", file=file)
        print("        (*args).runnable();", file=file)
        print("        fprintf(file, \"Runnable %s executed.\\n\", (*args).runnable_name);", file=file)
        print("        fclose(file);", file=file)
        print("        Rewrite();", file=file)
        print("        pthread_mutex_unlock(&event_mutex);", file=file)
        print("    }", file=file)
        print("}", file=file)
        print("", file=file)

        print("int main()", file=file)
        print("{", file=file)
        print("    FILE* file;", file=file)
        print("    file = fopen(\"log.txt\", \"a+\");", file=file)
        print("    fprintf(file, \"Compile successful, executable is running.\\n\");", file=file)
        print("    fclose(file);", file=file)

        print("", file=file)
        print("    pthread_mutex_init(&event_mutex, NULL);", file=file)
        print("", file=file)

        start = True

        for swc in package.softwarecomponent_set.all():
            for event in swc.timingevent_set.all():
                if event.runnable is not None:
                    if not start:
                        print("", file=file)

                    start = False

                    print("    struct TimingEventArgs " + event.name + ";", file=file)
                    print("    " + event.name + ".runnable = " + event.runnable.name + ";", file=file)
                    print("    " + event.name + ".period = " + str(int(event.period * 1000)) + ";", file=file)
                    print("    " + event.name + ".runnable_name = \"" + event.runnable.name + "\";", file=file)
                    print("    pthread_t " + event.name + "_thread;", file=file)
                    print("    pthread_create(&" + event.name + "_thread, NULL, TimerThread, (void*)&" + event.name + ");", file=file)

        print("", file=file)
        print("    pthread_t timeout_thread;", file=file)
        print("    pthread_create(&timeout_thread, NULL, Timeout, (void*)0);", file=file)
        print("    pthread_join(timeout_thread, NULL);", file=file)

        print("", file=file)
        print("    pthread_mutex_destroy(&event_mutex);", file=file)
        print("", file=file)

        print("    file;", file=file)
        print("    file = fopen(\"log.txt\", \"a+\");", file=file)
        print("    fprintf(file, \"Simulation time ended.\");", file=file)
        print("    fclose(file);", file=file)

        print("}", file=file)
