
from benchmark import Benchmark
from llm.evaluator_llm import evaluator_llm
import pickle
import os
from dotenv import load_dotenv
import os
import sys
from utils import Logger

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
benchmark_data = {}

logger = Logger("logs", sys.argv[2]).logger

def load_benchmark_data(filepath):
    with open(filepath, "rb") as file:
        contents = pickle.load(file)
    return contents

def extract_content(contents):
    # Convert keys to a sorted list to access the first and last elements
    keys = list(contents.keys())

    # print all values
    for key, (source_code, avg_energy, avg_runtime) in contents.items():
        logger.info(f"key: {key}, avg_energy: {avg_energy}, avg_runtime: {avg_runtime}")

    # Extract the first(original) and last(current) elements
    first_key = keys[0]
    last_key = keys[-1]

    first_value = contents[first_key]
    last_value = contents[last_key]


    # Loop through the contents to find the key with the lowest avg_energy
    min_avg_energy = float('inf')
    min_energy_key = None
    for key, (source_code, avg_energy, avg_runtime) in contents.items():
        if avg_energy < min_avg_energy:
            min_avg_energy = avg_energy
            min_energy_key = key

    min_value = contents[min_energy_key]

    # Prepare results in a structured format (dictionary)
    benchmark_info = {
        "original": {
            "source_code": first_value[0],
            "avg_energy": first_value[1],
            "avg_runtime": first_value[2]
        },
        "lowest_avg_energy": {
            "source_code": min_value[0],
            "avg_energy": min_value[1],
            "avg_runtime": min_value[2]
        },
        "current": {
            "source_code": last_value[0],
            "avg_energy": last_value[1],
            "avg_runtime": last_value[2]
        }
    }
    
    return benchmark_info

def print_benchmark_info(benchmark_info):
    """Prints the benchmark information in a structured format."""
    logger.info("Original: Average Energy: {}, Average Runtime: {}".format(benchmark_info["original"]["avg_energy"], benchmark_info["original"]["avg_runtime"]))
    logger.info("Lowest Average Energy: Average Energy: {}, Average Runtime: {}".format(benchmark_info["lowest_avg_energy"]["avg_energy"], benchmark_info["lowest_avg_energy"]["avg_runtime"]))
    logger.info("Current: Average Energy: {}, Average Runtime: {}".format(benchmark_info["current"]["avg_energy"], benchmark_info["current"]["avg_runtime"]))

def get_evaluator_feedback(llm, model_name, filename, optim_iter, client, assistant_id):

    language = filename.split(".")[-1]

    name = filename.split(".")[0]

    original_code_path = f"{USER_PREFIX}/benchmark_c++/{filename.split('.')[0]}/{filename}"

    optimized_code_path = f"{USER_PREFIX}/benchmark_c++/{filename.split('.')[0]}/optimized_{filename}"

    pkl_path = f"{USER_PREFIX}/src/runtime_logs/c++/benchmark_data.pkl"
    
    #create a benchmark object
    bmark = Benchmark(language, name, benchmark_data)
    
    #run benchmark
    #load the original code and data into pkl file 
    if optim_iter == 0:
        logger.info("Iteration 0, run benchmark on the original code")
        bmark.run(optim_iter)
        bmark.process_results(optim_iter, original_code_path)
        
    #load the optimized code and data
    optim_iter = optim_iter + 1 # offset
    logger.info(f"Iteration {optim_iter}, run benchmark on the optimized code")
    bmark.run(optim_iter)
    bmark.process_results(optim_iter, original_code_path if optim_iter == 0 else optimized_code_path)

    # Load benchmark data
    contents = load_benchmark_data(pkl_path)
    
    # Find the required benchmark elements
    benchmark_info = extract_content(contents)
    
    # Print the benchmark information
    print_benchmark_info(benchmark_info)

    #run evaluator
    evaluator_llm(llm, model_name, benchmark_info, client, assistant_id)