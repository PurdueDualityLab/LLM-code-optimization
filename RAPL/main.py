import subprocess
import time
import psutil
import os
from datetime import datetime

WARMUP_RUNS = 2
NTIMES = 5
LOG_DIR = "/home/parth/LLM-code-optimization/src/runtime_logs/"
PERF_EVENTS = "cycles"

def run_benchmark(command, language, test_name):
    log_path = os.path.join(LOG_DIR, f"{language}.csv")

    # Warm-up
    for _ in range(WARMUP_RUNS):
        subprocess.run(command, shell=True)

    results = []

    total_start = time.time()

    with open(log_path, "a") as fp:
        for _ in range(NTIMES):
            fp.write(f"{test_name}, ")

            # Construct perf + memory tracking command
            perf_cmd = (
                f"/usr/bin/time -f '%M' -o memory_usage.txt "
                f"perf stat -e {PERF_EVENTS} -x , -o perf_output.txt bash -c \"{command}\""
            )

            start = time.time()

            # Energy measurement start
            subprocess.run(["sudo", "./rapl_before.sh", "0"], check=True)

            # Execute the benchmark with perf and memory measurement
            subprocess.run(perf_cmd, shell=True)

            # Energy measurement end
            subprocess.run(["sudo", "./rapl_after.sh", "0"], check=True)

            end = time.time()
            elapsed_time = end - start

            # Read CPU cycles
            with open("perf_output.txt") as f:
                lines = f.readlines()
            cycles = 0
            for line in lines:
                if "cycles" in line:
                    cycles = int(line.strip().split(",")[0])
                    break
            os.remove("perf_output.txt")

            # Read memory usage
            with open("memory_usage.txt") as f:
                peak_memory_kb = int(f.read().strip())
            os.remove("memory_usage.txt")

            # Log results
            fp.write(f"{elapsed_time:.6f}, {cycles}, {peak_memory_kb}\n")

        total_end = time.time()
        total_duration = total_end - total_start
        throughput = NTIMES / total_duration
        fp.write(f"Throughput (executions per second), {throughput}\n")

    print("Benchmarking complete.")
