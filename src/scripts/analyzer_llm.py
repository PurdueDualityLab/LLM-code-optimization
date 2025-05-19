from dotenv import load_dotenv  
from pydantic import BaseModel  
import sys  
import os  
import json  
from jinja2 import Environment, FileSystemLoader  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import LLMAgent
from utils import Logger

# Setup environment  
load_dotenv()  
USER_PREFIX = os.getenv('USER_PREFIX')  
openai_key = os.getenv('API_KEY')
genai_api_key = os.getenv('GenAI_API_KEY')

class AnalysisResult(BaseModel):  
    analysis: str  
  
def analyze_optimization(original_code, optimized_code, llm_assistant):  
    
    print("Analyzing code optimization...")


    prompt =    f"""  
                I have two versions of a program: an original code and final optimized code. I want to evaluate the differences between the original code and the optimized code to identify any optimization techniques or decisions made in the optimized version. Please compare these codes in terms of:  
                Algorithmic changes: Are there any changes in the logic or approach used to solve the problem?  
                Performance improvements: Are there any changes that improve time complexity, space complexity, or runtime efficiency?  
                Redundant code removal: Has any unnecessary or redundant code been removed in the optimized version?  
                Other optimizations: Any other improvements or differences that are worth noting.  
                
                Here are the two versions of the code:  
                
                Original Code:  
                {original_code}  
                
                Final Optimized Code:  
                {optimized_code}  
                
                Output Structure:  
                First provide a brief description of what the code is doing.  
                Then provide a detailed comparison and highlight the specific optimizations or decisions made in the optimized version.  
                Lastly provide a precise bullet point summary of the optimizations.  
                """  

    
    # Send to LLM for analysis  
    llm_assistant.add_to_memory("user", prompt)  
    llm_assistant.generate_response(response_format=AnalysisResult)  
    response = llm_assistant.get_last_msg()  
      
    try:  
        if llm_assistant.is_genai_studio() or llm_assistant.is_openai_model():  
            content_dict = json.loads(response["content"])  
            analysis = content_dict["analysis"]  
        else:  
            analysis = AnalysisResult.model_validate_json(response["content"]).analysis  
        return analysis  
    except json.JSONDecodeError as e:  
        logger.error(f"Failed to decode JSON: {e}")  
        return "Error: Failed to analyze code optimization."  
  

if __name__ == "__main__":

    with open("original_code.txt", "r") as f:
        original_code = f.read()

    with open("optimized_code.txt", "r") as f:
        optimized_code = f.read()
    
    # Initialize LLM agent  
    analyzer_llm = LLMAgent(openai_api_key=openai_key, genai_api_key=genai_api_key,   
                            model="gpt-4o", use_genai_studio=False,   
                            system_message="You are a code expert. Analyze code optimizations thoroughly.")  
    
    # Analyze code optimization  
    analysis = analyze_optimization(original_code, optimized_code, analyzer_llm)  

    with open("analysis_result.txt", "w") as f:  
        f.write(analysis)
    print("Analysis result saved to analysis_result.txt")