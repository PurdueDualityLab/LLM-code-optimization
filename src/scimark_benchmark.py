from benchmark import Benchmark
from dotenv import load_dotenv
import os
import subprocess
import sys
from utils import Logger
import re
from abstract_syntax_trees.java_ast import JavaAST
import csv

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
logger = Logger("logs", sys.argv[2]).logger

class SciMarkBenchmark(Benchmark):
    def __init__(self, program):
        self.program = program
        self.compilation_error = None
        self.energy_data = {}
        self.evaluator_feedback_data = {}
        self.expect_test_output = None
        self.original_code = None
        self.optimization_iteration = 0
        self.set_original_code()
    
    # Copy the original code to the optimized code (because we only measure the optimized code)
    def set_original_code(self):
        command = f"cp {USER_PREFIX}/benchmark_scimark/{self.program}/{self.program}OptimizedOriginal {USER_PREFIX}/benchmark_scimark/{self.program}/{self.program}Optimized.java"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        source_path = f"{USER_PREFIX}/benchmark_scimark/{self.program}/{self.program}Optimized.java"
        with open(source_path, "r") as file:
            self.original_code = file.read()
        
    def get_original_code(self):
        return self.original_code
    
    def set_optimization_iteration(self, num):
        return super().set_optimization_iteration(num)

    def get_optimization_iteration(self):
        return super().get_optimization_iteration()

    def set_original_energy(self):
        logger.info("Run benchmark on the original code")

        # compile
        # Needed for makefiles
        problem_id = self.program.split('_')[0]
        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{problem_id}")  
        try: 
            result = subprocess.run(
                ["make", "compile"], 
                check=True,
                capture_output=True,
                text=True
            )
            self.compilation_error = result.stdout + result.stderr
            logger.info(f"Original code compile successfully.\n")
        except subprocess.CalledProcessError as e:
            logger.error(f"Original code compile failed: {e}\n")
            return False

        self._run_rapl(problem_id)

        avg_energy, avg_latency, avg_cpu_cycles, max_peak_memory, throughput = self._compute_avg()

        #Append results to benchmark data dict
        self.energy_data[0] = (self.original_code, round(avg_energy, 3), round(avg_latency, 3), len(self.original_code.splitlines()))
        logger.info(f"original_energy_data: {self.energy_data[0]}")
        return True

    def pre_process(self, code):
        ast = JavaAST("Java")
        source_code_path = f"{USER_PREFIX}/benchmark_scimark/{self.program}/{self.program}Optimized.java"
        with open(source_code_path, 'r') as file:
            code = file.read()
        return ast.create_ast(source_code_path)

    def post_process(self, code):
        code = code.replace("```java", "")
        code = code.replace("```", "")
        code = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL | re.MULTILINE)
        return code
        
    def compile(self, optimized_code):
        logger.info(f"llm_optimize: : writing optimized code to benchmark/{self.program}/{self.program}Optimized.java")
        destination_path = f"{USER_PREFIX}/benchmark_scimark/{self.program}/{self.program}Optimized.java"
        with open(destination_path, "w") as file:
            file.write(optimized_code)

        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{self.program}")
        try: 
            result = subprocess.run(
                ["make", "compile"], 
                check=True,
                capture_output=True,
                text=True
            )
            self.compilation_error = result.stdout + result.stderr
            logger.info(f"Optimized code compile successfully.\n")
        except subprocess.CalledProcessError as e:
            logger.error(f"Optimized code compile failed: {e}\n")
            return False
        return True
    
    def get_compilation_error(self):
        return super().get_compilation_error()  

    def run_tests(self):
        # Needed for makefiles
        # os.chdir(f"{USER_PREFIX}/benchmark_scimark/{self.program}")

        # if (self.expect_test_output == None):   
        #     self.expect_test_output = self._process_output_content(self._run_program(False))
        
        # optimized_output = self._run_program(True)

        # if not self._compare_outputs(optimized_output):
        #     return False
        # else:
        #     return True
        return True

    def measure_energy(self, optimized_code):            
        #load the optimized code and data
        logger.info(f"Iteration {self.optimization_iteration + 1}, run benchmark on the optimized code")
        
        problem_id = self.program.split('_')[0]
        self._run_rapl(problem_id)
    
        avg_energy, avg_latency, avg_cpu_cycles, max_peak_memory, throughput = self._compute_avg()
        
        #Append results to benchmark data dict
        self.energy_data[self.optimization_iteration + 1] = (optimized_code, round(avg_energy, 3), round(avg_latency, 3), len(optimized_code.splitlines()))
        
        # Find the required benchmark elements
        self.evaluator_feedback_data = self._extract_content(self.energy_data)
        
        # Print the benchmark information
        self._print_benchmark_info(self.evaluator_feedback_data)

    def get_energy_data(self):
        return super().get_energy_data()
    
    def get_evaluator_feedback_data(self):
        return super().get_evaluator_feedback_data()
    
    def static_analysis(self, optimized_code):
        return super().static_analysis(optimized_code)

    def _run_program(self, optimized, input_file):
        return "output"

    def _process_output_content(self, content):
        return "output"

    def _compare_outputs(self, optimized_output):
        return True

    

    def _run_rapl(self, problem_id):
        # First clear the contents of the energy data log file
        logger.info(f"Benchmark.run: clearing content in java.csv")
        log_file_path = f"{USER_PREFIX}/src/runtime_logs/java.csv"
        if os.path.exists(log_file_path):
            file = open(log_file_path, "w+")
            file.close()

        #run make measure using make file
        #change current directory to benchmarks/folder to run make file
        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{self.program.split('_')[0]}")
        current_dir = os.getcwd()
        logger.info(f"Current directory: {current_dir}")

        try:
            input_file = "input.0.txt"
            measure_unoptimized = ["make", "measure", f"input={input_file}", f"problem_id={problem_id}"]
            measure_optimized = ["make", "measure_optimized", f"input={input_file}", f"problem_id={problem_id}"]
            if (self.optimization_iteration == 0):
                subprocess.run(measure_unoptimized, check=True, capture_output=True, text=True)
            else:
                subprocess.run(measure_optimized, check=True, capture_output=True, text=True)
            logger.info("Benchmark.run: make measure successfully\n")
        except subprocess.CalledProcessError as e:
            logger.error(f"Benchmark.run: make measure failed: {e}\n")

    def _compute_avg(self):
        benchmark_data = []
        throughput = 0  # Initialize throughput variable
        with open(f'{USER_PREFIX}/src/runtime_logs/java.csv', mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            for index, row in enumerate(csv_reader):
                if index == 5:
                    throughput = row[1]
                else:
                    benchmark_name = row[0]
                    energy = row[1]
                    latency = row[2]
                    cpu_cycles = row[3]
                    peak_memory = row[4]
                    benchmark_data.append((benchmark_name, energy, latency, cpu_cycles, peak_memory))

        #Find average energy usage and average runtime
        avg_energy = 0
        avg_latency = 0
        avg_cpu_cycles = 0
        max_peak_memory = 0
        for data in benchmark_data:
            energy = float(data[1])
            if energy < 0:
                benchmark_data.remove(data)
            else:
                avg_energy += energy
                avg_latency += float(data[2])
                avg_cpu_cycles += float(data[3])
                max_peak_memory = max(max_peak_memory, float(data[4]))

        avg_energy /= len(benchmark_data)
        avg_latency /= len(benchmark_data)
        avg_cpu_cycles /= len(benchmark_data)

        return avg_energy, avg_latency, avg_cpu_cycles, max_peak_memory, float(throughput)
    
    def _extract_content(self, contents):
        # Convert keys to a sorted list to access the first and last elements
        keys = list(contents.keys())

        # print all values
        for key, (source_code, avg_energy, avg_runtime, num_of_lines) in contents.items():
            logger.info(f"key: {key}, avg_energy: {avg_energy}, avg_runtime: {avg_runtime}, num_of_lines: {num_of_lines}")

        # Extract the first(original) and last(current) elements
        first_key = keys[0]
        last_key = keys[-1]

        first_value = contents[first_key]
        last_value = contents[last_key]


        # Loop through the contents to find the key with the lowest avg_energy
        min_avg_energy = float('inf')
        min_energy_key = None
        for key, (source_code, avg_energy, avg_runtime, num_of_lines) in contents.items():
            if avg_energy < min_avg_energy:
                min_avg_energy = avg_energy
                min_energy_key = key

        min_value = contents[min_energy_key]

        # Prepare results in a structured format (dictionary)
        benchmark_info = {
            "original": {
                "source_code": first_value[0],
                "avg_energy": first_value[1],
                "avg_runtime": first_value[2],
                "num_of_lines": first_value[3]
            },
            "lowest_avg_energy": {
                "source_code": min_value[0],
                "avg_energy": min_value[1],
                "avg_runtime": min_value[2],
                "num_of_lines": min_value[3]
            },
            "current": {
                "source_code": last_value[0],
                "avg_energy": last_value[1],
                "avg_runtime": last_value[2],
                "num_of_lines": last_value[3]
            }
        }
        
        return benchmark_info
    
    def _print_benchmark_info(self, benchmark_info):
        logger.info("Original: Average Energy: {}, Average Runtime: {}".format(benchmark_info["original"]["avg_energy"], benchmark_info["original"]["avg_runtime"]))
        logger.info("Lowest Average Energy: Average Energy: {}, Average Runtime: {}".format(benchmark_info["lowest_avg_energy"]["avg_energy"], benchmark_info["lowest_avg_energy"]["avg_runtime"]))
        logger.info("Current: Average Energy: {}, Average Runtime: {}".format(benchmark_info["current"]["avg_energy"], benchmark_info["current"]["avg_runtime"]))


def get_valid_scimark_programs():
    valid_programs = [
        "FFT",
        "LU",
        "MonteCarlo",
        "SOR",
        "SparseMatmult"
    ]
    return valid_programs