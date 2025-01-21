#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import dotenv
from openai import OpenAI
import yaml

dotenv.load_dotenv()
from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall

class Agent:
    agent_id = ""
    agent_tools = []
    
    def __init__(self, agent):
        client = OpenAI(
            base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
        )

        self.agent_name = agent["metadata"]["name"]
        self.agent_model = agent["spec"]["model"]
        self.agent_desc = agent["spec"]["description"]
        self.agent_instr = agent["spec"]["instructions"]
        self.agent_input = agent["spec"].get("input")
        self.agent_output = agent["spec"].get("output")
        self.agent_tools = []

        tools = agent["spec"].get("tools")
        if tools:
            for tool in tools:
                if tool == "code_interpreter":
                    self.agent_tools.append({"type": tool})
                else:
                    print(f"Enable the {tool} tool in the Bee UI")

        instructions = f"{agent_instr} Input is expected in format: {self.agent_input}" if self.agent_input else self.agent_instr
        instructions = f"{instructions} Output must be in format: {self.agent_output}" if self.agent_output else instructions
        assistant = client.beta.assistants.create(
            name=self.agent_name,
            model=self.agent_model,
            description=self.agent_desc,
            tools=self.agent_tools,
            instructions=instructions,
        )

        self.agent_id = assistant.id


    def run(self, prompt):
        print(f"🐝 Running {self.agent_name}...")
        client = OpenAI(
            base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
        )
        assistant = client.beta.assistants.retrieve(self.agent_id)
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": str(prompt)}]
        )
        client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.agent_id
        )
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value
        print(f"🐝 Response from {self.agent_name}: {answer}")
        return answer

    def run_streaming(self, prompt):
        print(f"🐝 Running {self.agent_name}...")
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
        print(f"🐝 Response from {self.agent_name}: {answer}")
        return answer

