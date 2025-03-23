from dotenv import load_dotenv
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

def rank_patterns(llm_assistant, source_code):
    class Pattern(BaseModel):
        pattern_name: str
        pattern_description: str
        pattern_example: str
        rank: str

    class PatternSelection(BaseModel):
        patterns: list[Pattern]

    # get patterns from pattern catalog
    # patterns is in JSON format
    patterns = get_patterns(file_path=energy_patterns)

    # update prompt with patterns & source code
    updated_prompt = advisor_prompt.replace('{patterns}', patterns).replace('{source_code}', source_code)

    # inference with LLM
    logger.info(f"filter patterns: Advisor LLM filtering patterns ....")
    llm_assistant.add_to_memory("user", updated_prompt)
    if llm_assistant.generate_response(response_format=PatternSelection) != 1:
        return -1
    response = llm_assistant.get_last_msg()
    if response == None:
        return -1
    logger.info(response)

    # return dictionary
    # using for top_k_test
    try:
        if(llm_assistant.is_openai_model()):
            content_dict = json.loads(response["content"])
            return content_dict
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")

    # format string response
    #try:
    #    if (llm_assistant.is_openai_model()):
    #        content_dict = json.loads(response["content"])
    #        patterns = "\n".join(
    #            f"{entry['pattern_name']}:\nDescription:{entry['pattern_description']}\nExample:{entry['pattern_example']}\nRank:{entry['rank']}"
    #            for entry in content_dict["patterns"]
    #        )
    #    else:
    #        #TODO Need to fix patterns assignment below.
    #        patterns = [entry.pattern_name for entry in PatternSelection.model_validate_json(response["content"]).patterns]
    #    return patterns
    #except json.JSONDecodeError as e:
    #    logger.error(f"Failed to decode JSON: {e}")
    #    return
