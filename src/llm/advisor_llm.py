from dotenv import load_dotenv
from agent import LLMAgent
from pydantic import BaseModel
from utils import Logger
from scripts.read_pattern_cat import get_patterns
import json
import sys
import os

logger = Logger("logs", sys.argv[2]).logger
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
energy_patterns = f"{USER_PREFIX}/pattern_catalog/energy_patterns.xlsx"
with open(f"{USER_PREFIX}/src/llm/llm_prompts/advisor_prompt.txt", "r") as file:
    advisor_prompt = file.read()

def filter_patterns(llm_assistant, source_code):
    class Strategy(BaseModel):
        optimization_pattern: str
        prompt: str

    class PromptSelection(BaseModel):
        prompts: list[Strategy]

    # get patterns from pattern catalog
    # patterns is in JSON format
    patterns = get_patterns(file_path=energy_patterns)

    # update prompt with patterns & source code
    updated_prompt = advisor_prompt.replace('{patterns}', patterns).replace('{source_code}', source_code)

    # inference with LLM
    logger.info(f"filter patterns: Advisor LLM filtering patterns ....")
    llm_assistant.add_to_memory("user", updated_prompt)
    if llm_assistant.generate_response(response_format=PromptSelection) != 1:
        return -1
    response = llm_assistant.get_last_msg()
    if response == None:
        return -1
    logger.info(response)

    # format response
    try:
        if (llm_assistant.is_openai_model()):
            content_dict = json.loads(response["content"])
            prompts = "\n".join(
                f"{entry['optimization_pattern']}: {entry['prompt']}\n"
                for entry in content_dict["prompts"]
            )
            #prompts = content_dict["prompts"]
        else:
            #TODO
            prompts = [entry.prompt for entry in PromptSelection.model_validate_json(response["content"]).prompts]
        return prompts
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return

#TODO: prompt refinement
def pattern_refinement():
    pass
