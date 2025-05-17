import os
from dotenv import load_dotenv
import json
import sys
sys.path.insert(0, '/home/hpeng/E2COOL/src')
from agent import LLMAgent
from utils import Logger
import sys
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
import re
import subprocess
import csv
from split_test_code import split_asserts

logger = Logger("logs", "default").logger

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
openai_key = os.getenv('API_KEY')
genai_api_key = os.getenv('GenAI_API_KEY')
DATASET_DIR = os.path.join(USER_PREFIX, "benchmark_human_eval/dataset.json")
RAPL_TOOL = os.path.join(USER_PREFIX, "RAPL/main")
RUNTIME_LOG = os.path.join(USER_PREFIX, "src/runtime_logs/c++.csv")
env = Environment(loader=FileSystemLoader(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/prompt"))

llm = LLMAgent(openai_api_key=openai_key, genai_api_key=genai_api_key, model="gpt-4o", system_message="")

def post_process(code):
    code = code.replace("```cpp", "").replace("```", "")
        
    def remove_main_function(cpp_code: str) -> str:
        # Regex pattern to match the main function (basic heuristic)
        pattern = re.compile(
            r'\bint\s+main\s*\([^)]*\)\s*{'
            r'(?:[^{}]*|{[^{}]*})*'
            r'}', 
            re.DOTALL
        )

        cleaned_code = re.sub(pattern, '', cpp_code)
        return cleaned_code
    code = remove_main_function(code)
    return re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL | re.MULTILINE)

def compile(program, optimized_code, test_code):
    destination_path = f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}/optimized_{program}.cpp"
    with open(destination_path, "w") as file:
        file.write(f"{optimized_code}\n\n{test_code}")

    os.chdir(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}")
    try:
        subprocess.run(["make", "compile_optimized"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Compile failed: {e.stderr}")
        return False
    
    return True

def run_tests(program: str) -> bool:
    # Needed for makefiles
    os.chdir(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}")

    try:        
        logger.info(f"Running optimized program")
        result = subprocess.run(["make", "run_optimized"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin-1', timeout=120)
    except subprocess.CalledProcessError as e:
        logger.error(f"Run_Test failed: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("Make run timeout")
        return False

    if result.returncode is None or result.returncode != 0:
        return False
    
    return True

def correctness_check(program: str, function_code: str, test_code: str) -> bool:
    # Compile and run the code
    if not compile(program, function_code, test_code):
        return False
    # Run the test code
    if not run_tests(program):
        return False
    
    return True

def get_most_expensive_unit_test(program: str, function_code: str, test_code: str) -> str:
    snippets = split_asserts(test_code)
    most_expensive_runtime = -1
    most_expensive_code_str = ""
    for i, code_str in enumerate(snippets, 1):
        # e.g. compile or run with subprocess, or feed to a sandbox
        logger.info(f"---- snippet #{i} ----")
        logger.info(code_str)
        destination_path = f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}/unittest/{program}.cpp"
        with open(destination_path, "w") as file:
            file.write(f"{function_code}\n\n{code_str}")

        os.chdir(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}/unittest")
        log_file_path = f"{USER_PREFIX}/src/runtime_logs/c++.csv"
        open(log_file_path, "w").close()
        try:
            cmd1 = ["/usr/bin/g++", "-g", "-c", "-pipe", "-fomit-frame-pointer", "-march=native", "-std=c++11", "-fopenmp", f"{program}.cpp", "-o", f"{program}.cpp.o"]
            cmd2 = ["/usr/bin/g++", "-g", f"{program}.cpp.o", "-o", f"{program}.gpp_run", "-fopenmp", "-lssl", "-lcrypto"]
            subprocess.run(cmd1, check=True, capture_output=True, text=True)
            subprocess.run(cmd2, check=True, capture_output=True, text=True)
            
            subprocess.run(["sudo", "modprobe", "msr"], check=True, capture_output=True, text=True, timeout=120)
            subprocess.run([
                "sudo", f"{USER_PREFIX}/RAPL/main",
                f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}/unittest/{program}.gpp_run",
                "c++", f"{program}"
            ], check=True, capture_output=True, text=True, timeout=120)
            subprocess.run(["sudo", "chmod", "-R", "777", f"{USER_PREFIX}/src/runtime_logs/c++.csv"], check=True, capture_output=True, text=True, timeout=120)
        except subprocess.CalledProcessError as e:
            logger.error(f"Compile unittest {i} failed: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            logger.error(f"Compile unittest {i} timeout")
            return False
            
        values = []
        with open(RUNTIME_LOG, mode='r') as file:
            reader = csv.reader(file)
            for index, row in enumerate(reader):
                try:
                    val = float(row[2])
                    values.append(val)
                except (IndexError, ValueError):
                    continue
        
        values.remove(max(values))
        values.remove(min(values))
        
        if not values:
            return -1

        avg_latency = sum(values) / len(values)
        
        if avg_latency > most_expensive_runtime:
            most_expensive_runtime = avg_latency
            most_expensive_code_str = code_str
    logger.info(f"Most expensive unit test: {most_expensive_code_str}\n")
    return most_expensive_code_str

def measure_performance(program: str, code: str, test: str, optimized: bool):
    log_file_path = f"{USER_PREFIX}/src/runtime_logs/c++.csv"
    open(log_file_path, "w").close()
    
    if optimized:
        can_compile = compile(program, optimized_code=code, test_code=test)
        if not can_compile:
            logger.error(f"Compilation failed for final make measure")
            return 0
    else:
        # Compile and run the original code
        destination_path = f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}/{program}.cpp"
        with open(destination_path, "w") as file:
            file.write(f"{code}\n\n{test}")

        os.chdir(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}")
        try:
            subprocess.run(["make", "compile"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Compile original code failed: {e.stderr}")
            return 0
        
    os.chdir(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{program}")

    try:
        cmd = ["make", "measure_optimized" if optimized else "measure"]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return extract_metrics()
    except subprocess.CalledProcessError as e:
        logger.error(f"Make measure failed: {e.stderr}")
        return 0

def extract_metrics():
    values = []
    with open(RUNTIME_LOG, mode='r') as file:
        reader = csv.reader(file)
        for index, row in enumerate(reader):
            try:
                val = float(row[2])
                values.append(val)
            except (IndexError, ValueError):
                continue

    if not values:
        return -1

    avg_latency = sum(values) / len(values)
    logger.info(f"Average latency: {avg_latency}")
    return avg_latency

def round_1(function_code: str):
    template = env.get_template("round_1.jinja")
    data = {
        "solution": function_code
    }
    prompt = template.render(data)
        
    logger.info(f"llm_optimize: Round 1 LLM Optimizing ....")
    logger.info(f"Round 1 prompt: {prompt}")
    
    class Optimization(BaseModel):
        code: str
    
    # llm.add_to_memory("user", prompt)
    # llm.generate_response(Optimization)
    # response = llm.get_last_msg()
    
    # try:
    #     content_dict = json.loads(response["content"])
    #     code = content_dict["code"]
    # except json.JSONDecodeError as e:
    #     logger.error(f"Failed to decode JSON: {e}")
    #     return
    
    # if code == "":
    #     logger.error("Error in llm completion")
    #     return None
    
    return function_code

def round_2(function_code, testcase: str):
    template = env.get_template("round_2.jinja")
    data = {
        "testcase": testcase
    }
    prompt = template.render(data)
        
    logger.info(f"llm_optimize: Round 2 LLM Optimizing ....")
    logger.info(f"Round 2 prompt: {prompt}")
    
    # class Optimization(BaseModel):
    #     code: str
    
    # llm.add_to_memory("user", prompt)
    # llm.generate_response(Optimization)
    # response = llm.get_last_msg()
    
    # try:
    #     content_dict = json.loads(response["content"])
    #     code = content_dict["code"]
    # except json.JSONDecodeError as e:
    #     logger.error(f"Failed to decode JSON: {e}")
    #     return
    
    # if code == "":
    #     logger.error("Error in llm completion")
    #     return None
    
    return function_code

def main():
    logger.info(f"Running PerfCodeGen.")
    results = []
    with open(DATASET_DIR, "r") as f:
        dataset = json.load(f)
    
    for entry in dataset[1:2]:
        id = entry["task_id"]
        logger.info(f"Processing: {id}")
        
        folder_path = f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{id}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        if not os.path.exists(f"{folder_path}/unittest"):
            os.makedirs(f"{folder_path}/unittest")      
        
        # Combine function and test code
        function_code = entry["function_code"]
        test_code = entry["test_code"]
        
        #Create parameterized Makefile for each problem id folder
        makefile_template = open(f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/makefile_template.mak", "r")
        makefile_content = makefile_template.read()
        makefile_content = makefile_content.replace("${FILE_NAME}", id)
        makefile_template.close()
        makefile_template = open(f"{folder_path}/Makefile", "w")
        makefile_template.write(makefile_content)
        makefile_template.close()
        
        # round 1 optimization
        logger.info(f"Optimizing {id} round 1")
        round_1_optimized_code = round_1(function_code)
        if round_1_optimized_code is None:
            logger.info(f"Error in round 1 llm completion for {id}")
            continue
        
        round_1_optimized_code = post_process(round_1_optimized_code)
        
        # correctness_check
        is_correct = correctness_check(id, round_1_optimized_code, test_code)
        
        if is_correct:
            logger.info(f"Correctness check passed for {id}")
        else:
            logger.info(f"Correctness check failed for {id}")
            results.append((id, -1))
            continue
        
        # exection
        logger.info("Getting most expensive unit test")
        most_expensive_unit_test = get_most_expensive_unit_test(id, round_1_optimized_code, test_code)
        
        # round 2 optimization
        logger.info(f"Optimizing {id} round 2")
        round_2_optimized_code = round_2(round_1_optimized_code, most_expensive_unit_test)
        if round_2_optimized_code is None:
            logger.info(f"Error in round 2 llm completion for {id}")
            continue
        
        round_2_optimized_code = post_process(round_2_optimized_code)
        
        # correctness_check
        is_correct = correctness_check(id, round_2_optimized_code, test_code)
        
        final_code = round_2_optimized_code
        if is_correct:
            logger.info(f"Correctness check passed for {id}")
        else:
            logger.info(f"Correctness check failed for {id}")
            final_code = round_1_optimized_code
        
        # measure final performance
        optimized_latency = measure_performance(id, final_code, test_code, optimized=True)
        original_latency = measure_performance(id, function_code, test_code, optimized=False)
        results.append((id, original_latency / optimized_latency))
        
    # Save results to CSV
    with open(f"{USER_PREFIX}/profcodegen_results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "Speedup"])
        writer.writerows(results)
        
    # Compute average improvements across all entries
    if results:
        total = len(results)
        correct = sum(1 for _, s in results if s != -1)
        optimized = sum(1 for _, s in results if s >= 1.1)
        speedups = [max(1, s) for _, s in results if s != -1]
        avg_speedup = round(sum(speedups) / len(speedups), 3) if speedups else 0

        percent_correct = round(100 * correct / total, 2)
        percent_optimized = round(100 * optimized / total, 2)

        logger.info(f"% correct: {percent_correct}%")
        logger.info(f"% optimized: {percent_optimized}%")
        logger.info(f"Average speedup (correct only, min 1x): {avg_speedup}x")
    else:
        logger.error("No valid results to compute statistics.")
            
    # Clean up
    for entry in dataset:
        id = entry["task_id"]
        folder_path = f"{USER_PREFIX}/src/baseline/profcodegen/humaneval/{id}"
        if os.path.exists(folder_path):
            os.system(f"rm -rf {folder_path}")
            
if __name__ == "__main__":
    main()