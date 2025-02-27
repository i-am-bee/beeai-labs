# SPDX-License-Identifier: Apache-2.0

import importlib
import asyncio

from .agent import Agent

class CrewAIAgent(Agent):
    """
    CrewAIAgent extends the Agent class to load and run a specific CrewAI agent.
    """
    def __init__(self, agent: dict) -> str:
        """
        Initializes the workflow for the specified agent. 
        The executable code must be within $PYTHONPATH.
        Args:
            agent_name (dict): Agent Configuration
        Raises:
            Exception: If the agent cannot be loaded, an exception is raised with an error message.
        """

        super().__init__(agent)

        # TODO: Add additional properties later. for now using naming:
        #   <directory>.<filename>.<class>.<method> ie
        #   test.crewai_test.ColdWeatherCrew.activity_crew

        try:
            partial_agent_name, method_name = self.agent_name.rsplit(".", 1)
            module_name, class_name = partial_agent_name.rsplit(".", 1)
            my_module = importlib.import_module(module_name)
            # Get the class object
            self.crew_agent_class = getattr(my_module, class_name)
            # Instantiate the class
            self.instance = self.crew_agent_class()          
            self.method_name = method_name
        except Exception as e:
            print(f"Failed to load agent {self.agent_name}: {e}")
            raise(e)


    async def run(self, prompt: str) -> str:
        """
        Executes the CrewAI agent with the given prompt. The agent's `kickoff` method is called with the input.
       
        Args:
            prompt (str): The input to be processed by the agent. 
        Returns:
            Any: The output from the agent's `kickoff` method.
        Raises:
            Exception: If there is an error in retrieving or executing the agent's method.
        """
        print(f"Running CrewAI agent: {self.agent_name} with prompt: {prompt}")

        try:
            method = getattr(self.instance, self.method_name)
            output = method().kickoff({ 'prompt': prompt})
            return { 'prompt': output.raw }

        # TODO address error handling
        except Exception as e:
            print(f"Failed to kickoff crew agent: {self.agent_name}: {e}")
            raise(e)

    def run_streaming(self, prompt) ->str:
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
