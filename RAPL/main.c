#include <stdio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include "rapl.h"
#include <sys/time.h>
#include <stdint.h>  // For uint64_t type
#include <sys/resource.h>  // For getrusage

#define RUNTIME 1

// Function to read the time-stamp counter (CPU cycles)
static inline uint64_t read_tsc() {
    unsigned int lo, hi;
    __asm__ volatile("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

// Function to get peak memory usage
void get_peak_memory_usage(long *peak_mem) {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);

    *peak_mem = usage.ru_maxrss; // Peak memory usage in kilobytes
}

int main (int argc, char **argv) {
    char command[500]="", language[500]="", test[500]="", path[500]="";
    int ntimes = 5;
    int core = 0;
    int i=0;

#ifdef RUNTIME
    double time_spent;
    struct timeval tvb, tva;
    struct timeval total_start_time, total_end_time; // For measuring total runtime
#endif

    FILE * fp;

    // Run command
    strcat(command, argv[1]);
    // Language name
    strcpy(language, argv[2]);
    // Path to language .csv file
    strcpy(path, "/home/rishi/E2COOL/src/runtime_logs/");
    strcat(language, ".csv");
    strcat(path, language);
    // Test name
    strcpy(test, argv[3]);

    fp = fopen(path, "a");

    rapl_init(core);

    // Start total time measurement for throughput calculation
    gettimeofday(&total_start_time, 0);

    for (i = 0; i < ntimes; i++) {
        fprintf(fp, "%s; ", test);

#ifdef RUNTIME
        // Get the start time using gettimeofday
        gettimeofday(&tvb, 0);
#endif
        // Measure the CPU cycles before execution
        uint64_t start_cycles = read_tsc();

        // Measure peak memory usage before execution
        long peak_mem_before = 0;
        get_peak_memory_usage(&peak_mem_before);

        rapl_before(fp, core);

        system(command);

        rapl_after(fp, core);

        // Measure the CPU cycles after execution
        uint64_t end_cycles = read_tsc();

        // Measure peak memory usage after execution
        long peak_mem_after = 0;
        get_peak_memory_usage(&peak_mem_after);

#ifdef RUNTIME
        // Get the end time using gettimeofday
        gettimeofday(&tva, 0);
        time_spent = (tva.tv_sec - tvb.tv_sec) * 1000000 + tva.tv_usec - tvb.tv_usec;
        time_spent = time_spent / 1000;  // Convert to milliseconds
#endif

        // Calculate CPU cycles used during the command execution
        uint64_t cpu_cycles = end_cycles - start_cycles;

        // Peak memory usage during the command execution
        long peak_mem_usage = peak_mem_after - peak_mem_before;

#ifdef RUNTIME
        fprintf(fp, "%G, ", time_spent);  // Log runtime in milliseconds
#endif

        // Log CPU cycles and peak memory usage
        fprintf(fp, "%lu, ", (unsigned long)cpu_cycles);  // Log CPU cycles used
        fprintf(fp, "%ld\n", peak_mem_usage);  // Peak memory usage (in KB)
    }

    // End total time measurement
    gettimeofday(&total_end_time, 0);

    // Calculate total time in seconds
    double total_time = (total_end_time.tv_sec - total_start_time.tv_sec) + 
                        (total_end_time.tv_usec - total_start_time.tv_usec) / 1000000.0;

    // Calculate throughput (executions per second)
    double throughput = ntimes / total_time;

    // Log throughput
    fprintf(fp, "Throughput (executions per second), %f\n", throughput);

    fclose(fp);
    fflush(stdout);

    return 0;
}
