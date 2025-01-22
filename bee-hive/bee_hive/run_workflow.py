#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys
import importlib
        
import yaml
import dotenv

from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall

from abc import ABC, abstractmethod

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
    """
    Abstract base class for running agents.
    """

    def __init__(self, agent_name):
        """
        Initializes the AgentRunner with the given agent name.
        Args:
            agent_name (str): The name of the agent.
        """
        self.agent_name = agent_name

    @abstractmethod
    def run(self, prompt):
        """
        Runs the agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """

        pass
    
    @abstractmethod
    def stream(self, prompt):
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        pass
    
class CrewAIAgentRunner(AgentRunner):
    """
    CrewAIAgentRunner extends the AgentRunner class to load and run a specific CrewAI agent.
    """
    def __init__(self, agent_name):
        """
        Initializes the workflow for the specified agent. 
        The executable code must be within $PYTHONPATH.
        Args:
            agent_name (str): The name of the agent in the format 
                              <directory>.<filename>.<class>.<method> where 'crewai_' 
                              must appear in the name, e.g., test.crewai_test.ColdWeatherCrew.activity_crew.
        Raises:
            Exception: If the agent cannot be loaded, an exception is raised with an error message.
        """
        
        super().__init__(agent_name)
        
        # load python module based on name
        # TODO: improve configuration - current requirement is to have the agent name in the format:
        #   <directory>.<filename>.<class>.<method> where 'crewai_' must appear in the name ie
        #   test.crewai_test.ColdWeatherCrew.activity_crew
        
        try:
            partial_agent_name, method_name = agent_name.rsplit(".", 1)
            module_name, class_name = partial_agent_name.rsplit(".", 1)
            my_module = importlib.import_module(module_name)
            # Get the class object
            self.crew_agent_class = getattr(my_module, class_name)
            # Instantiate the class
            self.instance = self.crew_agent_class()            
            self.method_name = method_name
        except Exception as e:
            print(f"Failed to load agent {agent_name}: {e}")
            raise(e)


    def run(self, prompt):
        """
        Executes the CrewAI agent with the given prompt. The agent's `kickoff` method is called with the input.
       
        Args:
            prompt (str): The input to be processed by the agent. This must be in JSON format ie {"key": "value"}.
        Returns:
            Any: The output from the agent's `kickoff` method.
        Raises:
            Exception: If there is an error in retrieving or executing the agent's method.
        """
        print(f"Running CrewAI agent: {self.agent_name} with prompt: {prompt}")
        
        try:

            method = getattr(self.instance, self.method_name)
            output = method().kickoff(inputs=prompt)
            # TODO: Still need to figure out return
            return output
    
        except Exception as e:
            print(f"Failed to kickoff crew agent: {self.agent_name}: {e}")
            raise(e)
    
    def stream(self, prompt):
        """
        Streams the execution of the CrewAI agent with the given prompt.
        This is NOT YET IMPLEMENTED

        Args:
            prompt (str): The input prompt to be processed by the CrewAI agent.

        Raises:
            NotImplementedError: Indicates that the CrewAI agent execution logic is not yet implemented.
        """
        print(f"Running CrewAI agent (streaming): {self.agent_name} with prompt: {prompt}")

        raise NotImplementedError("CrewAI agent execution logic not implemented yet")
        
class LangGraphAgentRunner(AgentRunner):
    """
    LangGraphAgentRunner extends the AgentRunner class to load and run a specific LangGraph agent.
    """
    def __init__(self, agent_name):
        """
        Initialize a new instance.
        Args:
            agent_name (str): The name of the agent to be initialized.
        """
        
        super().__init__(agent_name)
        # Initialize LangGraph-specific resources here

    def run(self, prompt):
        """
        Executes the LangGraph agent with the given prompt.
        This is NOT YET IMPLEMENTED

        Args:
            prompt (str): The input prompt to be processed by the LangGraph agent.

        Raises:
            NotImplementedError: If the LangGraph agent execution logic is not implemented yet.
        """

        print(f"Running LangGraph agent: {self.agent_name} with prompt: {prompt}")
        # Implement LangGraph agent execution logic here
        # workflow = StateGraph(...) << not yet used by sample, can refactor as this is normal way of launching
        raise NotImplementedError("LangGraph agent execution logic not implemented yet")
    
    def stream(self, prompt):
        """
        Executes the LangGraph agent with the given prompt in streaming mode.
        This is NOT YET IMPLEMENTED

        Args:
            prompt (str): The input prompt to be processed by the LangGraph agent.

        Raises:
            NotImplementedError: If the LangGraph agent execution logic is not implemented yet.
        """
        print(f"Running LangGraph agent (streaming): {self.agent_name} with prompt: {prompt}")
        # Implement LangGraph agent execution logic here
        # workflow = StateGraph(...) << not yet used by sample, can refactor as this is normal way of launching
        raise NotImplementedError("LangGraph agent execution logic not implemented yet")
        
class BeeAgentRunner(AgentRunner):
    """
    BeeAgentRunner extends the AgentRunner class to load and run a specific Bee agent.
    """

    def __init__(self, agent_name):
        """
        Initializes the workflow for the specified agent.
        
        Args:
            agent_name (str): The name of the agent. This should already be defined in agents.yaml and hive run with 'hive create -f agents.yaml'
        """
        super().__init__(agent_name)
        # Initialize Bee-specific resources here

    def run(self, prompt):
        """
        Executes the Bee agent with the given prompt. 
       
        Args:
            prompt (str): The input to be processed by the agent. 
        Returns:
            Any: The output from the agent.
        """
        print(f"Running Bee agent: {self.agent_name} with prompt: {prompt}")

        # delegate to existing implementation
        # TODO: Refactor bee code to be more modular
        result=run_agent(self.agent_name, prompt)
        return result
    
    def stream(self, prompt):
        """
        Executes the Bee agent with the given prompt in streaming mode. 
       
        Args:
            prompt (str): The input to be processed by the agent. 
        Returns:
            Any: The output from the agent.
        """
        print(f"Running Bee agent (streaming): {self.agent_name} with prompt: {prompt}")

        # delegate to existing implementation
        result=run_streaming_agent(self.agent_name, prompt)
        return result
        
# --- Agent Runner Factory ---

class AgentRunnerFactory:
    @staticmethod
    class AgentRunnerFactory:
        """
        Factory class for creating agent runners based on the agent's name.
        
        The following agent types are supported: CrewAIUI, LangGraph, Bee.
        """
        
    def create_agent_runner(agent_name):
        """
        Creates and returns an agent runner based on the provided agent name.
        The function determines the type of agent runner to create based on the 
        prefix of the agent name. It supports three types of agent runners:
        - CrewAIAgentRunner: for agent names starting with "crewai_"
        - LangGraphAgentRunner: for agent names starting with "langgraph_"
        - BeeAgentRunner: for all other agent names
        Args:
            agent_name (str): The name of the agent for which to create a runner.
        Returns:
            An instance of the appropriate agent runner class based on the agent name.
        Raises:
            ValueError: If the agent name does not match any known agent framework.
        """
        
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

            if ( workflow_yaml["spec"]["strategy"]["output"]
                 and 
                 workflow_yaml["spec"]["strategy"]["output"] == "verbose" ):
                prompt = agent_runner.stream(prompt)
            else:
                prompt = agent_runner.run(prompt)                
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
