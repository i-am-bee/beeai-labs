#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os

import dotenv
from openai import AssistantEventHandler, OpenAI
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCall

from bee_hive.agent import Agent

dotenv.load_dotenv()

class MockAgent(Agent):
    """
    MockAgent extends the Agent class to load and run a specific agent.
    """    
    
    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified Bee agent.
         
        Args:
            agent_name (str): The name of the agent. 
        """
        super().__init__(agent)
    
        client = OpenAI(
            base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
        )
        
        self.agent_tools = []

        tools = agent["spec"].get("tools")
        if tools:
            for tool in tools:
                print(f"Mock agent:Loading {tool}")

        print(f"Mock agent: name={self.agent_name}, model={self.agent_model}, description={self.agent_desc}, tools={self.agent_tools}, instructions={self.instructions}")
        self.agent_id = self.agent_name

    def run(self, prompt: str) -> str:
        """
        Runs the bee agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        print(f"🐝 Running {self.agent_name}...")
        answer = f"Mock agent: answer for {prompt}" 
        print(f"🐝 Response from {self.agent_name}: {answer}")
        return answer

    def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """    
        print(f"🐝 Running {self.agent_name}...")
        answer = f"Mock agent: answer for {prompt}" 
        print(f"🐝 Response from {self.agent_name}: {answer}")
        return answer

