import subprocess
import time
import os
from perfetto.trace_processor import TraceProcessor
import json
import csv

from emulator import start_emulator, push_config_file, remove_existing_trace_file, run_perfetto, pull_trace_file, terminate_emulator
# Paths & Configurations
CONFIG_FILE = "energy_trace_config.pbtx"  # Local Perfetto config file
DEVICE_CONFIG_PATH = "/data/local/tmp/energy_trace_config.pbtx"  # Device path on emulator
TRACE_FILE = "/data/local/tmp/trace_file.perfetto-trace"
LOCAL_TRACE_PATH = "trace_file.perfetto-trace"
HEAP_TRACE_FILE = "heap_trace/raw-trace"
METRICS_OUTPUT_FILE = "android_metrics/metrics_output.json"


def run_record_android_trace(app_package_name):
    """Runs the 'record_android_trace' command to start tracing on the emulator."""
    print("Running 'record_android_trace' command to start tracing...")
    cmd = [
        "./perfetto_executable/record_android_trace",
        "-o", "trace_file.perfetto-trace",
        "-t", "30s",
        "-b", "64mb",
        "sched", "freq", "idle", "am", "wm", "gfx", "memory",   # Data souces for tracing (CPU Scheduling, CPU Frequency, CPU Idle, Memory)
        "-a", app_package_name,
        "--no-open"
    ]

    # Open a file to write the output
    with open("trace_log/record_android_trace_output.log", "w") as log_file:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Read the output line by line and write to both the terminal and the file
        for line in process.stdout:
            print(line, end='')  # Print to terminal
            log_file.write(line)  # Write to file

        # Read the error output line by line and write to both the terminal and the file
        for line in process.stderr:
            print(line, end='')  # Print to terminal
            log_file.write(line)  # Write to file

        process.wait()  # Wait for the process to complete

def run_heap_profile(duration, process_name):
    print("Running 'heap_profile' command to start heap profiling...")
    """Runs the 'heap_profile' command with the specified duration, process name, and output directory."""
    cmd = [
        "./perfetto_executable/heap_profile",
        "-d", str(duration), # Duration (ms)
        "-n", process_name,  # Process name
        "-o", "heap_trace" # Output directory
    ]

    # Open a file to write the output
    with open("trace_log/heap_profile_output.log", "w") as log_file:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Read the output line by line and write to both the terminal and the file
        for line in process.stdout:
            print(line, end='')  # Print to terminal
            log_file.write(line)  # Write to file

        # Read the error output line by line and write to both the terminal and the file
        for line in process.stderr:
            print(line, end='')  # Print to terminal
            log_file.write(line)  # Write to file

        process.wait()  # Wait for the process to complete

    print("Heap profiling completed.\n")

def run_trace_processor():
    """Runs the 'trace_processor' command to process the trace and output metrics to a file."""
    print("Running 'trace_processor' command to process the trace...")
    cmd = [
        "./perfetto_executable/trace_processor",
        "--run-metrics", "android_mem,android_cpu", # Run memory and CPU metrics
        "--metrics-output", "json",
        LOCAL_TRACE_PATH
    ]

    # Open a file to write the output
    with open(METRICS_OUTPUT_FILE, "w") as output_file:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            if not line.startswith("Loading trace:") and not line.startswith("["):
                output_file.write(line)  # Write to file

        # Read the error output line by line and write to both the terminal and the file
        for line in process.stderr:
            print(line, end='')  # Print to terminal

        process.wait()  # Wait for the process to complete

    print(f"Metrics output saved to: {METRICS_OUTPUT_FILE}\n")


def extract_app_process_data(input_file, output_file, app_name):
    with open(input_file, 'r') as infile:
        data = json.load(infile)

    # Extract the relevant process_info for the specified app from android_cpu
    app_cpu_process_info = []
    for process_info in data.get("android_cpu", {}).get("process_info", []):
        if process_info.get("name") == app_name:
            app_cpu_process_info.append(process_info)

    # Extract the relevant process_info for the specified app from android_mem
    app_mem_process_info = []
    for process_info in data.get("android_mem", {}).get("process_metrics", []):
        if process_info.get("process_name") == app_name:
            app_mem_process_info.append(process_info)

    # Write the filtered data to the output file
    with open(output_file, 'w') as outfile:
        json.dump({
            "metric": {
                "android_cpu": {"process_info": app_cpu_process_info},
                "android_mem": {"process_metrics": app_mem_process_info}
            }
        }, outfile, indent=2)

def list_tables_in_trace(trace_file):
    """Lists all tables available in the trace file."""
    print("Listing all tables in the trace file...")
    tp = TraceProcessor(trace=trace_file)
    qr_it = tp.query("SELECT name FROM sqlite_master WHERE type='table';")
    qr_df = qr_it.as_pandas_dataframe()
    print("Available tables:")
    print(qr_df.to_string())

def query_table_content(trace_file, table_name):
    """Queries the content of a specific table in the trace file."""
    print(f"Querying content of table: {table_name}")
    tp = TraceProcessor(trace=trace_file)
    qr_it = tp.query(f"SELECT * FROM {table_name};")
    qr_df = qr_it.as_pandas_dataframe()
    # print(qr_df.to_string())

    output_file = f"{table_name}_output.csv"
    output_dir = f"trace_table_content/{output_file}"
    qr_df.to_csv(output_dir, index=False)
    print(f"Table content saved to: {output_file}\n")
    

