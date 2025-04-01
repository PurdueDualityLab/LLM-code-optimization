from benchmark import Benchmark
import os
import subprocess
import sys
from dotenv import load_dotenv
from abstract_syntax_trees.java_ast import JavaAST
from status import Status
from utils import Logger
import csv
import re
from dacapo_profiling import get_hotspots
from collections import defaultdict

load_dotenv()
USER_PREFIX = os.path.expanduser(os.getenv('USER_PREFIX'))


logger = Logger("logs", sys.argv[2]).logger

class DaCapoBenchmark(Benchmark):

    def __init__(self, test_method, test_class, test_group, benchmark_name):

        # ex. test_method = PDFNumsArray, test_class = pdf, test_group = core, benchmark_name = fop

        self.method_name = test_method
        self.class_name = test_class
        self.group_name = test_group
        self.program = benchmark_name
        self.compilation_error = None
        self.energy_data = {}
        self.evaluator_feedback_data = {}
        self.expect_test_output = None
        self.original_code = None
        self.optimization_iteration = 0
        self.set_original_code()
        
    def set_original_code(self):

        if self.program == 'fop':
            source_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-{self.group_name}/src/main/java/org/apache/{self.program}/{self.class_name}/{self.method_name}.java"
        elif self.program == 'spring':
            source_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/src/main/java/org/springframework/samples/petclinic/{self.class_name}/{self.method_name}.java"
        elif self.program == 'biojava':
            source_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/biojava-{self.group_name}/src/main/java/org/biojava/nbio/{self.group_name}/{self.class_name}/{self.method_name}.java"



        #the above path still is not general enough for all bms, apache only works for fop and 2.8 is only for fop

        with open(source_path, 'r') as file:
            code = file.read() 
        filtered_code = re.sub(r'\s*//.*?$|/\*[\s\S]*?\*/\s*', '', code, flags=re.MULTILINE)
        self.original_code = filtered_code
        
    def get_original_code(self):
        return self.original_code
    
    def set_original_energy(self):
        logger.info("Run benchmark on the original code")

        # compile
        # Needed for makefiles
        if self.program == 'fop':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-{self.group_name}/")
        elif self.program == 'spring':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/")
        elif self.program == 'biojava':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/biojava-{self.group_name}/")

        try:
            result = subprocess.run(["make", "compile", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.method_name}", f"TEST_FOLDER={self.group_name}"], check=True, capture_output=True, text=True)
            logger.info("Original code compile successfully.\n")
            self.compilation_error = result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            print(e.stderr + e.stdout)
            logger.error(f"Original code compile failed: {e}\n")
            return False
        
        #run make measure using make file for same test class
        if not self._run_rapl():
            return False

        #compute avg energy and avg runtime
        avg_energy, avg_latency, avg_cpu_cycles, avg_memory, throughput = self._compute_avg()

        self.energy_data[0] = (self.original_code, round(avg_energy, 3), round(avg_latency, 3),  avg_cpu_cycles, avg_memory, round(throughput, 3), len(self.original_code.splitlines()))        
        return True
    
    def pre_process(self, code):
        ast = JavaAST("java")
        return ast.create_ast(code)
    
    def post_process(self, code):
        code = code.replace("```java", "")
        code = code.replace("```", "")
        filtered_code = re.sub(r'\s*//.*?$|/\*[\s\S]*?\*/\s*', '', code, flags=re.MULTILINE)
        return filtered_code

    def compile(self, optimized_code):
        #write optimized code to file

        if self.program == 'fop':
            destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-{self.group_name}/src/main/java/org/apache/{self.program}/{self.class_name}/{self.method_name}.java"
        elif self.program == 'spring':
            destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/src/main/java/org/springframework/samples/petclinic/{self.class_name}/{self.method_name}.java"
        elif self.program == 'biojava':
            destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/biojava-{self.group_name}/src/main/java/org/biojava/nbio/{self.group_name}/{self.class_name}/{self.method_name}.java"
        
        with open(destination_path, "w") as file:
            file.write(optimized_code)

        #compile optimized code
        if self.program == 'fop':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/fop/build/fop-2.8/fop-{self.group_name}")
        elif self.program == 'spring':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/spring/build")
        elif self.program == 'biojava':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/biojava/build/biojava-{self.group_name}") 

        try:
            result = subprocess.run(
                ["make", "compile", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.method_name}", f"TEST_FOLDER={self.group_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            logger.info(f"Optimized code compile successfully.\n")
            return True
        except subprocess.CalledProcessError as e:
            self.compilation_error = e.stdout + e.stderr  # Capture both stdout and stderr
            print(e.stderr + e.stdout)
            logger.error(f"Compile optimized code failed: {e}\n")
            logger.error(f"Maven output: {self.compilation_error}")
            return False
        

    def get_compilation_error(self):
        return super().get_compilation_error()
    
    def run_tests(self):

        if self.program == 'fop':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/fop/build/fop-2.8/fop-{self.group_name}")
        elif self.program == 'spring':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/spring/build")
        elif self.program == 'biojava':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/biojava/build/biojava-{self.group_name}")

        try:
            # Using subprocess.PIPE allows us to capture both stdout and stderr
            result = subprocess.run(
                ["make", "test", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.method_name}", f"TEST_FOLDER={self.group_name}"],
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
         #load the optimized code and data
        logger.info(f"Iteration {self.optimization_iteration + 1}, run benchmark on the optimized code")
        self._run_rapl()

        avg_energy, avg_latency, avg_cpu_cycles, avg_memory, throughput = self._compute_avg()
        original_data = self.energy_data[0]
        energy_change = original_data[1] / avg_energy
        speedup = original_data[2] / avg_latency
        cpu_change = original_data[3] / avg_cpu_cycles
        memory_change = original_data[4] / avg_memory
        throughput_change = throughput / original_data[5]

        self.energy_data[self.optimization_iteration + 1] = (optimized_code, round(energy_change, 3), round(speedup, 3), cpu_change, memory_change, throughput_change, len(optimized_code.splitlines()))

        self.evaluator_feedback_data = self._extract_content(self.energy_data)   
        return True

    def _run_rapl(self):
        # First clear the contents of the energy data log file
        logger.info(f"Benchmark.run: clearing content in java.csv")
        log_file_path = f"{USER_PREFIX}/src/runtime_logs/java.csv"
        if os.path.exists(log_file_path):
            file = open(log_file_path, "w")
            file.close()

        #run make measure using make file
        if self.program == 'fop':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/fop/build/fop-2.8/fop-{self.group_name}")
        elif self.program == 'spring':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/spring/build")
        elif self.program == 'biojava':
            os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/biojava/build/biojava-{self.group_name}")

        try:
            result = subprocess.run(["make", "measure", f"BENCHMARK={self.program}", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.method_name}", f"TEST_FOLDER={self.group_name}"], check=True, capture_output=True, text=True, timeout=120)
            logger.info("Original code compile successfully.\n")
            logger.info(result.stdout)
            return True
        except subprocess.TimeoutExpired:
            logger.error("Make measure timeout")
            return False
        except subprocess.CalledProcessError as e:
            print(e.stderr + e.stdout)
            logger.error(f"Make measure failed: {e}\n")
            #to get the error message, might have to return the error message from here
            return False
    
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
        avg_memory = 0
        for data in benchmark_data:
            energy = float(data[1])
            if energy < 0:
                benchmark_data.remove(data)
            else:
                avg_energy += energy
                avg_latency += float(data[2])
                avg_cpu_cycles += float(data[3])
                avg_memory += float(data[4])

        avg_energy /= len(benchmark_data)
        avg_latency /= len(benchmark_data)
        avg_cpu_cycles /= len(benchmark_data)
        avg_memory /= len(benchmark_data)

        return avg_energy, avg_latency, avg_cpu_cycles, avg_memory, float(throughput)
        
    def get_evaluator_feedback_data(self):
        return super().get_evaluator_feedback_data()
    
    def static_analysis(self, optimized_code):

        if self.program == 'fop':
            destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-{self.group_name}/src/main/java/org/apache/{self.program}/{self.class_name}/{self.method_name}.java"
        elif self.program == 'spring':
            destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/src/main/java/org/springframework/samples/petclinic/{self.class_name}/{self.method_name}.java"
        elif self.program == 'biojava':
            destination_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/biojava-{self.group_name}/src/main/java/org/biojava/nbio/{self.group_name}/{self.class_name}/{self.method_name}.java"

        def restore_original():
            with open(destination_path, "w") as file:
                file.write(self.original_code)

        try:
            if not self.compile(optimized_code):
                return Status.COMPILATION_ERROR
            if not self.run_tests():
                return Status.RUNTIME_ERROR_OR_TEST_FAILED 
            if not self.measure_energy(optimized_code):
                return Status.ALL_TEST_PASSED
            return Status.PERFORMANCE_IMPROVED
        finally:
            restore_original()
        
    def _extract_content(self, contents):
        # Convert keys to a sorted list to access the first and last elements
        keys = list(contents.keys())

        # Extract the first(original) and last(current) elements
        first_key = keys[0]
        last_key = keys[-1]

        first_value = contents[first_key]
        last_value = contents[last_key]
        
        # print all values
        logger.info(f"key 0, avg_energy: {first_value[1]}, avg_runtime: {first_value[2]}, avg_cpu_cycles: {first_value[3]}, avg_memory: {first_value[4]}, throughput: {first_value[5]}, num_of_lines: {first_value[6]}")
        for key, (source_code, avg_energy, avg_runtime, avg_cpu_cycles, avg_memory, throughput, num_of_lines) in list(contents.items())[1:]:
            logger.info(f"key: {key}, avg_energy_improvement: {avg_energy}, avg_speedup: {avg_runtime}, avg_cpu_improvement: {avg_cpu_cycles}, avg_memory_improvement: {avg_memory}, avg_throughput_improvement: {throughput}, num_of_lines: {num_of_lines}")
            

       # Loop through the contents to find the key with the highest speedup
        max_avg_speedup = float('-inf')
        max_avg_speedup_key = None
        for key, (source_code, avg_energy, avg_speedup, avg_cpu_cycles, avg_memory, throughput, num_of_lines) in list(contents.items())[1:]:
            if avg_speedup > max_avg_speedup:
                max_avg_speedup = avg_speedup
                max_avg_speedup_key = key

        max_value = contents[max_avg_speedup_key]

        # Prepare results in a structured format (dictionary)
        benchmark_info = {
            "original": {
                "source_code": first_value[0],
                "avg_energy": first_value[1],
                "avg_runtime": first_value[2],
                "avg_cpu_cycles": first_value[3],
                "avg_memory": first_value[4],
                "throughput": first_value[5],
                "num_of_lines": first_value[6]
            },
            "max_avg_speedup": {
                "source_code": max_value[0],
                "avg_energy_improvement": max_value[1],
                "avg_speedup": max_value[2],
                "avg_cpu_improvement": max_value[3],
                "avg_memory_improvement": max_value[4],
                "avg_throughput_improvement": max_value[5],
                "num_of_lines": max_value[6]
            },
            "current": {
                "source_code": last_value[0],
                "avg_energy_improvement": last_value[1],
                "avg_speedup": last_value[2],
                "avg_cpu_improvement": last_value[3],
                "avg_memory_improvement": last_value[4],
                "avg_throughput_improvement": last_value[5],
                "num_of_lines": last_value[6]
            }
        }
        
        return benchmark_info

def get_valid_dacapo_classes(application_name):
    hotspots = get_hotspots(application_name, top_K=5)
    methods_name = list(hotspots.keys())

    transformed_data = defaultdict(list)
    
    for method in methods_name:
        parts = method.split('/')
        class_name, method_name = parts[-1].split('.')  # Split the last part into class and method
        
        group_name = parts[3] #hardcode for fop e.g. org/apache/fop/cli/Main.startFOP
        
        transformed_data[application_name].append((group_name, class_name, method_name))
    
    benchmark_classes = dict(transformed_data)

    # benchmark_classes = {'fop': [('pdf','PDFNumsArray'), ('pdf','PDFRoot'), ('pdf','PDFFactory'), ('pdf','PDFDocument'), ('pdf','PDFPage'), ('pdf','PDFPageSequence'), ('pdf','PDFPageSequence.PagePosition'), ('pdf','PDFPageSequence.PagePosition.PagePositionComparator'), ('pdf','PDFPageSequence.PagePosition.PagePositionComparator.PagePositionComparator'), ('pdf','PDFPageSequence.PagePosition.PagePositionComparator.PagePositionComparator.PagePositionComparator')]
    #                     #spring:[],
    # spring':[('owner','OwnerController')]
    # DaCapoBenchmark('OwnerController', 'owner', 'spring')
    #                     #biojava:[],
    #                     }

    setup_makefile(application_name)
    return benchmark_classes[application_name]

def setup_makefile(application_name):

    if application_name == 'fop':
        folder_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{application_name}/build/fop-2.8"
        subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
    elif application_name == 'spring':
        folder_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{application_name}"
        subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir() and f.name == 'build']
    elif application_name == 'biojava':
        folder_path = f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{application_name}/build"
        subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir() and f.name.startswith('biojava-')]

    for subfolder in subfolders:
        print(subfolder)
        makefile_template = open(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/makefile_template.mak", "r")
        makefile_content = makefile_template.read()
        makefile_template.close()
        makefile_template = open(f"{subfolder}/Makefile", "w")
        makefile_template.write(makefile_content)
        makefile_template.close()
    
    

#just to test the code
def main():


    # ff = DaCapoBenchmark('PDFNumsArray', 'pdf', 'core', 'fop')
    # ff.set_original_energy()
    # status = ff.static_analysis(ff.original_code)
    # print(f"Status: {status}")
    # ff = DaCapoBenchmark('OwnerController', 'owner', 'none', 'spring')
    # ff.set_original_energy()

    # setup_makefile('spring')
    # ff.static_analysis(ff.original_code)

    ff = DaCapoBenchmark('ChromosomeSequence', 'sequence', 'core', 'biojava')
    setup_makefile('biojava')
    ff.set_original_energy()
    status = ff.static_analysis(ff.original_code)


if __name__ == '__main__':
    main()