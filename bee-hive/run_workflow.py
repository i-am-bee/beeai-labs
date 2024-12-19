#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import yaml
import dotenv
from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall

dotenv.load_dotenv()


def parse_yaml(file_path):
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def load_agent(agent):
    with open("agent_store.json") as f:
        agent_store = json.load(f)
    return agent_store[agent]


def sequential_workflow(workflow):
    prompt = workflow_yaml["spec"]["template"]["prompt"]
    agents = workflow_yaml["spec"]["template"]["agents"]
    if workflow_yaml["spec"]["strategy"]["output"] and workflow_yaml["spec"]["strategy"]["output"] == "verbose":
        run_workflow = run_streaming_agent
    else:
        run_workflow = run_agent
    for agent in agents:
        prompt = run_workflow(agent['name'], prompt)
    return prompt


def run_agent(agent_name, prompt):
    print(f"🐝 Running {agent_name}...")
    agent_id = load_agent(agent_name)
    client = OpenAI(base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY"))
    assistant = client.beta.assistants.retrieve(agent_id)
    thread = client.beta.threads.create(messages=[{"role": "user", "content": str(prompt)}])
    run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value
    print(f"🐝 Response from {agent_name}: {answer}")
    return answer


def run_streaming_agent(agent_name, prompt):
    print(f"🐝 Running {agent_name}...")
    agent_id = load_agent(agent_name)
    client = OpenAI(base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY"))
    assistant = client.beta.assistants.retrieve(agent_id)
    thread = client.beta.threads.create(messages=[{"role": "user", "content": str(prompt)}])
    class EventHandler(AssistantEventHandler):
        """NOTE: Streaming is work in progress, not all methods are implemented"""

        def on_event(self, event: AssistantStreamEvent) -> None:
            print(f"event > {event.event}")

        def on_text_delta(self, delta, snapshot):
            print(delta.value, end="", flush=True)

        def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
            if delta.step_details.type != "tool_calls":
                print(f"{delta.step_details.type} > {getattr(delta.step_details, delta.step_details.type)}")

        def on_tool_call_created(self, tool_call: ToolCall) -> None:
            """Not implemented yet"""

        def on_tool_call_done(self, tool_call: ToolCall) -> None:
            """Not implemented yet"""
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value
    print(f"🐝 Response from {agent_name}: {answer}")
    return answer


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python run_workflow.py <yaml_file>')
        sys.exit(1)

    file_path = sys.argv[1]
    workflow_yaml = parse_yaml(file_path)
    runtime_strategy = workflow_yaml["spec"]["strategy"]["type"]

    if runtime_strategy == "sequence":
        result = sequential_workflow(workflow_yaml)
        print(f"🐝 Final answer: {result}")
    else:
        raise ValueError("Invalid workflow strategy type: ", runtime_strategy)
