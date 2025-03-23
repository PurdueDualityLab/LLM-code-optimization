from dotenv import load_dotenv
from pydantic import BaseModel
import sys
from utils import Logger
import json
import os

logger = Logger("logs", sys.argv[2]).logger
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
with open(f"{USER_PREFIX}/src/llm/llm_prompts/generator_prompt_topk.txt", "r") as file:
    generator_prompt = file.read()

def llm_optimize(code, llm_assistant, evaluator_feedback, optimization_pattern, ast):
    # use the pattern corresponding to current value of k_iter

    #class Strategy(BaseModel):
    #    Strategy: str
    #    Pros: str
    #    Cons: str

    class OptimizationReasoning(BaseModel):
        analysis: str
        #optimization_opportunities: str
        #strategies: list[Strategy] 
        strategy: str
        final_code: str
        optimization_pattern_name: str
        optimization_pattern_description: str
        optimization_pattern_rank: str
    
    # add optimization pattern to prompt
    updated_generator_prompt = generator_prompt.replace('{optimization_pattern}', optimization_pattern)

    if evaluator_feedback == "":
        prompt = updated_generator_prompt + f"Here is the code to optimize, follow the instruction to provide the optimized code WHILE MAINTAINING IT'S FUNCTIONAL EQUIVALENCE:\n{code}.\n" + f"Here is the AST of the source code: {ast}"
    else:
        prompt = f"The code you generated did not improve performance, please reoptimize WHILE MAINTAINING IT'S FUNCTIONAL CORRECTNESS. Here are some feedbacks: {evaluator_feedback}.\n Original code to optimize:\n {code}"
    
    logger.info(f"llm_optimize: Generator LLM Optimizing ....")
    
    if llm_assistant.is_genai_studio():
        prompt = prompt + "\n Strictly only output final code only."

    llm_assistant.add_to_memory("user", prompt)
    llm_assistant.generate_response(OptimizationReasoning)

    response = llm_assistant.get_last_msg()
    logger.info(response)
    
    try:
        if llm_assistant.is_genai_studio():
            final_code = response["content"]
        elif (llm_assistant.is_openai_model()):
            content_dict = json.loads(response["content"])
            final_code = content_dict["final_code"]
        else:
            final_code = OptimizationReasoning.model_validate_json(response["content"]).final_code
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return

    if final_code == "":
        logger.error("Error in llm completion")
        return
    
    #need to return more than just final code for top_k.
    #will just return dictionary to keep it simple.
    #looking at the code above (line53-54) this will not work with genai_studo, this will only work with openai_model.
    return content_dict

def handle_compilation_error(error_message, llm_assistant):
    class ErrorReasoning(BaseModel):
        analysis: str
        final_code: str
    
    # removing the sentence on considering different optimizations for Top-K accuracy test.
    compilation_error_prompt = f"""The code you returned failed to compile with the following error message: {error_message}. 
        Analyze the error message and explicitly identify the issue in the code that caused the compilation error. 
        Then, consider if there are code changes which can fix this implementation.
        Finally, update the code accordingly and ensure it compiles successfully.
        Ensure that the optimized code is both efficient and error-free and return it. """   
        
    if llm_assistant.is_genai_studio():
        compilation_error_prompt = compilation_error_prompt + "\n Strictly only output final code only."
    
    llm_assistant.add_to_memory("user", compilation_error_prompt)
    llm_assistant.generate_response(ErrorReasoning)
    response = llm_assistant.get_last_msg()

    try:
        if llm_assistant.is_genai_studio():
            final_code = response["content"]
        elif (llm_assistant.is_openai_model()):
            content_dict = json.loads(response["content"])
            final_code = content_dict["final_code"]
        else:
            final_code = ErrorReasoning.model_validate_json(response["content"])["final_code"]
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return
        
    if final_code == "":
        logger.error("Error in llm completion")
        return

    return final_code 

