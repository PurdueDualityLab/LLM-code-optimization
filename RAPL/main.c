#include <stdio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include "rapl.h"
#include <sys/time.h>
#include <stdint.h>
#include <sys/resource.h>

#define WARMUP_RUNS 2

static inline uint64_t read_tsc() {
    unsigned int lo, hi;
    __asm__ volatile("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

int main(int argc, char **argv) {
    char command[500] = "", language[500] = "", test[500] = "", path[500] = "";
    int ntimes = 5;
    int core = 0;
    int i = 0;

    struct timespec start, end;
    struct timespec total_start_time, total_end_time;
    double elapsed_time;

    FILE *fp;

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

    // Warm-up Phase
    for (i = 0; i < WARMUP_RUNS; i++) {
        system(command);
    }

    // Start total time measurement
    clock_gettime(CLOCK_MONOTONIC, &total_start_time);

    for (i = 0; i < ntimes; i++) {
        fprintf(fp, "%s, ", test);

        // Use /usr/bin/time to measure memory usage
        char time_command[600];
        snprintf(time_command, sizeof(time_command),  "/usr/bin/time -f '%%M' -o memory_usage.txt bash -c \"%s\"", command);

        // Start timing, CPU cycle, and energy measurement
        clock_gettime(CLOCK_MONOTONIC, &start);
        uint64_t start_cycles = read_tsc();
        rapl_before(fp, core);

        // Execute the command with memory measurement
        system(time_command);

        // End timing, CPU cycle, and energy measurement
        rapl_after(fp, core);
        uint64_t end_cycles = read_tsc();
        clock_gettime(CLOCK_MONOTONIC, &end);

        // Calculate elapsed time and CPU cycles
        elapsed_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1.0e9;
        uint64_t cpu_cycles = end_cycles - start_cycles;

        // Read memory usage from the file
        FILE *mem_file = fopen("memory_usage.txt", "r");
        long peak_mem_usage = 0;
        if (mem_file) {
            fscanf(mem_file, "%ld", &peak_mem_usage);
            fclose(mem_file);
            remove("memory_usage.txt");
        }

        // Log results
        fprintf(fp, "%G, ", elapsed_time);
        fprintf(fp, "%lu, ", (unsigned long)cpu_cycles);
        fprintf(fp, "%ld\n", peak_mem_usage);  // Peak memory usage (in KB)
    }

    // End total time measurement
    clock_gettime(CLOCK_MONOTONIC, &total_end_time);

    // Calculate total time and throughput
    double total_time = (total_end_time.tv_sec - total_start_time.tv_sec) +
                        (total_end_time.tv_nsec - total_start_time.tv_nsec) / 1.0e9;
    double throughput = ntimes / total_time;

    // Log throughput
    fprintf(fp, "Throughput (executions per second), %f\n", throughput);

    fclose(fp);
    fflush(stdout);

    return 0;
}
