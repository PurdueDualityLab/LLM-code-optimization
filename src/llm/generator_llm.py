from dotenv import load_dotenv
from pydantic import BaseModel
import sys
from utils import Logger
import json
import os

logger = Logger("logs", sys.argv[2]).logger
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
with open(f"{USER_PREFIX}/src/llm/llm_prompts/generator_prompt.txt", "r") as file:
    generator_prompt = file.read()

def llm_optimize(code, llm_assistant, evaluator_feedback):
    class Strategy(BaseModel):
        Pros: str
        Cons: str

    class OptimizationReasoning(BaseModel):
        analysis: str
        strategies: list[Strategy] 
        selected_strategy: str
        final_code: str

    prompt = generator_prompt + f"Here is the code to optimize, follow the instruction to provide the optimized code WHILE MAINTAINING IT'S FUNCTIONAL CORRECTNESS:\n{code}" + f"\n {evaluator_feedback}"
    
    logger.info(f"llm_optimize: Generator LLM Optimizing ....")
    
    thread_id = llm_assistant.create_thread()
    llm_output = llm_assistant.create_run(user_input=prompt, thread_id = thread_id, output_format=OptimizationReasoning)

    try:
        final_code = json.loads(llm_output)['final_code']
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return

    if final_code == "":
        logger.error("Error in llm completion")
        return
    
    return final_code

def handle_compilation_error(error_message, llm_assistant):
    class ErrorReasoning(BaseModel):
        analysis: str
        final_code: str
        
    compilation_error_prompt = f"""The code you returned failed to compile with the following error message: {error_message}. 
        Analyze the error message and explicitly identify the issue in the code that caused the compilation error. 
        Then, consider if there's a need to use a different optimization strategy to compile successfully or if there are code changes which can fix this implementation strategy.
        Finally, update the code accordingly and ensure it compiles successfully. Ensure that the optimized code is both efficient and error-free and return it. """   
        
    thread_id = llm_assistant.get_current_thread_id()
    llm_output = llm_assistant.create_run(user_input=compilation_error_prompt, thread_id = thread_id, output_format=ErrorReasoning)

    try:
        final_code = json.loads(llm_output)['final_code']
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return
        
    if final_code == "":
        logger.error("Error in llm completion")
        return

    return final_code 

