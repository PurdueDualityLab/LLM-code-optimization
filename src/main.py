from dotenv import load_dotenv
import json
import os
import sys
from utils import Logger
import argparse
from agent import OpenAIAssistant
from status import Status
from llm.generator_llm import llm_optimize, handle_compilation_error
from llm.evaluator_llm import evaluator_llm
from energy_language_benchmark import get_valid_energy_language_programs, EnergyLanguageBenchmark

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
openai_key = os.getenv('API_KEY')
logger = Logger("logs", sys.argv[2]).logger

def parse_arguments():
    parser = argparse.ArgumentParse(description="LLM-Energy-Optimization")
    parser.add_argument("--benchmark", type=str, default="EnergyLanguage", choices=["EnergyLanguage", "PIE", "Datacenter", "Android"], help="dataset used for experiment")
    parser.add_argument("--llm", type=str, default="gpt-4o", choices=["llama-3.1", "code llama"], help="llm used for inference")
    parser.add_argument("--self_optimization_step", type=int, default=5, help="number of LLM self-optimization step")

def get_valid_programs(benchmark):
    if (benchmark == "EnergyLanguage"):
        return get_valid_energy_language_programs()
    return []

def master_script(benchmark, model, self_optimization_step):
    #create LLM agent
    with open(f"{USER_PREFIX}/src/llm/llm_prompts/generator_prompt.txt", "r") as file:
        generator_prompt = file.read()

    with open(f"{USER_PREFIX}/src/llm/llm_prompts/evaluator_prompt.txt", "r") as file:
        evaluator_prompt = file.read()

    generator = OpenAIAssistant(api_key=openai_key, name="Generator", instructions=generator_prompt, model=model)
    evaluator = OpenAIAssistant(api_key=openai_key, name="Evaluator", instructions=evaluator_prompt, model=model)
        
    for program in get_valid_programs(benchmark):     
        if (benchmark == "EnergyLanguage"):
            benchmark_obj = EnergyLanguageBenchmark(program)
        else:
            logger.error("Invalid benchmark.")
            return
        
        compilation_errors = 0
        reoptimize_lastly_flag = 0
        evaluator_feedback = ""
        original_code = benchmark_obj.get_original_code()
        last_working_optimized_code = original_code
        last_optimized_code = original_code
        num_success_iteration = 0
        while True:
            # optimize code
            if reoptimize_lastly_flag == 0:
                logger.info(f"Optimizing {program}, iteration {num_success_iteration}")
                if compilation_errors > 0 and compilation_errors < 3:
                    compilation_error_message = benchmark_obj.get_compilation_error()
                    last_optimized_code = handle_compilation_error(error_message=compilation_error_message, llm_assistant=generator)
                else:
                    last_optimized_code = llm_optimize(code=last_optimized_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback)
            else:
                logger.info("re-optimizing from latest working optimization")
                last_optimized_code = llm_optimize(code=last_working_optimized_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback)
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
                continue
            else:
                # getting feedback from the evaluator
                logger.info("Regression test success, getting evaluator feedback")
                energy_data = benchmark_obj.get_energy_data(program)
                evaluator_feedback = evaluator_llm(energy_data=energy_data, llm_assistant=evaluator)
                logger.info("Got evaluator feedback")
                num_success_iteration += 1
                benchmark_obj.set_optimization_iteration(num_success_iteration)
                compilation_errors = 0

                # Copy lastest optimized code for logic error re-optimization
                last_working_optimized_code = last_optimized_code
                
                if num_success_iteration == self_optimization_step:
                    logger.info("Optimization Complete, writing results to file.....")

                    dict_str = json.dumps(benchmark_obj.get_energy_data(), indent=4)
                    results_dir = f"{USER_PREFIX}/results/{benchmark}"
                    if not os.path.exists(results_dir):
                        os.makedirs(results_dir)
                    with open(f"{results_dir}/{program}.txt", "w+") as file:
                        file.write(str(dict_str))
                    break   

def main():
    args=parse_arguments()
    
    benchmark = args.benchmark
    model = args.llm
    self_optimization_step = args.self_optimization_step
       
    #run benchmark
    master_script(benchmark, model, self_optimization_step)

if __name__ == "__main__":
    main()