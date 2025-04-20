from dotenv import load_dotenv
import json
import os
import sys
from utils import Logger
import argparse
from agent import LLMAgent
from status import Status
from llm.generator_llm import llm_optimize, handle_compilation_error
from llm.evaluator_llm import evaluator_llm
from energy_language_benchmark import get_valid_energy_language_programs, EnergyLanguageBenchmark
from pie_benchmark import get_valid_pie_programs, PIEBenchmark
from scimark_benchmark import get_valid_scimark_programs, SciMarkBenchmark
from dacapo_benchmark import get_valid_dacapo_classes, DaCapoBenchmark
from collections import defaultdict
import glob

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
openai_key = os.getenv('API_KEY')
genai_api_key = os.getenv('GenAI_API_KEY')
logger = Logger("logs", sys.argv[2]).logger

def parse_arguments():
    parser = argparse.ArgumentParser(description="LLM-Code-Optimization")
    parser.add_argument("--benchmark", type=str, default="EnergyLanguage", choices=["EnergyLanguage", "PIE", "SciMark", "Dacapobench", "Android"], help="dataset used for experiment")
    parser.add_argument("--llm", type=str, default="gpt-4o", choices=["gpt-4o", "o1", "o3-mini", "deepseek-r1:32b","deepseek-r1:70b", "qwen2.5:72b", "llama3.3:70b", "codellama:latest"], help="llm used for inference")
    parser.add_argument("--self_optimization_step", type=int, default=5, help="number of LLM self-optimization step")
    parser.add_argument("--num_programs", type=int, default=5, help="For PIE only, number of programs from the benchmark to test")
    parser.add_argument("--application_name", type=str, default="fop", choices=["biojava", "fop", "cassandra", "h2", "h2o", "Kafka", "Luindex", "Lusearch", "spring", "Tomact", "Tradebeans", "Tradesoap", "Xalan", "pmd"], help="For Dacapobench only, name of the application from the benchmark to test")
    parser.add_argument("--genai_studio", type=bool, default=False, help="Flag to indicate if genai_studio is used to inference open-source llms")
    parser.add_argument("--method_level", type=bool, default=False, help="Flag to indicate if method level optimization is used")
    parser.add_argument("--ablation", type=int, default=0, choices=[0, 1, 2, 3, 4], help="ablation study level: 0 indicates no ablation, 1 indicates generator with source code and basic prompt, 2 adds ast and flamegraph, 3 adds advisor, 4 adds feedback without evaluator")

    args = parser.parse_args()
    return args

def get_valid_programs(benchmark, num_programs, application_name):
    if (benchmark == "EnergyLanguage"):
        return get_valid_energy_language_programs()
    elif (benchmark == "PIE"):
        return get_valid_pie_programs()
    elif (benchmark == "SciMark"):
        # cleanup
        txt_files = glob.glob(f"{USER_PREFIX}/benchmark_scimark/*/*.txt")
        flamegraph_files = glob.glob(f"{USER_PREFIX}/benchmark_scimark/*/*Flamegraph.java")
        all_files_to_remove = txt_files + flamegraph_files
        for file_path in all_files_to_remove:
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing {file_path}: {e}")
        return get_valid_scimark_programs()
    elif (benchmark == "Dacapobench"):
        return get_valid_dacapo_classes(application_name)
    else:
        return []
    
def write_result(energy_data, program, evaluator_feedback_data, results_dir):
    dict_str = json.dumps(energy_data, indent=4)
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    with open(f"{results_dir}/{program}.txt", "w+") as file:
        file.write(str(dict_str))

    avg_energy_improvement = evaluator_feedback_data["max_avg_speedup"]["avg_energy_improvement"]
    avg_speedup = evaluator_feedback_data["max_avg_speedup"]["avg_speedup"]
    avg_cpu_improvement = evaluator_feedback_data["max_avg_speedup"]["avg_cpu_improvement"]
    avg_memory_improvement = evaluator_feedback_data["max_avg_speedup"]["avg_memory_improvement"]
    avg_throughput_improvement = evaluator_feedback_data["max_avg_speedup"]["avg_throughput_improvement"]
    if "mflops_improvement" in evaluator_feedback_data["max_avg_speedup"]:
        avg_mflops_improvement = evaluator_feedback_data["max_avg_speedup"]["mflops_improvement"]
    lowest_loc = evaluator_feedback_data["max_avg_speedup"]["num_of_lines"]
    original_loc = evaluator_feedback_data["original"]["num_of_lines"]

    return {
        "energy_improvement": avg_energy_improvement,
        "runtime_improvement": avg_speedup,
        "cpu_cycles_improvement": avg_cpu_improvement,
        "peak_memory_improvement": avg_memory_improvement,
        "throughput_improvement": avg_throughput_improvement,
        "mflops_improvement": avg_mflops_improvement if "mflops_improvement" in evaluator_feedback_data["max_avg_speedup"] else None,
        "loc_improvement": round(original_loc / lowest_loc, 3),
    }

