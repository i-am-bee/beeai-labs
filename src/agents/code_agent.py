#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.agents.agent import Agent

load_dotenv()

class CodeAgent(Agent):
    """
    CodeAgent extends the Agent class that executes an arbitrary python code specifed in the code section of the agent difinition.
    """

    def __init__(self, agent: dict) -> None:
        """
        Initializes the agent with agent definitions.
        """
        super().__init__(agent)
        

    async def run(self, *args, context=None) -> str:
        """
        Runs the BeeAI agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """

        self.print(f"Running {self.agent_name} with {args}...\n")
        local = {"input": args}
        exec(self.agent_code, local)
        answer = local["input"]
        self.print(f"Response from {self.agent_name}: {answer}\n")        
        return local["input"]

    async def run_streaming(self, *args, context=None) -> str:
        """
        Runs the BeeAI agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """

        self.print(f"Running {self.agent_name} with {args}...\n")
        local = {"input": args}
        exec(self.agent_code, local)
        answer = local["input"]
        self.print(f"Response from {self.agent_name}: {answer}\n")        
        return local["input"]

