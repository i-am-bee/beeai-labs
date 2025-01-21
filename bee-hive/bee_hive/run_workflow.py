#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys
import importlib
        
from click import prompt
import yaml
import dotenv

from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall

from abc import ABC, abstractmethod
import re

dotenv.load_dotenv()


def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def load_agent(agent):
    with open("agent_store.json") as f:
        agent_store = json.load(f)
    return agent_store[agent]

# --- Abstract Base Class for Agent Runners ---
class AgentRunner(ABC):
    def __init__(self, agent_name):
        self.agent_name = agent_name

    @abstractmethod
    def run(self, prompt):
        """Runs the agent with the given prompt."""
        pass
    
    @abstractmethod
    def stream(self, prompt):
        """Runs the agent in streaming mode with the given prompt."""
        pass
    
class CrewAIAgentRunner(AgentRunner):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        # load python module based on name
        # TODO: improve flex. for now agent_name should be the module + classname (which must begin with crewai_)
        # For example:
        #   crewai_things_to_do_cold_weather.ColdWeatherCrew
        try:
            module_name, class_name = agent_name.rsplit(".", 1)
            my_module = importlib.import_module(module_name)
            # Get the class object
            self.crew_agent_class = getattr(my_module, class_name)

            # Instantiate the class
            self.instance = self.crew_agent_class()
        except Exception as e:
            print(f"Failed to load agent {agent_name}: {e}")
            raise(e)


    def run(self, prompt):
        print(f"Running CrewAI agent: {self.agent_name} with prompt: {prompt}")
        # Implement CrewAI agent execution logic here
        # crew = Crew(agent_name, ...)
        # crew.kickoff() << this is how we kick it off in the sample code. Note could be additional tasks
        
        # TODO: We get called with prompt='New York' or similar. test agent needs { "location": "New York" }
        #prompt2  = { "location": prompt }
        try: 
            # TODO: need to lookup method to call - base don agent name?
            self.instance.activity_crew().kickoff(prompt)
        except Exception as e:
            print(f"Failed to kickoff crew agent: {self.agent_name}: {e}")
            raise(e)
    
    def stream(self, prompt):
        print(f"Running CrewAI agent (streaming): {self.agent_name} with prompt: {prompt}")

        raise NotImplementedError("CrewAI agent execution logic not implemented yet")
        
class LangGraphAgentRunner(AgentRunner):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        # Initialize LangGraph-specific resources here

    def run(self, prompt):
        print(f"Running LangGraph agent: {self.agent_name} with prompt: {prompt}")
        # Implement LangGraph agent execution logic here
        # workflow = StateGraph(...) << not yet used by sample, can refactor as this is normal way of launching
        raise NotImplementedError("LangGraph agent execution logic not implemented yet")
    
    def stream(self, prompt):
        print(f"Running LangGraph agent (streaming): {self.agent_name} with prompt: {prompt}")
        # Implement LangGraph agent execution logic here
        # workflow = StateGraph(...) << not yet used by sample, can refactor as this is normal way of launching
        raise NotImplementedError("LangGraph agent execution logic not implemented yet")
        
class BeeAgentRunner(AgentRunner):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        # Initialize Bee-specific resources here

    def run(self, prompt):
        print(f"Running Bee agent: {self.agent_name} with prompt: {prompt}")

        # delegate to existing implementation
        # TODO: Refactor bee code to be more modular
        result=run_agent(self.agent_name, prompt)
        return result
    
    def stream(self, prompt):
        print(f"Running Bee agent (streaming): {self.agent_name} with prompt: {prompt}")

        # delegate to existing implementation
        result=run_streaming_agent(self.agent_name, prompt)
        return result
        
# --- Agent Runner Factory ---

class AgentRunnerFactory:
    @staticmethod
    def create_agent_runner(agent_name):
        """Creates an agent runner based on the agent's name."""
        # TODO: May want to discover agent type, or define in workflow
        if "crewai_" in agent_name:
            return CrewAIAgentRunner(agent_name)
        elif "langgraph_" in agent_name:
            return LangGraphAgentRunner(agent_name)
        else:
        #elif re.match(r"^[a-zA-Z]+$", agent_name):
            return BeeAgentRunner(agent_name)
        #else:
            #raise ValueError(f"Unknown agent framework for agent: {agent_name}")
        
def sequential_workflow(workflow):
    prompt = workflow_yaml["spec"]["template"]["prompt"]
    agents = workflow_yaml["spec"]["template"]["agents"]

    for agent in agents:
        try:
            agent_runner = AgentRunnerFactory.create_agent_runner(agent["name"])
            # TODO: reinstate streaming support
            #prompt=agent_runner.stream(prompt) if( workflow_yaml["spec"]["strategy"]["streaming"] and workflow_yaml["spec"]["strategy"]["output"] == "verbose" ) else agent_runner.run(prompt)
            agent_runner.run(prompt)
        except ValueError as e:
            print(e)
            raise(e)

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
        result = sequential_workflow(workflow_yaml)
        print(f"🐝 Final answer: {result}")
    else:
        raise ValueError("Invalid workflow strategy type: ", runtime_strategy)
