from openai import OpenAI
import time

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


