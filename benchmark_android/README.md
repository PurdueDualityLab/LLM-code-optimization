##  How to run
- Start Android Studio and run the emulator and app
- (comment out start_emulator() if android studio is already running the emulator)
- run_trace_processor(), run_heap_profile(), run_cpu_profile() these function runs the profiling script
- Need to delete both files in cpu_trace and heap_trace so run_heap_profile(), run_cpu_profile() would record new trace, if the files in cpu_trace and heap_trace is not deleted it would not collect new trace
- (run_trace_processor(), run_heap_profile(), run_cpu_profile(), these three trace now run consecutively, I will make them run in three threads so it's proiling the same time interval)

## Current Status

**android_profiler.py**
- start the emulator and run heap_profile, cpu_profile, and record_android_trace to record trace.
- heap_profile, cpu_profile, and record_android_trace are executable to record trace.

**android_metric**
- metric_output.json: Contain (max, min, avg) cpu_frequency and memroy allocated per thread.
- filtered_metric_output: Contain (max, min, avg) cpu_frequency and memroy allocated per thread of the app process.

**cpu_trace and heap_trace**
- heap_trace/raw-trace: Contain trace of how many bytes were allocated per callstack and how many object were allocated per callstack.
- cpu_trace/raw-trace: Contain trace of the callstack.
- raw-trace: output trace file (display as flamegraph in Perfetto UI)
  
**trace_table_cotent**
- Contain all table I was able to qurey from the trace file

**perfetto_executable**    
- perfetto executable for converting tracefile, capture cpu and heap trace.

**trace_log**
- Logs when running perfetto executable.

**flamegraph_output.csv**
- Contain the funtion name, name of the binary or shared library (e.g., .so file) where the function resides.
- Contain the cumulative bytes allocated in a function

### Current Issue
- In android metric, the cpu_frequency occilate bewteen 1 and 2 kHz becuase the min/max cpu frequency value are set to 1 and 2 in emulator.
- In the flamegraph_output.csv, the function name of the app process are all empty for some reason.
- I asked the perfetto developers for suggestions and they suggested a tool call Watton, but it only works on real device: https://lpc.events/event/18/contributions/1842/attachments/1476/3126/LPC%202024%20-%20Wattson.pdf
- This is the CPU frequency of real device (from wattson slides)
<img width="403" alt="Screenshot 2025-03-12 at 3 14 57 PM" src="https://github.com/user-attachments/assets/c2aa67e2-5057-4c3f-942a-edba0fc71634" />

-  This is the emulator CPU frequency
<img width="626" alt="Screenshot 2025-03-12 at 3 16 18 PM" src="https://github.com/user-attachments/assets/6d78672f-e42d-4ed7-acaf-fa436530e26c" />
