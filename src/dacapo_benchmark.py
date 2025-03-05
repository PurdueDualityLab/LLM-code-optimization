from benchmark import Benchmark
import os
import subprocess
import sys
from utils import Logger
from dotenv import load_dotenv
from utils import Logger

load_dotenv()
# USER_PREFIX = os.getenv('USER_PREFIX')
USER_PREFIX = os.path.expanduser(os.getenv('USER_PREFIX'))


# logger = Logger("logs", sys.argv[2]).logger

class DaCapoBenchmark(Benchmark):

    def __init__(self, program):
        self.program = program
        self.compilation_error = None
        self.energy_data = {}
        self.evaluator_feedback_data = {}
        self.expect_test_output = None
        self.original_code = None
        self.optimization_iteration = 0
        self.set_original_code()

    def set_original_energy(self):
        # logger.info("Run benchmark on the original code")

        # print(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program.split('.')[0].split('_')[-1]}")
        # os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program.split('.')[0].split('_')[-1]}")  

        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/")  
        # get current directory
        current_dir = os.getcwd()
        print(f"Current directory: {current_dir}")
        try: 
            result = subprocess.run(
                ["make", "compile", f"BENCHMARK={self.program}"], 
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            self.compilation_error = result.stdout + result.stderr
            # logger.info(f"Original code compile successfully.\n")
        except subprocess.CalledProcessError as e:
            # logger.error(f"Original code compile failed: {e}\n")
            print(f"Original code compile failed: {e}\n")
            return False

        self._run_rapl()

        avg_energy, avg_runtime = self._compute_avg()

        #Append results to benchmark data dict
        self.energy_data[0] = (self.original_code, round(avg_energy, 3), round(avg_runtime, 3), len(self.original_code.splitlines()))
        # logger.info(f"original_energy_data: {self.energy_data[0]}")
        print(f"original_energy_data: {self.energy_data[0]}")
        return True



    def set_original_code(self):
        # capitalize first letter of program name
        file_name = self.program.capitalize()
        source_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/harness/src/org/dacapo/harness/{file_name}.java"
        with open(source_path, 'r') as file:
            self.original_code = file.read()

    def _run_rapl(self):
        # First clear the contents of the energy data log file
        # logger.info(f"Benchmark.run: clearing content in c++.csv")
        # log_file_path = f"{USER_PREFIX}/src/runtime_logs/java/Java.csv"
        # if os.path.exists(log_file_path):

        #     file = open(log_file_path, "w+")
        #     file.close()

        #run make measure using make file
        #change current directory to benchmarks/folder to run make file
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/")
        current_dir = os.getcwd()
        # logger.info(f"Current directory: {current_dir}")

        try:
            if (self.optimization_iteration == 0):
                result = subprocess.run(["make", "measure", f"BENCHMARK={self.program}"], check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(["make", "measure_optimized", f"BENCHMARK={self.program}"], check=True, capture_output=True, text=True)
            
            # logger.info("Benchmark.run: make measure successfully\n")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            # logger.error(f"Benchmark.run: make measure failed: {e}\n")
            print(f"Benchmark.run: make measure failed: {e}\n")

    def _compute_avg(self):
        energy_data_file = open(f"{USER_PREFIX}/src/runtime_logs/java/Java.csv", "r")
        benchmark_data = []
        for line in energy_data_file:
            parts = line.split(';')
            benchmark_name = parts[0].strip()
            energy_data = [vals.strip() for vals in parts[1].split(',')]
            
            #Remove empty strings for CPU, GPU, DRAM and convert remaining numbers to floats
            energy_data = [float(num) for num in energy_data if num]
            benchmark_data.append((benchmark_name, *energy_data))

        energy_data_file.close()

        #Find average energy usage and average runtime
        avg_energy = 0
        avg_runtime = 0
        for data in benchmark_data:
            if data[1] < 0 or data[2] < 0:
                benchmark_data.remove(data)
            else:
                avg_energy += data[1]
                avg_runtime += data[2]

        avg_energy /= len(benchmark_data)
        avg_runtime /= len(benchmark_data)

        return avg_energy, avg_runtime
        
def get_valid_dacapo_programs(application_name):
    '''
    Temporary solution: hardcode a list of 10 classe names from this application
    '''
    return []


def main():


    ff = DaCapoBenchmark('fop')
    
    ff.set_original_code()
    ff.set_original_energy()

if __name__ == '__main__':
    main()