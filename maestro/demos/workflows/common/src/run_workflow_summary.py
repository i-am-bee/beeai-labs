#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""
Trigger Bee-Hive Workflow using docopt

Usage:
  hive run workflow.yaml

Options:
  -h, --help    Show this screen.
"""
#  --prompt      Prompt input
# hive run workflow.yaml [--prompt=<prompt>]

import json
import os
import sys

import yaml
import dotenv
from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall
import ast
dotenv.load_dotenv()


def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def load_agent(agent):
    with open("agent_store.json") as f:
        agent_store = json.load(f)
    return agent_store[agent]


def sequential_workflow(workflow):
    prompt = workflow_yaml["spec"]["template"]["prompt"]
    agents = workflow_yaml["spec"]["template"]["agents"]
    if (
        workflow_yaml["spec"]["strategy"]["output"]
        and workflow_yaml["spec"]["strategy"]["output"] == "verbose"
    ):
        run_workflow = run_streaming_agent
    else:
        run_workflow = run_agent
    for agent in agents:
        prompt = run_workflow(agent, prompt)
    return prompt


def sequential_workflow_for_demo(workflow):
    """
    Custom sequential workflow for the ArXiv summarization demo.
    Identical to sequential_workflow(), except Summary iterates over a list.
    """
    prompt = workflow["spec"]["template"]["prompt"]
    agents = workflow["spec"]["template"]["agents"]
    if (
        workflow_yaml["spec"]["strategy"]["output"]
        and workflow_yaml["spec"]["strategy"]["output"] == "verbose"
    ):
        run_workflow = run_streaming_agent
    else:
        run_workflow = run_agent
    for agent in agents:
        if agent == "Individual Summary":
            if isinstance(prompt, str) and prompt.startswith(("{", "[")):
                prompt = ast.literal_eval(prompt)
            else:
                print('Filter agent failed')
            for title in prompt:
                summary_prompt = f"Summarize the paper: {title}"
                summary = run_workflow(agent, summary_prompt)
                print(f"Summary of {title}: {summary}")
        else:
            prompt = run_workflow(agent, prompt)

    return prompt


def sequential_workflow_for_summary(workflow):
    """
    Custom sequential workflow for the ArXiv summarization demo.
    Introduces an interactive user selection step before summary generation.
    """
    prompt = workflow["spec"]["template"]["prompt"]
    agents = workflow["spec"]["template"]["agents"]

    if (
        workflow["spec"]["strategy"]["output"]
        and workflow["spec"]["strategy"]["output"] == "verbose"
    ):
        run_workflow = run_streaming_agent
    else:
        run_workflow = run_agent

    for agent in agents:
        print(f"\n🐝 Executing Agent: {agent}...\n")
        if agent == "Search Arxiv":
            prompt = run_workflow(agent, prompt)
            if isinstance(prompt, str) and prompt.startswith(("{", "[")):
                paper_titles = ast.literal_eval(prompt)
            else:
                print("❌ Error: Search ArXiv did not return a valid list of titles.")
                return

            print("\n🔍 **Recent ArXiv Papers on Your Topic:**")
            for i, title in enumerate(paper_titles):
                print(f"{i + 1}. {title}")

            while True:
                user_input = input("\n💡 Enter the numbers of the papers you want to summarize (comma-separated): ").strip()
                selected_indices = [int(x) - 1 for x in user_input.split(",") if x.isdigit() and 0 <= int(x) - 1 < len(paper_titles)]
                
                if selected_indices:
                    selected_titles = [paper_titles[i] for i in selected_indices]
                    print(f"\n✅ Selected Titles for Summary: {selected_titles}\n")
                    prompt = selected_titles
                    break
                else:
                    print("❌ Invalid selection. Please enter valid numbers separated by commas.")

        elif agent == "Individual Summary":
            if isinstance(prompt, list):
                for title in prompt:
                    summary_prompt = f"Summarize the paper: {title}"
                    summary = run_workflow(agent, summary_prompt)
                    print(f"📜 **Summary of {title}:**\n{summary}\n")
            else:
                print("❌ Error: No valid titles selected for summary.")
                return

        else:
            prompt = run_workflow(agent, prompt)

    return prompt


def run_agent(agent_name, prompt):
    print(f"🐝 Running {agent_name}...")
    agent_id = load_agent(agent_name)
    client = OpenAI(
        base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
    )
    assistant = client.beta.assistants.retrieve(agent_id)
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": str(prompt)}]
    )
    client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value
    print(f"🐝 Response from {agent_name}: {answer}")
    return answer


def run_streaming_agent(agent_name, prompt):
    print(f"🐝 Running {agent_name}...")
    agent_id = load_agent(agent_name)
    client = OpenAI(
        base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
    )
    assistant = client.beta.assistants.retrieve(agent_id)
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
        assistant_id=assistant.id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value
    print(f"🐝 Response from {agent_name}: {answer}")
    return answer


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_workflow.py <yaml_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    workflow_yaml = parse_yaml(file_path)
    runtime_strategy = workflow_yaml["spec"]["strategy"]["type"]

    if runtime_strategy == "sequence":
        # note: change function here based on demo
        result= sequential_workflow_for_summary(workflow_yaml)
        print(f"🐝 Final answer: {result}")
    else:
        raise ValueError("Invalid workflow strategy type: ", runtime_strategy)