def get_heap_profile_data(trace_file):
    tables = ["perfetto_tables", "stack_profile_callsite", "stack_profile_mapping", "stack_profile_frame", "heap_profile_allocation", "heap_graph_object"]
    for table in tables:
        query_table_content(trace_file, table)

def get_cpu_data(trace_file):
    tables = ["perfetto_tables", "cpu_counter_track", "process_counter_track", "__intrinsic_cpu_freq", "__intrinsic_thread", "__intrinsic_process", "__intrinsic_counter"] 
    for table in tables:
        query_table_content(trace_file, table)

def get_cpu_profile_data(trace_file):
    tables = ["perfetto_tables", "stack_profile_callsite", "stack_profile_mapping", "stack_profile_frame", "heap_graph_object", "heap_graph_reference", "heap_graph_class"] 
    for table in tables:
        query_table_content(trace_file, table)

def get_latest_heap_profile_timestamp(trace_file):
    """Gets the latest timestamp from the heap_profile_allocation table."""
    print("Getting the latest heap profile timestamp...")
    tp = TraceProcessor(trace=trace_file)
    query = """
    SELECT ts FROM heap_profile_allocation ORDER BY ts;
    """
    qr_it = tp.query(query)
    qr_df = qr_it.as_pandas_dataframe()
    latest_timestamp = qr_df['ts'].iloc[0]
    print(qr_df)
    print(f"Latest heap profile timestamp: {latest_timestamp}")
    return latest_timestamp

def run_flamegraph_query(trace_file, output_file, timestamp):
    """Runs the flamegraph query and outputs the result to a file."""
    print("Running flamegraph query...")
    tp = TraceProcessor(trace=trace_file)
    query = f"""
    select
      name,
      map_name,
      cumulative_size
    from experimental_flamegraph(
      'native',
      {timestamp},
      NULL,
      1,
      NULL,
      NULL
    )
    order by abs(cumulative_size) desc;
    """
    qr_it = tp.query(query)
    qr_df = qr_it.as_pandas_dataframe()
    qr_df.to_csv(output_file, index=False)
    print(f"Flamegraph query result saved to: {output_file}\n")

def run_cpu_profile(process_name, frequency=100, duration=10000, output_dir="cpu_trace"):
    """
    Runs the cpu_profile script with the specified process name, frequency, duration, and output directory.
    """
    print(f"Running 'cpu_profile' command to start CPU profiling for process: {process_name}...")
    cmd = [
        "./perfetto_executable/cpu_profile",
        "-n", process_name,
        "-f", str(frequency),
        "-d", str(duration),
        "-o", output_dir
    ]

    # Open a file to write the output
    with open("trace_log/cpu_profile_output.log", "w") as log_file:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Read the output line by line and write to both the terminal and the file
        for line in process.stdout:
            print(line, end='') 
            log_file.write(line)

        # Read the error output line by line and write to both the terminal and the file
        for line in process.stderr:
            print(line, end='') 
            log_file.write(line)  

        process.wait() 

    print(f"CPU profiling completed successfully. Trace saved to: {output_dir}")

if __name__ == "__main__":
    print("Starting Android Profiler...")
    input_file = 'android_metrics/metrics_output.json'
    output_file = 'android_metrics/filtered_metrics_output.json'
    app_package_name = "ws.xsoh.etar.debug"


    # emulator_proc = start_emulator()
    # time.sleep(20)  # Wait for emulator to start
    
    # # Run the profiling steps
    # remove_existing_trace_file()
    # run_record_android_trace(app_package_name)
    # run_trace_processor()

    # extract_app_process_data(input_file, output_file, app_package_name)

    # run the heap profile
    # run_heap_profile(30000, app_package_name) #remember to delete the files in heap_trace
    # time.sleep(20)  # Wait for heap profiling to complete

    # # get the latest heap profile timestamp and run the flamegraph query
    # timestamp = get_latest_heap_profile_timestamp(HEAP_TRACE_FILE)
    # run_flamegraph_query(HEAP_TRACE_FILE, "flamegraph_output.csv", timestamp)

    timestamp = get_latest_heap_profile_timestamp("cpu_trace/raw-trace")
    run_flamegraph_query("cpu_trace/raw-trace", "flamegraph_output.csv", timestamp)
    # # Run the CPU profiling
    # run_cpu_profile(app_package_name)

    # # Get the list of tables in the trace file
    # get_heap_profile_data(HEAP_TRACE_FILE)
    # get_cpu_data(LOCAL_TRACE_PATH)
    # get_cpu_profile_data("cpu_trace/raw-trace")


    
    # # Terminate the emulator after profiling is completed.
    # terminate_emulator()
    
    print("Profiling completed successfully!")


# adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
# affected_cpus
# cpuinfo_cur_freq
# cpuinfo_max_freq
# cpuinfo_min_freq
# cpuinfo_transition_latency
# related_cpus
# scaling_available_frequencies
# scaling_available_governors
# scaling_cur_freq
# scaling_driver
# scaling_governor
# scaling_max_freq
# scaling_min_freq
# scaling_setspeed
# stats