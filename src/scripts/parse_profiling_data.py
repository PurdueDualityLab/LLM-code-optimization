from dotenv import load_dotenv
import heapq
import os


load_dotenv()
USER_PREFIX = os.getenv("USER_PREFIX")
PROFILER_DATA_CSV = "profiler_output.csv"

def compile_profiling_data(benchmark_name, prompting_method):
    profiling_data_csv = open(f"{USER_PREFIX}/benchmarks/{benchmark_name}/{PROFILER_DATA_CSV}", "r")
    profiling_data = [] if prompting_method == "raw" else {}

    for line in profiling_data_csv.readlines():
        line_items = line.split(",")
        if prompting_method == "raw":
            energy_value = float(line_items[0])
            profiling_data.append(energy_value)
        elif prompting_method == "labeled":
            energy_value, region_name = float(line_items[0]), line_items[-1][1:].strip("\n")
            profiling_data[region_name] = energy_value

    return profiling_data


def get_topK_data(profiling_data, topK):
    topK = min(topK, len(profiling_data.items()))
    topK_data = dict(heapq.nlargest(topK, profiling_data.items(), key=lambda data: data[1]))
    
    return topK_data



if __name__ == "__main__":
    benchmark_name = "binarytrees"
    prompting_method = "labeled" # or  "labeled"
    profiling_data = compile_profiling_data(benchmark_name, prompting_method)
    print(profiling_data)

    if prompting_method == "labeled":
        topK = 3
        topK_data = get_topK_data(profiling_data, topK)
        print(topK_data)