def master_script(benchmark, num_programs, application_name, model, self_optimization_step, use_genai_studio, method_level):
    #create LLM agent
    generator = LLMAgent(openai_api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")
    evaluator = LLMAgent(openai_api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")

    results = {}
        
    for program in get_valid_programs(benchmark, num_programs, application_name):  
        if benchmark == "EnergyLanguage":
            benchmark_obj = EnergyLanguageBenchmark(program)
        elif benchmark == "PIE":
            benchmark_obj = PIEBenchmark(program)
        elif benchmark == "SciMark":
            target_program = program[0]
            target_method = program[1]
            benchmark_obj = SciMarkBenchmark(target_program, target_method, method_level)
        elif benchmark == "Dacapobench":
            #program is a tuple of (test_method, test_class, test_namespace, test_group)
            test_method = program[0]
            test_class = program[1]
            test_namespace = program[2]
            test_group = program[3]
            unit_tests = program[4]
            benchmark_obj = DaCapoBenchmark(test_method, test_class, test_namespace, test_group, unit_tests, application_name, method_level)
        else:
            logger.error("Invalid benchmark")
            break

        folder_name = program[1] if isinstance(program, tuple) else program

        if benchmark_obj.get_original_code() is None:
            results[folder_name] = "Unable to find original code"
            continue
        
        # TODO: Change the error message shown by logger - currently it is misleading since code may compile but actually RAPL causes the error
        original_code_compiles = benchmark_obj.set_original_energy()
        if not original_code_compiles:
            logger.error(f"Unable to compile or measure energy of the original code for {program}")
            results[folder_name] = "Unable to compile or measure energy of the original code or timeout"
            continue
        
        compilation_errors = 0
        reoptimize_lastly_flag = 0
        evaluator_feedback = ""
        original_code = benchmark_obj.get_original_code()
        last_working_optimized_code = original_code
        last_optimized_code = original_code
        num_success_iteration = 0
        total_output_difference = 0
        total_compilation_failure = 0

        results_dir = f"{USER_PREFIX}/results/{benchmark}"
       
        while True:
            if total_output_difference == 3 or total_compilation_failure == 2:
                logger.error("Unable to produce functional equivalent programs.")
                if num_success_iteration == 0:
                    results[folder_name] = "Unable to produce functional equivalent programs."
                else:
                    logger.info(f"{num_success_iteration} optimization completes, writing results to file.....")
                    energy_data = benchmark_obj.get_energy_data()
                    results[folder_name] = write_result(energy_data, folder_name, evaluator_feedback_data, results_dir)
                break
            # optimize code
            if reoptimize_lastly_flag == 0:
                logger.info(f"Optimizing {program}, iteration {num_success_iteration}")
                if compilation_errors > 0 and compilation_errors < 3:
                    compilation_error_message = benchmark_obj.get_compilation_error()
                    last_optimized_code = handle_compilation_error(error_message=compilation_error_message, llm_assistant=generator)
                else:
                    ast = benchmark_obj.pre_process(last_optimized_code)
                    flame_report = benchmark_obj.dynamic_analysis(code=last_optimized_code) if benchmark == "PIE" or not method_level else None
                    last_optimized_code = llm_optimize(code=last_optimized_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback, ast=ast, flame_report=flame_report)
            else:
                logger.info("re-optimizing from latest working optimization")
                generator.clear_memory()
                evaluator.clear_memory()
                evaluator_feedback = ""
                ast = benchmark_obj.pre_process(last_working_optimized_code)
                flame_report = benchmark_obj.dynamic_analysis(code=last_working_optimized_code) if benchmark == "PIE" or not method_level else None
                last_optimized_code = llm_optimize(code=last_working_optimized_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback, ast=ast, flame_report=flame_report)
                reoptimize_lastly_flag = 0
            
            # Error in LLM completion
            if last_optimized_code is not None:       
                # code post_process
                last_optimized_code = benchmark_obj.post_process(last_optimized_code)

                # static analysis
                status = benchmark_obj.static_analysis(last_optimized_code)
            else:
                status = Status.RUNTIME_ERROR_OR_TEST_FAILED
            
            # switch case of status
            if (status == Status.COMPILATION_ERROR):
                if compilation_errors == 3:
                    logger.error("Could not compile optimized file after 3 attempts, will re-optimize from lastest working optimized file")
                    reoptimize_lastly_flag = 1
                    compilation_errors = 0
                    evaluator_feedback = ""
                    total_compilation_failure += 1
                compilation_errors += 1
                logger.error("Error in optimized file, re-optimizing")
                continue
            elif (status == Status.RUNTIME_ERROR_OR_TEST_FAILED):
                logger.error("Output difference in optimized file, will re-optimize from lastest working optimized file")
                reoptimize_lastly_flag = 1
                evaluator_feedback = ""
                compilation_errors = 0
                total_output_difference += 1
                continue
            else:
                num_success_iteration += 1
                compilation_errors = 0
                # Copy lastest optimized code for logic error re-optimization
                last_working_optimized_code = last_optimized_code
                total_output_difference = 0
                total_compilation_failure = 0

                evaluator_feedback_data = benchmark_obj.get_evaluator_feedback_data()
                
                if num_success_iteration == self_optimization_step:
                    logger.info("Optimization Complete, writing results to file.....")
                    energy_data = benchmark_obj.get_energy_data()
                    results[folder_name] = write_result(energy_data, folder_name, evaluator_feedback_data, results_dir)
                    break
                
                # Perform dynamic analysis using flame graph
                if benchmark == "PIE" or not method_level:
                    benchmark_obj.dynamic_analysis(last_optimized_code)
                    evaluator_feedback_data = benchmark_obj.get_evaluator_feedback_data()

                # getting feedback from the evaluator
                logger.info("Regression test success, getting evaluator feedback")
                evaluator_feedback = evaluator_llm(evaluator_feedback_data=evaluator_feedback_data, llm_assistant=evaluator)
                logger.info("Got evaluator feedback")
        
        # clearing LLM memory
        generator.clear_memory()
        evaluator.clear_memory()

    evaluation_summary(results, results_dir)
        
def ablation_script_level_1_and_2(benchmark, num_programs, application_name, model, use_genai_studio, ablation):
    #create LLM agent
    generator = LLMAgent(openai_api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")
    
    results = {}
    
    for program in get_valid_programs(benchmark, num_programs, application_name):
        if benchmark == "PIE":
            benchmark_obj = PIEBenchmark(program)
        elif benchmark == "SciMark":
            target_program = program[0]
            target_method = program[1]
            benchmark_obj = SciMarkBenchmark(target_program, target_method, method_level=False)
        else:
            logger.error("Invalid benchmark for ablation study")
            break
        
        folder_name = program[0] if isinstance(program, tuple) else program

        if benchmark_obj.get_original_code() is None:
            results[folder_name] = "Unable to find original code"
            continue

        original_code_compiles = benchmark_obj.set_original_energy()
        if not original_code_compiles:
            results[folder_name] = "Unable to compile original code or timeout"
            continue
        
        original_code = benchmark_obj.get_original_code()

        # create direct if not exist
        if not os.path.exists(f"{USER_PREFIX}/results/ablation"):
            os.makedirs(f"{USER_PREFIX}/results/ablation")
        if not os.path.exists(f"{USER_PREFIX}/results/ablation/level_{ablation}"):
            os.makedirs(f"{USER_PREFIX}/results/ablation/level_{ablation}")
        results_dir = f"{USER_PREFIX}/results/ablation/level_{ablation}"
        
        if ablation == 2:
            logger.info(f"Optimizing {program} with ast and flamegraph")
            ast = benchmark_obj.pre_process(original_code)
            flame_report = benchmark_obj.dynamic_analysis(original_code)
            optimized_code = llm_optimize(code=original_code, llm_assistant=generator, ast=ast, flame_report=flame_report)
        else:
            logger.info(f"Optimizing {program} with only source code")
            optimized_code = llm_optimize(code=original_code, llm_assistant=generator)
            
         # Error in LLM completion
        if optimized_code is None:
            logger.error("Error in LLM completion")
            results[folder_name] = "Error in LLM completion."
            continue
        
        # code post_process
        optimized_code = benchmark_obj.post_process(optimized_code)

        # static analysis
        status = benchmark_obj.static_analysis(optimized_code)

        # switch case of status
        if (status == Status.COMPILATION_ERROR or status == Status.RUNTIME_ERROR_OR_TEST_FAILED):
            logger.error("Error in optimized file")
            results[folder_name] = "Unable to produce functional equivalent programs."
        else:
            logger.info("Optimization Complete, writing results to file.....")
            energy_data = benchmark_obj.get_energy_data()
            evaluator_feedback_data = benchmark_obj.get_evaluator_feedback_data()
            results[folder_name] = write_result(energy_data, folder_name, evaluator_feedback_data, results_dir)
    
    evaluation_summary(results, results_dir)

def evaluation_summary(results, results_dir):
    try:
        results_dir
    except NameError:
        results_dir = f"{USER_PREFIX}/results"

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    with open(f"{results_dir}/results.txt", "w+") as file:
        json.dump(results, file, indent=4)
        
    # final evaluation result
    total_programs = len(results)
    valid_programs = {k: v for k, v in results.items() if isinstance(v, dict)}
    num_correct = len(valid_programs)
    
    # Initialize containers for aggregation
    metrics = defaultdict(list)
    metrics_above_1_1 = defaultdict(int)
    
    all_metrics = [
        "energy_improvement", "runtime_improvement", "cpu_cycles_improvement",
        "peak_memory_improvement", "throughput_improvement", "mflops_improvement",
        "loc_improvement"
    ]
    
    # Process each program (including incorrect ones)
    for program, result in results.items():
        if isinstance(result, dict):  # functionally correct
            for metric in all_metrics:
                value = result.get(metric)
                if value is None:
                    continue
                if value >= 1.1:
                    metrics_above_1_1[metric] += 1
                metrics[metric].append(max(value, 1.0))  # cap at 1
        else:  # non-functional, count as 1
            for metric in all_metrics:
                metrics[metric].append(1.0)  # not above 1.1, so don't increment count
    
    # Compute statistics
    correctness_percent = 100 * num_correct / total_programs
    
    percent_above_1_1 = {
        metric: 100 * metrics_above_1_1.get(metric, 0) / total_programs
        for metric in all_metrics
    }
    avg_improvement = {
        metric: sum(metrics[metric]) / len(metrics[metric])
        for metric in all_metrics
    }
    
    # Write to .txt file
    output_path = f"{results_dir}/optimization_summary.txt"
    with open(output_path, "w") as f:
        f.write(f"Correctness: {correctness_percent:.2f}%\n\n")
        f.write("% of programs with ≥1.1 improvement (out of all programs):\n")
        for metric in all_metrics:
            percent = percent_above_1_1.get(metric, 0.0)
            f.write(f"  {metric}: {percent:.2f}%\n")
        f.write("\nAverage improvement (capping values < 1 as 1):\n")
        for metric in all_metrics:
            avg = avg_improvement.get(metric, 0.0)
            f.write(f"  {metric}: {avg:.3f}\n")
    
    logger.info(f"Evaluation summary written to {output_path}")

def main():
    args=parse_arguments()
    
    benchmark = args.benchmark
    num_programs = args.num_programs
    model = args.llm
    self_optimization_step = args.self_optimization_step
    use_genai_studio = args.genai_studio
    application_name = args.application_name
    method_level = args.method_level
    ablation = args.ablation
        
    if ablation == 0:
        master_script(benchmark, num_programs, application_name, model, self_optimization_step, use_genai_studio, method_level)
    elif ablation == 1 or ablation == 2:
        ablation_script_level_1_and_2(benchmark, num_programs, application_name, model, use_genai_studio, ablation)      

if __name__ == "__main__":
    main()
