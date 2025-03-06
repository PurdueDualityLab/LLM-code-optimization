from benchmark import Benchmark
import os
import subprocess
import sys
from dotenv import load_dotenv
# from utils import Logger

load_dotenv()
# USER_PREFIX = os.getenv('USER_PREFIX')
USER_PREFIX = os.path.expanduser(os.getenv('USER_PREFIX'))


# logger = Logger("logs", sys.argv[2]).logger

class DaCapoBenchmark(Benchmark):

    def __init__(self, test_name, class_name, benchmark_name):
        #ex. test_name = PDFNumsArray, class_name = pdf, program = fop
        self.test_name = test_name
        self.class_name = class_name
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
    
    def set_optimization_iteration(self, num):
        return super().set_optimization_iteration(num)
    
    def get_optimization_iteration(self):
        return super().get_optimization_iteration()
    
    def set_original_energy(self):
        # logger.info("Run benchmark on the original code")

        # compile
        # Needed for makefiles
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/")
        print(os.getcwd())

        try:
            result = subprocess.run(["make", "compile", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"], check=True, capture_output=True, text=True)
            # logger.info("Original code compile successfully.\n")
            print(result.stdout)
            self.compilation_error = result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            # logger.error(f"Original code compile failed: {e}\n")
            return False
        
        #run make measure using make file for same test class
        if not self._run_rapl():
            return False

        #compute avg energy and avg runtime
        avg_energy, avg_runtime = self._compute_avg()
        self.energy_data[0] = (self.original_code, round(avg_energy, 3), round(avg_runtime, 3), len(self.original_code.splitlines()))
        # logger.info(f"original_energy_data: {self.energy_data[0]}")
        print(f"original_energy_data: {self.energy_data[0]}")
        
        return True
    
    def pre_process(self, code):
        #java ast does not exist
        pass
    
    def post_process(self, code):
        #java ast does not exist
        pass

    def compile(self, optimized_code):
        #not sure if this is needed since it doesnt get called in main
        pass

    def get_compilation_error(self):
        return super().get_compilation_error()
    
    def run_tests(self):

        #make sure all tests pass
        #run tests
        #return true if all tests pass, false otherwise

        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/")
        print(os.getcwd())

        try:
            result = subprocess.run(["make", "run", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"], check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Make run failed: {e}\n")
            return False
     
    
        

    def _run_rapl(self):

        # First clear the contents of the energy data log file
        # logger.info(f"Benchmark.run: clearing content in c++.csv")
        log_file_path = f"{USER_PREFIX}/src/runtime_logs/java.csv"
        if os.path.exists(log_file_path):
            file = open(log_file_path, "w")
            file.close()

        #run make measure using make file
        os.chdir(f"{USER_PREFIX}/benchmark_dacapo/benchmarks/bms/{self.program}/build/{self.program}-2.8/{self.program}-core/")
        print(os.getcwd())

        try:
            if (self.optimization_iteration == 0):
                result = subprocess.run(["make", "measure", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"], check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(["make", "measure_optimized", f"TEST_GROUP={self.class_name}", f"TEST_CLASS={self.test_name}"], check=True, capture_output=True, text=True)
            # logger.info("Original code compile successfully.\n")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Make measure failed: {e}\n")
            #to get the error message, might have to return the error message from here
            return False
        
        return True

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
        
def get_valid_classes():

    benchmark_classes = {'fop': {'pdf': ['PDFNumsArrayTestCase']},
                        # 'biojava': {'bio': ['BiojavaBenchmark']},
                        # 'spring': {'spring': ['SpringBenchmark']}
                         } 

    return benchmark_classes

    
def get_valid_dacapo_programs(application_name):
    '''
    Temporary solution: hardcode a list of 10 classe names from this application
    '''
    return []


def main():


    ff = DaCapoBenchmark('PDFNumsArray', 'pdf', 'fop')
    
    ff.set_original_code()
    ff.set_original_energy()

if __name__ == '__main__':
    main()