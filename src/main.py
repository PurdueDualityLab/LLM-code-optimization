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
from llm.advisor_llm import get_applicable_patterns
from scimark_benchmark import get_valid_scimark_programs, SciMarkBenchmark
from dacapo_benchmark import get_valid_dacapo_classes, DaCapoBenchmark

import pprint
import logging

load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
openai_key = os.getenv('API_KEY')
genai_api_key = os.getenv('GenAI_API_KEY')
logger = Logger("logs", sys.argv[2]).logger
#logger.setLevel(logging.CRITICAL + 1) # uncomment this to supress logging

def parse_arguments():
    parser = argparse.ArgumentParser(description="LLM-Code-Optimization")
    parser.add_argument("--benchmark", type=str, default="EnergyLanguage", choices=["EnergyLanguage", "PIE", "SciMark", "Dacapobench", "Android"], help="dataset used for experiment")
    parser.add_argument("--llm", type=str, default="gpt-4o", choices=["gpt-4o", "o1", "o3-mini", "deepseek-r1:671b","deepseek-r1:70b", "qwen2.5-coder:32b", "llama3.3:70b-instruct-q4_K_M", "codellama:70b", "llama3.2"], help="llm used for inference")
    parser.add_argument("--self_optimization_step", type=int, default=5, help="number of LLM self-optimization step")
    parser.add_argument("--num_programs", type=int, default=5, help="For PIE only, number of programs from the benchmark to test")
    parser.add_argument("--application_name", type=str, default="fop", choices=["fop", "cassandra", "h2", "h2o", "Kafka", "Luindex", "Lusearch", "Spring", "Tomact", "Tradebeans", "Tradesoap", "Xalan"], help="For Dacapobench only, name of the application from the benchmark to test")
    parser.add_argument("--genai_studio", type=bool, default=False, help="Flag to indicate if genai_studio is used to inference open-source llms")
    parser.add_argument("--top_k", type=int, default=5, help="Flag to set k value for Top-K accuracy test")

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
    
def program_results(evaluator_feedback_data, gen_content_dict, k_iter):
    return {
        "k_iter": str(k_iter),
        "energy_improvement": evaluator_feedback_data["current"]["avg_energy_improvement"],
        "runtime_improvement": evaluator_feedback_data["current"]["avg_speedup"],
        "cpu_cycles_improvement": evaluator_feedback_data["current"]["avg_cpu_improvement"],
        "memory_improvement": evaluator_feedback_data["current"]["avg_memory_improvement"],
        "throughput_improvement": evaluator_feedback_data["current"]["avg_throughput_improvement"],
        "loc_improvement": round(evaluator_feedback_data["current"]["num_of_lines"]/evaluator_feedback_data["original"]["num_of_lines"], 3),
        "optimization_pattern_name": gen_content_dict["optimization_pattern_name"],
        "optimization_pattern_description": gen_content_dict["optimization_pattern_description"],
        "optimization_rank": gen_content_dict["optimization_pattern_rank"],
        "strategy": gen_content_dict["strategy"],
        "final_code": gen_content_dict["final_code"],
    }

def failed_program_results(gen_content_dict):
    return {
        "k_iter": str(0),
        "energy_improvement": 0,
        "runtime_improvement": 0,
        "cpu_cycles_improvement": 0,
        "memory_improvement": 0,
        "throughput_improvement": 0,
        "loc_improvement": 0,
        "optimization_pattern_name": gen_content_dict["optimization_pattern_name"],
        "optimization_pattern_description": gen_content_dict["optimization_pattern_description"],
        "optimization_rank": gen_content_dict["optimization_pattern_rank"],
        "strategy": gen_content_dict["strategy"],
        "final_code": gen_content_dict["final_code"],
    }

def select_pattern_from_dict(pattern_dict, rank):
    # get the pattern corresponding to rank
    pattern_list = pattern_dict.get("patterns", [])
    selected_pattern = next((p for p in pattern_list if p["rank"] == str(rank)), None)
    return selected_pattern

def evaluate_results(results_dict, top_k):
    results_dict_sorted = sorted(results_dict.items(), key=lambda x: x[1].get("runtime_improvement"), reverse=True)
    top_k_bool_res = any(entry[1].get("optimization_rank") == "1" for entry in results_dict_sorted[:top_k])
    results_dict_sorted.append({f"The Advisor/LLM-ranked number 1 optimization pattern was found in the Top-K ({top_k})": f"{top_k_bool_res}"})
    #print(f"testing sort by runtime_improvement: {results_dict_sorted}")
    #print(f"testing boolean op: {top_k_bool_res}")
    return results_dict_sorted

