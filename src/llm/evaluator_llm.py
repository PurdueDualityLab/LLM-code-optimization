from dotenv import load_dotenv
from utils import Logger
import sys
import os
from pydantic import BaseModel
import json

logger = Logger("logs", sys.argv[2]).logger
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
with open(f"{USER_PREFIX}/src/llm/llm_prompts/evaluator_prompt.txt", "r") as file:
    evaluator_prompt = file.read()

class Feedback(BaseModel):
    feedback: str

def evaluator_llm(evaluator_feedback_data, llm_assistant):

    #extract original
    original_source_code = evaluator_feedback_data["original"]["source_code"]
    original_avg_runtime = evaluator_feedback_data["original"]["avg_runtime"]

    lowest_source_code = evaluator_feedback_data["max_avg_speedup"]["source_code"]
    lowest_avg_runtime = evaluator_feedback_data["max_avg_speedup"]["avg_speedup"]

    current_source_code = evaluator_feedback_data["current"]["source_code"]  
    current_avg_runtime = evaluator_feedback_data["current"]["avg_speedup"]

    prompt = evaluator_prompt + f"""
    Here is the original code snippet:
    ```
    {original_source_code}
    ```
    Average runtime in ms: {original_avg_runtime}

    Here is the previous optimized code snippets with highest speedup:
    ```
    {lowest_source_code}
    ```
    Average speedup: {lowest_avg_runtime}

    Here is the code snippiets that you are tasked to optimize:
    ```
    {current_source_code}
    ```
    Average speedup: {current_avg_runtime}

    Please respond in natural language (English) with actionable suggestions for improving the current code's performance. Provide only the best code with the lowest runtime.
    """

    llm_assistant.add_to_memory("user", prompt)
    llm_assistant.generate_response(response_format=Feedback)
    response = llm_assistant.get_last_msg()

    try:
        if llm_assistant.is_genai_studio():
            feedback = response["content"]
        elif llm_assistant.is_openai_model():
            content_dict = json.loads(response["content"])
            feedback = content_dict["feedback"]
        else:
            feedback = Feedback.model_validate_json(response["content"]).feedback
        return feedback
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return