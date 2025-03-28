#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os, dotenv
import asyncio
import requests
import json
from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall

from src.agents.agent import Agent

dotenv.load_dotenv()

class BeeAgent(Agent):
    """
    BeeAgent extends the Agent class to load and run a specific agent.
    """    
    
    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified Bee agent.
         
        Args:
            agent_name (str): The name of the agent. 
        """
        super().__init__(agent)
    
        url = f'{os.getenv("BEE_API")}/v1/assistants'
        payload_dict = {
            "tools": [
                {"type": "code_interpreter"},
                {"type": "system", "system": {"id": "web_search"}},
                {"type": "system", "system": {"id": "weather"}}
            ],
            "name": self.agent_name,
            "description": self.agent_desc,
            "instructions": self.instructions.strip(),
            "metadata": {},
            "model": self.agent_model,
            "agent": "bee",
            "top_p": 0.8,
            "temperature": 0.1
        }
        payload = json.dumps(payload_dict)
        headers = {
            'accept': "application/json",
            'Authorization': "Bearer sk-proj-testkey",
            'Content-Type': "application/json"
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        self.agent_id = response["id"]

    async def run(self, prompt: str) -> str:
        """
        Runs the bee agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        print(f"🐝 Running {self.agent_name}...\n")
        client = OpenAI(
            base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
        )
        # TODO: Unused currently
        assistant = client.beta.assistants.retrieve(self.agent_id)
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": str(prompt)}]
        )
        client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.agent_id
        )
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value
        print(f"🐝 Response from {self.agent_name}: {answer}\n")
        return answer

    def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """    
        print(f"🐝 Running {self.agent_name}...\n")
        client = OpenAI(
            base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
        )
        assistant = client.beta.assistants.retrieve(self.agent_id)
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": str(prompt)}]
        )

        class EventHandler(AssistantEventHandler):
            """NOTE: Streaming is work in progress, not all methods are implemented"""
    
            def on_event(self, event: AssistantStreamEvent) -> None:
                print(f"event > {event.event}")

            def on_text_delta(self, delta, snapshot):
                print(delta.value, end="", flush=True)

            def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
                if delta.step_details.type != "tool_calls":
                    print(
                        f"{delta.step_details.type} > {getattr(delta.step_details, delta.step_details.type)}"
                    )

            def on_tool_call_created(self, tool_call: ToolCall) -> None:
                """Not implemented yet"""

            def on_tool_call_done(self, tool_call: ToolCall) -> None:
                """Not implemented yet"""

        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=self.agent_id,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value
        print(f"🐝 Response from {self.agent_name}: {answer}\n")
        return answer

