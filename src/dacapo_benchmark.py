from benchmark import Benchmark
import os
import subprocess
import sys
from dotenv import load_dotenv
from abstract_syntax_trees.java_ast import JavaAST
from status import Status
from utils import Logger

load_dotenv()
# USER_PREFIX = os.getenv('USER_PREFIX')
USER_PREFIX = os.path.expanduser(os.getenv('USER_PREFIX'))


# logger = Logger("logs", sys.argv[2]).logger

class DaCapoBenchmark(Benchmark):

    def __init__(self, test_class, test_group, benchmark_name):
        # ex. test_class = PDFNumsArray, test_group = pdf, benchmark_name = fop
        self.test_name = test_class
        self.class_name = test_group
        self.program = benchmark_name
        self.compilation_error = None
        self.energy_data = {}
        self.evaluator_feedback_data = {}
        self.expect_test_output = None
        self.original_code = None
        self.optimization_iteration = 0
        self.set_original_code()
        

    
    def set_original_code(self):
        source_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/src/main/java/org/apache/{self.program}/{self.class_name}/{self.test_name}.java"
        #the above path still is not general enough for all bms, apache only works for fop and 2.8 is only for fop

        with open(source_path, 'r') as file:
            self.original_code = file.read() 
        
    def get_original_code(self):
        return self.original_code
    
    def set_original_energy(self):
        # logger.info("Run benchmark on the original code")

        # compile
        # Needed for makefiles
        # os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/")
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/")
        print(os.getcwd())

        try:
            result = subprocess.run(["make", "compile", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"], check=True, capture_output=True, text=True)
            # logger.info("Original code compile successfully.\n")
            print(result.stdout)
            self.compilation_error = result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            # logger.error(f"Original code compile failed: {e}\n")
            print(f"Original code compile failed: {e}\n") 
            print(e.stderr + e.stdout)
            return False
        
        #run make measure using make file for same test class
        if not self._run_rapl(optimized=False):
            return False

        #compute avg energy and avg runtime
        avg_energy, avg_runtime = self._compute_avg()
        self.energy_data[0] = (self.original_code, round(avg_energy, 3), round(avg_runtime, 3), len(self.original_code.splitlines()))
        # logger.info(f"original_energy_data: {self.energy_data[0]}")
        print(f"original_energy_data: {self.energy_data[0]}")
        
        return True
    
    def pre_process(self, code):
        ast = JavaAST("java")
        # Create temp directory if it doesn't exist
        temp_dir = f"{USER_PREFIX}/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Use temp directory for AST file
        source_code_path = f"{temp_dir}/ast_{self.test_name}.java"
        
        with open(source_code_path, 'w') as file:
            file.write(code)
        return ast.create_ast(source_code_path)
    
    def post_process(self, code):
        code = code.replace("```java", "")
        code = code.replace("```", "")
        return code

    def compile(self, optimized_code):
        #write optimized code to file
        destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/src/main/java/org/apache/{self.program}/{self.class_name}/{self.test_name}.java"
        with open(destination_path, "w") as file:
            file.write(optimized_code)

        #compile optimized code
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/")
        print(os.getcwd())

        try:
            result = subprocess.run(
                ["make", "compile", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.compilation_error = e.stdout + e.stderr  # Capture both stdout and stderr
            print(f"Compile optimized code failed: {e}\n")
            print(f"Maven output: {self.compilation_error}")
            return False
        

    def get_compilation_error(self):
        return super().get_compilation_error()
    
    def run_tests(self):
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/")

        try:
            # Using subprocess.PIPE allows us to capture both stdout and stderr
            result = subprocess.run(
                ["make", "test", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='latin-1'
            )
            
            # Check if the command failed (non-zero return code)
            if result.returncode != 0:
                print(f"Test failed with error:\nstdout: {result.stdout}\nstderr: {result.stderr}")
                return False
            
            print(f"Test output:\n{result.stdout}")

            #check if all tests pass
            #is this the right way to check if all tests pass?
            if "BUILD FAILURE" in result.stdout:
                return False
            else:
                return True
            
        except subprocess.CalledProcessError as e:
            print(f"Test execution failed: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")
            return False
        
    def measure_energy(self, optimized_code):
        
        self._run_rapl()

        avg_energy, avg_runtime = self._compute_avg()
        self.energy_data[self.optimization_iteration + 1] = (optimized_code, round(avg_energy, 3), round(avg_runtime, 3), len(optimized_code.splitlines()))

        self.evaluator_feedback_data = self._extract_content(self.energy_data)


        self._print_benchmark_info(self.evaluator_feedback_data)
        
        return True

    def _run_rapl(self, optimized):

        # First clear the contents of the energy data log file
        # logger.info(f"Benchmark.run: clearing content in c++.csv")
        log_file_path = f"{USER_PREFIX}/src/runtime_logs/java.csv"
        if os.path.exists(log_file_path):
            file = open(log_file_path, "w")
            file.close()

        #run make measure using make file
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/")
        print(os.getcwd())

        try:
            result = subprocess.run(["make", "measure", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"], check=True, capture_output=True, text=True)
            # logger.info("Original code compile successfully.\n")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Make measure failed: {e}\n")
            #to get the error message, might have to return the error message from here
            return False
    

    def _compute_avg(self):
        energy_data_file = open(f"{USER_PREFIX}/src/runtime_logs/java.csv", "r")
        benchmark_data = []
        for line in energy_data_file:
            if line.startswith("Throughput"):
                continue
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
        
    def get_evaluator_feedback_data(self):
        return super().get_evaluator_feedback_data()
    
    def static_analysis(self, optimized_code):
        destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/src/main/java/org/apache/{self.program}/{self.class_name}/{self.test_name}.java"

        def restore_original():
            with open(destination_path, "w") as file:
                file.write(self.original_code)

        try:
            if not self.compile(optimized_code):
                print(f"Compile failed: {self.compilation_error}")
                return Status.COMPILATION_ERROR
            if not self.run_tests():
                print(f"Test failed: {self.test_output}")
                return Status.RUNTIME_ERROR_OR_TEST_FAILED 
            if not self.measure_energy(optimized_code):
                return Status.ALL_TEST_PASSED
            return Status.PERFORMANCE_IMPROVED
        finally:
            restore_original()
        
    def _extract_content(self, contents):
        keys = list(contents.keys())

        # print all values
        for key, (source_code, avg_energy, avg_runtime, num_of_lines) in contents.items():
            # logger.info(f"key: {key}, avg_energy: {avg_energy}, avg_runtime: {avg_runtime}, num_of_lines: {num_of_lines}")
            print(f"key: {key}, avg_energy: {avg_energy}, avg_runtime: {avg_runtime}, num_of_lines: {num_of_lines}")

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
        pass
        # logger.info("Original: Average Energy: {}, Average Runtime: {}".format(benchmark_info["original"]["avg_energy"], benchmark_info["original"]["avg_runtime"]))
        # logger.info("Lowest Average Energy: Average Energy: {}, Average Runtime: {}".format(benchmark_info["lowest_avg_energy"]["avg_energy"], benchmark_info["lowest_avg_energy"]["avg_runtime"]))
        # logger.info("Current: Average Energy: {}, Average Runtime: {}".format(benchmark_info["current"]["avg_energy"], benchmark_info["current"]["avg_runtime"]))
    
def get_valid_dacapo_programs(application_name):
    '''
    Temporary solution: hardcode a list of 10 classe names from this application
    '''
    benchmark_classes = {'fop': [('pdf','PDFNumsArray'), ('pdf','PDFRoot'), ('pdf','PDFFactory'), ('pdf','PDFDocument'), ('pdf','PDFPage'), ('pdf','PDFPageSequence'), ('pdf','PDFPageSequence.PagePosition'), ('pdf','PDFPageSequence.PagePosition.PagePositionComparator'), ('pdf','PDFPageSequence.PagePosition.PagePositionComparator.PagePositionComparator'), ('pdf','PDFPageSequence.PagePosition.PagePositionComparator.PagePositionComparator.PagePositionComparator')]
                        #spring:[],
                        #biojava:[],
                        }

    return benchmark_classes[application_name]

#just to test the code
# def main():


#     ff = DaCapoBenchmark('PDFNumsArray', 'pdf', 'fop')
#     ff.set_original_energy()
#     # status = ff.static_analysis(ff.original_code)
#     # print(f"Status: {status}")

# if __name__ == '__main__':
#     main()