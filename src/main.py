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

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
openai_key = os.getenv('API_KEY')
genai_api_key = os.getenv('GenAI_API_KEY')
logger = Logger("logs", sys.argv[2]).logger

def parse_arguments():
    parser = argparse.ArgumentParser(description="LLM-Code-Optimization")
    parser.add_argument("--benchmark", type=str, default="EnergyLanguage", choices=["EnergyLanguage", "PIE", "SciMark", "Dacapobench", "Android"], help="dataset used for experiment")
    parser.add_argument("--llm", type=str, default="gpt-4o", choices=["gpt-4o", "o1", "o3-mini", "deepseek-r1:671b","deepseek-r1:70b", "qwen2.5-coder:32b", "llama3.3:70b", "codellama:70b"], help="llm used for inference")
    parser.add_argument("--self_optimization_step", type=int, default=5, help="number of LLM self-optimization step")
    parser.add_argument("--num_programs", type=int, default=5, help="For PIE only, number of programs from the benchmark to test")
    parser.add_argument("--application_name", type=str, default="fop", choices=["fop", "cassandra", "h2", "h2o", "Kafka", "Luindex", "Lusearch", "Spring", "Tomact", "Tradebeans", "Tradesoap", "Xalan"], help="For Dacapobench only, name of the application from the benchmark to test")
    parser.add_argument("--genai_studio", type=bool, default=False, help="Flag to indicate if genai_studio is used to inference open-source llms")

    args = parser.parse_args()
    return args

def get_valid_programs(benchmark, num_programs, application_name):
    if (benchmark == "EnergyLanguage"):
        return get_valid_energy_language_programs()
    elif (benchmark == "PIE"):
        return get_valid_pie_programs(num_programs)
    elif (benchmark == "SciMark"):
        return get_valid_scimark_programs()
    elif (benchmark == "Dacapobench"):
        return get_valid_dacapo_classes(application_name)
    else:
        return []

def master_script(benchmark, num_programs, application_name, model, self_optimization_step, use_genai_studio):
    #create LLM agent
    generator = LLMAgent(api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")
    evaluator = LLMAgent(api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")

    results = {}
    
    for program in get_valid_programs(benchmark, num_programs, application_name):  
        if benchmark == "EnergyLanguage":
            benchmark_obj = EnergyLanguageBenchmark(program)
        elif benchmark == "PIE":
            benchmark_obj = PIEBenchmark(program)
        elif benchmark == "SciMark":
            benchmark_obj = SciMarkBenchmark(program)
        elif benchmark == "Dacapobench":
            #program is a tuple of (test_group, test_class_name)
            test_group = program[0]
            test_class = program[1]
            benchmark_obj = DaCapoBenchmark(test_class, test_group, application_name)
        else:
            logger.error("Invalid benchmark")
            break
        original_code_compiles = benchmark_obj.set_original_energy()
        if not original_code_compiles:
            logger.error(f"Unable to compile original code for {program}")
            results[program] = "Unable to compile original code"
            continue
        
        compilation_errors = 0
        reoptimize_lastly_flag = 0
        evaluator_feedback = ""
        original_code = benchmark_obj.get_original_code()
        last_working_optimized_code = original_code
        last_optimized_code = original_code
        num_success_iteration = 0
        total_output_difference = 0
        
        while True:
            if total_output_difference == 3:
                logger.error("Unable to produce functional equivalent programs.")
                results[program] = "Unable to produce functional equivalent programs."
                break
            # optimize code
            if reoptimize_lastly_flag == 0:
                logger.info(f"Optimizing {program}, iteration {num_success_iteration}")
                if compilation_errors > 0 and compilation_errors < 3:
                    compilation_error_message = benchmark_obj.get_compilation_error()
                    last_optimized_code = handle_compilation_error(error_message=compilation_error_message, llm_assistant=generator)
                else:
                    ast = benchmark_obj.pre_process(last_optimized_code)
                    last_optimized_code = llm_optimize(code=last_optimized_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback, ast=ast)
            else:
                logger.info("re-optimizing from latest working optimization")
                generator.clear_memory()
                evaluator_feedback = ""
                ast = benchmark_obj.pre_process(last_working_optimized_code)
                last_optimized_code = llm_optimize(code=last_working_optimized_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback, ast=ast)
                reoptimize_lastly_flag = 0
            
            # code post_process
            last_optimized_code = benchmark_obj.post_process(last_optimized_code)

            # static analysis
            status = benchmark_obj.static_analysis(last_optimized_code)
            
            # switch case of status
            if (status == Status.COMPILATION_ERROR):
                if compilation_errors == 3:
                    logger.error("Could not compile optimized file after 3 attempts, will re-optimize from lastest working optimized file")
                    reoptimize_lastly_flag = 1
                    compilation_errors = 0
                    evaluator_feedback = ""
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

                evaluator_feedback_data = benchmark_obj.get_evaluator_feedback_data()
                
                if num_success_iteration == self_optimization_step:
                    logger.info("Optimization Complete, writing results to file.....")

                    dict_str = json.dumps(benchmark_obj.get_energy_data(), indent=4)
                    results_dir = f"{USER_PREFIX}/results/{benchmark}"
                    if not os.path.exists(results_dir):
                        os.makedirs(results_dir)
                    with open(f"{results_dir}/{program}.txt", "w+") as file:
                        file.write(str(dict_str))

                    original_energy = evaluator_feedback_data["original"]["avg_energy"]
                    original_runtime = evaluator_feedback_data["original"]["avg_runtime"]
                    original_loc = evaluator_feedback_data["original"]["num_of_lines"]

                    lowest_energy = evaluator_feedback_data["lowest_avg_energy"]["avg_energy"]
                    lowest_runtime = evaluator_feedback_data["lowest_avg_energy"]["avg_runtime"]
                    lowest_loc = evaluator_feedback_data["lowest_avg_energy"]["num_of_lines"]

                    results[program] = {
                        "energy_change": ((lowest_energy - original_energy) / original_energy) * 100,
                        "runtime_change": ((lowest_runtime - original_runtime) / original_runtime) * 100,
                        "loc_change": ((lowest_loc - original_loc) / original_loc) * 100,
                    }

                    break

                # getting feedback from the evaluator
                logger.info("Regression test success, getting evaluator feedback")
                evaluator_feedback = evaluator_llm(evaluator_feedback_data=evaluator_feedback_data, llm_assistant=evaluator)
                logger.info("Got evaluator feedback")

    with open(f"{results_dir}/results.txt", "w+") as file:
        json.dump(results, file, indent=4)

def main():
    args=parse_arguments()
    
    benchmark = args.benchmark
    num_programs = args.num_programs
    model = args.llm
    self_optimization_step = args.self_optimization_step
    use_genai_studio = args.genai_studio
    application_name = args.application_name
       
    #run benchmark
    master_script(benchmark, num_programs, application_name, model, self_optimization_step, use_genai_studio)

if __name__ == "__main__":
    main()