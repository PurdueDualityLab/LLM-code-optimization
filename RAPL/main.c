#include <stdio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include "rapl.h"
#include <sys/time.h>
#include <stdint.h>  // For uint64_t type
#include <sys/resource.h>  // For getrusage

#define RUNTIME 1
#define WARMUP_RUNS 1  // Number of warm-up iterations

// Function to read the time-stamp counter (CPU cycles)
static inline uint64_t read_tsc() {
    unsigned int lo, hi;
    __asm__ volatile("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

// Function to get peak memory usage
void get_peak_memory_usage(long *mem) {
    FILE *file = fopen("/proc/self/status", "r");
    if (!file) return -1;

    char line[256];
    long peak_mem = -1;

    while (fgets(line, sizeof(line), file)) {
        if (strncmp(line, "VmHWM:", 6) == 0) {  
            sscanf(line, "VmHWM: %ld kB", &peak_mem);
            break;
        }
    }

    fclose(file);
    *mem = peak_mem;
}

int main (int argc, char **argv) {
    char command[500]="", language[500]="", test[500]="", path[500]="";
    int ntimes = 5;
    int core = 0;
    int i=0;

#ifdef RUNTIME
    struct timespec start, end;  // Change timeval to timespec
    struct timespec total_start_time, total_end_time;
    double elapsed_time;
#endif

    FILE * fp;

    // Run command
    strcat(command, argv[1]);
    // Language name
    strcpy(language, argv[2]);
    // Path to language .csv file
    strcpy(path, "/home/rhasler/research-work/ee-swe/code-repos/purdue/E2COOL/src/runtime_logs/");
    strcat(language, ".csv");
    strcat(path, language);
    // Test name
    strcpy(test, argv[3]);

    fp = fopen(path, "a");

    rapl_init(core);

    // **Warm-up Phase**
    for (i = 0; i < WARMUP_RUNS; i++) {
        system(command);  // Run the command but don't record performance
    }

    // Start total time measurement for throughput calculation
    clock_gettime(CLOCK_MONOTONIC, &total_start_time); 

    for (i = 0; i < ntimes; i++) {
        fprintf(fp, "%s, ", test);

#ifdef RUNTIME
        // Get the start time using gettimeofday
        clock_gettime(CLOCK_MONOTONIC, &start);
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
        clock_gettime(CLOCK_MONOTONIC, &end);
        double elapsed_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1.0e9;
#endif

        // Calculate CPU cycles used during the command execution
        uint64_t cpu_cycles = end_cycles - start_cycles;

        // Peak memory usage during the command execution
        long peak_mem_usage = peak_mem_after - peak_mem_before;

#ifdef RUNTIME
        fprintf(fp, "%G, ", elapsed_time);  // Log runtime in milliseconds
#endif

        // Log CPU cycles and peak memory usage
        fprintf(fp, "%lu, ", (unsigned long)cpu_cycles);  // Log CPU cycles used
        fprintf(fp, "%ld\n", peak_mem_usage);  // Peak memory usage (in KB)
    }

    // End total time measurement
    clock_gettime(CLOCK_MONOTONIC, &total_end_time); 

    // Calculate total time in seconds
     double total_time = (total_end_time.tv_sec - total_start_time.tv_sec) + 
                        (total_end_time.tv_nsec - total_start_time.tv_nsec) / 1.0e9;

    // Calculate throughput (executions per second)
    double throughput = ntimes / total_time;

    // Log throughput
    fprintf(fp, "Throughput (executions per second), %f\n", throughput);

    fclose(fp);
    fflush(stdout);

    return 0;
}