import subprocess
from perfetto.trace_processor import TraceProcessor
from utils import run_command

# Paths & Configurations
CONFIG_FILE = "energy_trace_config.pbtx"  # Local Perfetto config file
DEVICE_CONFIG_PATH = "/data/local/tmp/energy_trace_config.pbtx"  # Device path on emulator
TRACE_FILE = "/data/local/tmp/trace_file.perfetto-trace"
LOCAL_TRACE_PATH = "trace_file.perfetto-trace"
AVD_NAME = "Pixel_6_Pro_API_30"

    
def start_emulator():
    """
    Starts the Android emulator in the background as an independent process.
    Returns the process handle.
    """
    
    emulator_cmd = [
        "/Users/jimmyho/Library/Android/sdk/emulator/emulator",
        "-avd", AVD_NAME,
        "-writable-system",
        "-selinux", "permissive",
        "-logcat", "*:V"
    ]

    process = subprocess.Popen(emulator_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Emulator started in background with PID:", process.pid)
    return process


def push_config_file():
    """Pushes the Perfetto config file to the emulator."""
    print("Pushing Perfetto config file...")
    run_command(["adb", "push", CONFIG_FILE, DEVICE_CONFIG_PATH])
    print("Config file pushed successfully.\n")

def remove_existing_trace_file():
    """Removes the existing Perfetto trace file from the emulator."""
    print("Removing existing Perfetto trace file...")
    run_command(["adb", "shell", "rm", "-f", TRACE_FILE])
    print("Existing trace file removed successfully.\n")

def run_perfetto():
    """Runs Perfetto tracing on the emulator."""
    print("Running Perfetto tracing...")
    run_command(["adb", "shell", "perfetto", "--txt", "-c", DEVICE_CONFIG_PATH, "-o", TRACE_FILE])
    print("Perfetto tracing completed.\n")

def pull_trace_file():
    """Pulls the Perfetto trace file from the emulator."""
    print("Pulling Perfetto trace file...")
    run_command(["adb", "pull", TRACE_FILE, LOCAL_TRACE_PATH])
    print(f"Trace file saved to: {LOCAL_TRACE_PATH}\n")

def terminate_emulator():
    """Terminates the Android emulator."""
    print("Terminating emulator...")
    run_command(["adb", "emu", "kill"])
    print("Emulator terminated.\n")