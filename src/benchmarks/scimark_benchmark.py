from benchmarks.benchmark import Benchmark
from dotenv import load_dotenv
import os
import subprocess
import sys
import re
import csv
import math
from utils import Logger
from abstract_syntax_trees.java_ast import JavaAST
from flamegraph_profiling import get_hotspots
from java_method_profiling import replace_method_body, get_method_source_code, compile_java_project

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
logger = Logger("logs", sys.argv[2]).logger

class SciMarkBenchmark(Benchmark):
    def __init__(self, program, method_name, method_level):
        self.program = program
        self.method_name = method_name
        self.method_level = method_level

        self.compilation_error = None
        self.runtime_error = None
        self.energy_data = {}
        self.evaluator_feedback_data = {}
        self.expect_test_output = None
        self.original_code = None
        self.optimization_iteration = 0

        self.set_original_code()

    def set_original_code(self):
        src_path = f"{USER_PREFIX}/benchmark_scimark/{self.program}"
        subprocess.run(f"cp {src_path}/{self.program}OptimizedOriginal {src_path}/{self.program}Optimized.java", shell=True)
        source_file = f"{src_path}/{self.program}Optimized.java"

        if self.method_level:
            compile_java_project()
            self.original_code = get_method_source_code(source_file, self.method_name)
        else:
            with open(source_file, "r") as file:
                self.original_code = file.read()

    def get_original_code(self):
        return self.original_code

    def pre_process(self, code):
        return JavaAST("Java").create_ast(code)

    def post_process(self, code):
        code_block = re.search(r'```java\s*(.*?)```', code, re.DOTALL)
        code = code_block.group(1) if code_block else code
        code = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL | re.MULTILINE)
        code = re.sub(r'\bclass\s+\w+', f'class {self.program}Optimized', code)
        return f"package jnt.scimark2;\n{code}" if not code.strip().startswith("package") else code

    def compile(self, optimized_code):
        dest_path = f"{USER_PREFIX}/benchmark_scimark/{self.program}/{self.program}Optimized.java"
        if self.method_level:
            with open(f"{USER_PREFIX}/src/runtime_logs/optimized_java.txt", "w") as f:
                f.write(optimized_code)
            if not replace_method_body(dest_path, self.method_name):
                self.compilation_error = "Please provide Java code in the original method format"
                return False
        else:
            with open(dest_path, "w") as f:
                f.write(optimized_code)

        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{self.program}")
        try:
            subprocess.run(["make", "compile"], check=True, capture_output=True, text=True)
            self.compilation_error = None
            return True
        except subprocess.CalledProcessError as e:
            self.compilation_error = e.stderr
            logger.error(f"Compile failed: {self.compilation_error}")
            return False

    def run_tests(self):
        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{self.program}")
        if self.expect_test_output is None:
            self.expect_test_output = self._process_output_content(self._run_program(False))
        optimized_output = self._run_program(True)
        return self._compare_outputs(optimized_output)

    def measure_energy(self, optimized_code):
        mflops = self._measure_mflops("measure_mflops_optimized")
        self._run_rapl(True)

        avg_energy, avg_latency, avg_cpu_cycles, avg_memory, throughput = self._compute_avg()
        orig = self.energy_data[0]

        metrics = (
            optimized_code,
            round(orig[1] / avg_energy, 3),
            round(orig[2] / avg_latency, 3),
            orig[3] / avg_cpu_cycles,
            orig[4] / avg_memory,
            throughput / orig[5],
            float(mflops) / float(orig[6]),
            len(optimized_code.splitlines())
        )
        self.energy_data[self.optimization_iteration + 1] = metrics
        self.evaluator_feedback_data = self._extract_content(self.energy_data)

    def _measure_mflops(self, target):
        try:
            result = subprocess.run(["make", target], check=True, capture_output=True, text=True, timeout=180)
            return "\n".join(
                line for line in result.stdout.splitlines()
                if not line.startswith("make[") and not line.startswith("./")
            ).split("make")[0].strip()
        except Exception as e:
            logger.error(f"mflops measure failed: {e}")
            return 0

    def _run_program(self, optimized):
        try:
            cmd = ["make", "run_optimized"] if optimized else ["make", "run"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin-1', timeout=120)
            if result.returncode != 0:
                self.runtime_error = result.stderr
                return None
            return "\n".join(
                line for line in result.stdout.splitlines()
                if not line.startswith("make[") and not line.startswith("./")
            ).split("make")[0].strip()
        except subprocess.TimeoutExpired:
            logger.error("Run timeout")
            return None

    def _compare_outputs(self, output):
        output = self._process_output_content(output)
        try:
            float_out = float(output)
            float_ref = float(self._process_output_content(self.expect_test_output))
        except ValueError:
            self.runtime_error = f"Cannot parse output: {output}"
            return False

        eps = {
            "FFT": 1e-10,
            "LU": 1e-12,
            "MonteCarlo": math.pi,
            "SOR": 0.003,
            "SparseCompRow": 1e-10
        }[self.program]

        if self.program == "MonteCarlo":
            return abs(float_out - eps) <= 0.05
        return abs(float_out) <= eps

    def _process_output_content(self, content):
        if isinstance(content, list):
            content = ''.join(content)
        return re.sub(r'\s+', '', content) if isinstance(content, str) else content

    def _run_rapl(self, optimized):
        open(f"{USER_PREFIX}/src/runtime_logs/java.csv", "w").close()
        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{self.program}")
        try:
            subprocess.run(["sudo", "make", "measure_optimized" if optimized else "measure"], check=True, capture_output=True, text=True, timeout=180)
            return True
        except Exception as e:
            logger.error(f"RAPL measurement failed: {e}")
            return False

    def _compute_avg(self):
        path = f"{USER_PREFIX}/src/runtime_logs/java.csv"
        with open(path, "r") as file:
            reader = csv.reader(file)
            data, throughput = [], 0
            for idx, row in enumerate(reader):
                if idx == 5:
                    throughput = float(row[1])
                else:
                    try:
                        energy, latency, cpu, mem = map(float, row[1:5])
                        if energy >= 0:
                            data.append((energy, latency, cpu, mem))
                    except ValueError:
                        continue

        if not data:
            return 0, 0, 0, 0, 0

        sums = list(map(sum, zip(*data)))
        count = len(data)
        return *(val / count for val in sums), throughput

    def _extract_content(self, contents):
        first_val = contents[0]
        last_val = contents[max(contents.keys())]
        max_key = max(contents.items(), key=lambda x: x[1][2])[0]
        max_val = contents[max_key]

        keys = ["source_code", "avg_energy", "avg_runtime", "avg_cpu_cycles", "avg_memory", "throughput", "mflops", "num_of_lines"]
        imp_keys = ["source_code", "avg_energy_improvement", "avg_speedup", "avg_cpu_improvement", "avg_memory_improvement", "avg_throughput_improvement", "mflops_improvement", "num_of_lines"]

        return {
            "original": dict(zip(keys, first_val)),
            "max_avg_speedup": dict(zip(imp_keys, max_val)),
            "current": dict(zip(imp_keys, last_val))
        }

def get_valid_scimark_programs():
    programs = ["FFT", "LU", "MonteCarlo", "SOR", "SparseCompRow"]
    results = []
    for prog in programs:
        os.chdir(f"{USER_PREFIX}/benchmark_scimark/{prog}")
        subprocess.run(f"cp {prog}OptimizedOriginal {prog}Optimized.java", shell=True)
        try:
            subprocess.run(["make", "compile"], check=True, capture_output=True, text=True, timeout=120)
        except subprocess.CalledProcessError:
            continue

        method_name = get_hotspots("SciMark", prog, 1)[0][0]
        method = method_name.split('/')[-1].split('.')[-1]
        results.append((prog, method))

    return results