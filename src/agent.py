from openai import OpenAI
import time
import subprocess
from utils import Logger
import sys
from ollama import Client
from pydantic import BaseModel

logger = Logger("logs", sys.argv[2]).logger

class LLMAgent:
    def __init__(self, api_key, model, system_message="You are a helpful assistant."):
        if not model:
            raise ValueError("A model must be specified when creating a LLM Agent.")
        self.model = model
        self.system_message=system_message
        self.memory = [{"role": "system", "content": system_message}]

        if self.is_openai_model():
            self.client = OpenAI(api_key=api_key)
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
            if (self.is_openai_model()):
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
        return self.model in ["gpt-4o", "o1"]

class OpenAIAssistant:
    def __init__(self, api_key: str, name: str, instructions: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.name = name
        self.instructions = instructions
        self.model = model
        self.current_thread = None

        # Create the assistant
        self.client = OpenAI(api_key=self.api_key)
        self.assistant = self.client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            model=self.model
        )

    def create_thread(self):
        thread = self.client.beta.threads.create()
        self.current_thread = thread
        return thread.id

    def get_current_thread_id(self):
        return self.current_thread.id

    def create_run(self, user_input: str, thread_id: int, output_format=None):
        if output_format is not None:
            response_format = response_format={
                    'type': 'json_schema',
                    'json_schema': 
                        {
                            "name":"whocares", 
                            "schema": output_format.model_json_schema()
                        }
                }
        else:
            response_format = None
        # Create and poll a run
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.assistant.id,
            instructions=user_input,
            response_format=response_format
        )

        # Poll until the run is completed
        while run.status != 'completed':
            time.sleep(2)  # Wait for 2 seconds before retrieving again
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Retrieve the message history
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        # Extract the final code or content
        output = messages.data[0].content[0].text.value

        return output
