from dotenv import load_dotenv
from agent import LLMAgent
from pydantic import BaseModel
from utils import Logger
import json
import sys
import os

logger = Logger("logs", sys.argv[2]).logger
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
with open(f"{USER_PREFIX}/src/llm/llm_prompts/pattern_prompt.txt", "r") as file:
    pattern_prompt = file.read()

def filter_patterns(llm_assistant, source_code):
    class Feedback(BaseModel):
        feedback: str

    # add source_code to energy optimization prompt
    updated_prompt = pattern_prompt.replace('{source_code}', source_code)

    # inference with LLM
    llm_assistant.add_to_memory("user", updated_prompt)
    if llm_assistant.generate_response(response_format=Feedback) != 1:
        return -1
    response = llm_assistant.get_last_msg()
    if response == None:
        return -1
    
    # format response (taken from evaluator_llm--should suffice for now)
    try:
        if (llm_assistant.is_openai_model()):
            content_dict = json.loads(response["content"])
            feedback = content_dict["feedback"]
        else:
            feedback = Feedback.model_validate_json(response["content"]).feedback
        return feedback
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return

#TODO: prompt refinement
def pattern_refinement():
    pass