def master_script(benchmark, num_programs, application_name, model, use_genai_studio, top_k):
    #create LLM agent
    generator = LLMAgent(api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")
    evaluator = LLMAgent(api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are a code expert. Think through the code optimizations strategies possible step by step.")
    advisor = LLMAgent(api_key=openai_key, genai_api_key=genai_api_key, model=model, use_genai_studio=use_genai_studio, system_message="You are an expert in software energy optimization patterns. You will be given a list of optimization patterns and corresponding source code. Your task is to analyze the source code and determine which patterns are most suitable for improving its energy efficiency.")

    results = {}
    
    for program in get_valid_programs(benchmark, num_programs, application_name):
        # clear LLM memory for next program
        generator.clear_memory()
        evaluator.clear_memory()
        advisor.clear_memory()

        # corresponds to rank of current optimization pattern being processes
        k_iter = 1

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
            results[f"{program}_iter_{k_iter}"] = "Unable to compile original code or timeout"
            continue
        
        compilation_errors = 0
        reoptimize_lastly_flag = 0
        evaluator_feedback = ""
        original_code = benchmark_obj.get_original_code()
        last_optimized_code = original_code
        total_output_difference = 0

        # for this program, getting patterns deemed as applicable by advisor LLM
        k_patterns = get_applicable_patterns(llm_assistant=advisor, source_code=original_code)
        # for this program, number of applicable patterns
        k_total = len(k_patterns.get("patterns"))
        # checking function get_applicable_patterns output
        print(f"k_total for program {program} is: {k_total}")
        print(f"patterns for program {program} are: {json.dumps(k_patterns)}")

        continue # uncomment this if you wish to see how many patterns are deemed applicable for a program without performing optimization.
        gen_content_dict = {}

        total_compilation_failure = 0

        results_dir = f"{USER_PREFIX}/results/{benchmark}"
        
        while True:
            if k_iter > k_total:
                break
            
            # get pattern for this iteration
            current_pattern_dict = select_pattern_from_dict(pattern_dict=k_patterns, rank=k_iter)
            current_pattern_str = json.dumps(current_pattern_dict)
            logger.info(f"Evaluating pattern: {current_pattern_str}")

            # if either occurrs, go to the next pattern
            if total_output_difference == 3 or total_compilation_failure == 2:
                logger.error("Unable to produce functional equivalent programs.")
                results[f"{program}_iter_{k_iter}"] = failed_program_results(gen_content_dict=gen_content_dict)

                # setting vars to evaluate the next pattern
                k_iter += 1
                compilation_errors = 0
                reoptimize_lastly_flag = 0
                evaluator_feedback = ""
                last_optimized_code = original_code
                total_output_difference = 0
                continue

            # optimize code
            if reoptimize_lastly_flag == 0:
                logger.info(f"Optimizing {program}")
                if compilation_errors > 0 and compilation_errors < 3:
                    # handle compilation error
                    compilation_error_message = benchmark_obj.get_compilation_error()
                    last_optimized_code = handle_compilation_error(error_message=compilation_error_message, llm_assistant=generator)
                else:
                    # pass original code
                    ast = benchmark_obj.pre_process(original_code)
                    gen_content_dict = llm_optimize(code=original_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback, optimization_pattern=current_pattern_str, ast=ast)
                    last_optimized_code = gen_content_dict["final_code"]
            else:
                # checksum failure/test failure occurred
                logger.info("re-optimizing from latest working optimization")
                generator.clear_memory()
                evaluator.clear_memory()
                # removing evaluator from pipeline for Top-K accuracy test
                evaluator_feedback = ""
                # re-optimize original code using same pattern
                ast = benchmark_obj.pre_process(original_code)
                gen_content_dict = llm_optimize(code=original_code, llm_assistant=generator, evaluator_feedback=evaluator_feedback, optimization_pattern=current_pattern_str, ast=ast)
                last_optimized_code = gen_content_dict["final_code"]
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
                # success
                compilation_errors = 0
                total_output_difference = 0
                total_compilation_failure = 0

                evaluator_feedback_data = benchmark_obj.get_evaluator_feedback_data()

                logger.info("Optimization Complete, writing results to file.....")
                results[f"{program}_iter_{k_iter}"] = program_results(evaluator_feedback_data=evaluator_feedback_data, gen_content_dict=gen_content_dict, k_iter=k_iter)
                k_iter += 1
        
                # getting feedback from the evaluator
                logger.info("Regression test success, moving onto next pattern")
        
        # write Top-K results for this program
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        with open(f"{results_dir}/results_{program}.txt", "w+") as file:
            json.dump(results, file, indent=4)
        
        # evaluate Top-K results for this program
        top_k_accuracy_res = evaluate_results(results_dict=results, top_k=top_k)
        formatted_res = pprint.pformat(top_k_accuracy_res, width=80)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        with open(f"{results_dir}/results_{program}.txt", "w+") as file:
            #file.write(json.dumps(top_k_accuracy_res))
            file.write(formatted_res)
            
        # clear dictionary for next program
        results.clear()

def main():
    args=parse_arguments()
    
    benchmark = args.benchmark
    num_programs = args.num_programs
    model = args.llm
    self_optimization_step = args.self_optimization_step
    use_genai_studio = args.genai_studio
    application_name = args.application_name
    top_k = args.top_k
       
    #run benchmark
    master_script(benchmark, num_programs, application_name, model, use_genai_studio, top_k)

def test_eval(r1, top_k):
    r1["entry1"] = {
        "k_iter": "1",
        "energy_improvement": 1.249,
        "runtime_improvement": 1.228,
        "cpu_cycles_improvement": 1.231,
        "memory_improvement": 89.476,
        "throughput_improvement": 1.228,
        "loc_improvement": 0.656,
        "optimization_pattern_name": "Increase cache efficiency",
        "optimization_pattern_description": "Adjust data structures and memory buffers to place items used at the same time next to each other in memory. This includes considerations such as memory locality and minimizing unnecessary memory accesses, especially for structures that aren't directly contributing to the operational logic.",
        "optimization_rank": "1",
        "strategy": "1. **Increase Cache Efficiency**: Instead of the string operations done manually for concatenation, review the need to fetch each character by leveraging contiguous memory access principles. The string concatenation approach needs no change except for reducing unnecessary structure initialization (i.e., the unused vector node).\n\n2. **Optimize I/O and Memory Utilization**:\n - Use a contiguous memory structure to ensure efficient string manipulations and retrieval.\n - Remove the vector node that consumes extra memory and is not used. Focus on only dealing with string `s` effectively.\n\nBy reducing unnecessary data structure utilization and keeping necessary variables in localized usage to ensure higher cache hits, the code will likely see improved performance.",
        "final_code": "#include <iostream>\n#define MOD 1000000007\n#define PI acos(-1.0)\ntypedef long long ll;\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(NULL);\n    cout.tie(NULL);\n    \n    string ans = \"\";\n    for(int i = 0; i < 3; i++) {\n        string s;\n        cin >> s;\n        ans += s[i];\n    }\n    cout << ans << endl;\n\n    return 0;\n}"
        }
    r1["entry2"] = {
            "k_iter": "3",
            "energy_improvement": 1.256,
            "runtime_improvement": 1.286,
            "cpu_cycles_improvement": 1.289,
            "memory_improvement": 88.233,
            "throughput_improvement": 1.286,
            "loc_improvement": 0.656,
            "optimization_pattern_name": "Eliminate data dependencies to promote ILP",
            "optimization_pattern_description": "Identify and eliminate data dependencies that hinder instruction-level parallelism, ensuring the code remains functionally correct. Loop unrolling is a common method to mitigate dependencies.",
            "optimization_rank": "3",
            "strategy": "1. **Eliminate Unnecessary Data Structures**: Remove the unused `vector<int> node[10001];`, which consumes unnecessary memory since it doesn't impact functionality.\n\n2. **Loop Unrolling for Instruction-Level Parallelism (ILP)**: Although the operation here is basic and loop unrolling may not necessarily produce benefits in this small context, if extended to similar multi-operation per loop contexts, unrolling would minimize separate executions integration in ILP pipelines.\n\n3. **Streamline Loop Execution**: Maintain streamlined operations by reading input and processing within the same loop to keep dependencies minimized and allow some level of perceived parallel execution.\n\nInventorize buffer structures in the case of similar iterative tasks to promote ILP by scheduling non-dependent parallel executions, adjusting to avoid resource dependency stalls.",
            "final_code": "#include <iostream>\n#define MOD 1000000007\n#define PI acos(-1.0)\ntypedef long long ll;\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(NULL);\n    cout.tie(NULL);\n    \n    string ans;\n    for (int i = 0; i < 3; i++) {\n        string s;\n        cin >> s;\n        ans += s[i];\n    }\n    cout << ans << endl;\n\n    return 0;\n}"
        }
    
    gen_content_dict = {
        "optimization_pattern_name": "testing",
        "optimization_pattern_description": "testing",
        "optimization_pattern_rank": "testing",
        "strategy": "testing",
        "final_code": "testing",
    }
    r1["entry3"] = failed_program_results(gen_content_dict=gen_content_dict)

    final_res = evaluate_results(r1, top_k)
    #print(json.dumps(final_res))
    pprint.pprint(final_res, width=80, compact=False)


if __name__ == "__main__":
    #r1 = {}
    #test_eval(r1, 2)
    main()