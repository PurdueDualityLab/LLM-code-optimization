from openai import OpenAI
import time
import subprocess
from utils import Logger
import sys
from ollama import Client
from pydantic import BaseModel
import requests
import json

logger = Logger("logs", sys.argv[2]).logger

class LLMAgent:
    def __init__(self, openai_api_key, genai_api_key, model, use_genai_studio, system_message="You are a helpful assistant."):
        if not model:
            raise ValueError("A model must be specified when creating a LLM Agent.")
        self.model = model
        self.system_message=system_message
        self.memory = [{"role": "system", "content": system_message}]
        self.use_genai_studio = use_genai_studio
        self.genai_api_key = genai_api_key

        if self.is_openai_model():
            self.client=OpenAI(api_key=openai_api_key)
        elif use_genai_studio:
            self.client=OpenAI(
                base_url="https://genai.rcac.purdue.edu/api",
                api_key=genai_api_key)
        else:
            try:
                subprocess.run(["ollama", "pull", model], check=True)
            except Exception as e:
                logger.error(f"Error pulling model from ollama: {e}")
                sys.exit(1)
            else:
                self.client = Client(host="http://localhost:11434")
    
    def add_to_memory(self, role, content):
        self.memory.append({"role": role, "content": content})
    
    def generate_response(self, response_format=BaseModel):
        try:
            if self.is_openai_model() or self.use_genai_studio:
                response = self.client.beta.chat.completions.parse(
                    model = self.model,
                    messages = self.memory,
                    response_format=response_format
                )
                content = response.choices[0].message.content
            else:
                response = self.client.chat(model=self.model, messages=self.memory, format=response_format.model_json_schema())
                content = response.message.content
        except Exception as e:
            logger.error(f"Error when generating response: {e}")
            return -1
        self.add_to_memory("assistant", content)
        return 1
    
    def get_last_msg(self):
        if self.memory:
            return self.memory[-1]
        return None
    
    def get_memory(self):
        return self.memory
    
    def clear_memory(self):
        self.memory = [{"role": "system", "content": self.system_message}]
    
    def is_openai_model(self):
        return self.model in ["gpt-4o", "o1", "o3-mini"]
    
    def is_genai_studio(self):
        return self.use_genai_studio
