#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod

class Agent:
    """
    Abstract base class for running agents.
    """
    def __init__(self, agent:dict) -> None:
        """
        Initializes the AgentRunner with the given agent configuration.
        Args:
            agent_name (str): The name of the agent.
        """
        # TODO: Review which attributes belong in base class vs subclasses
        self.agent_name = agent["metadata"]["name"]
        self.agent_framework = agent["spec"]["framework"]
        self.agent_model = agent["spec"]["model"]

        self.agent_desc = agent["spec"]["description"]
        self.agent_instr = agent["spec"]["instructions"]
        self.agent_input = agent["spec"].get("input")
        self.agent_output = agent["spec"].get("output")
        self.instructions = f"{self.agent_instr} Input is expected in format: {self.agent_input}" if self.agent_input else self.agent_instr
        self.instructions = f"{self.instructions} Output must be in format: {self.agent_output}" if self.agent_output else self.instructions

    @abstractmethod
    def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """

    @abstractmethod
    def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
