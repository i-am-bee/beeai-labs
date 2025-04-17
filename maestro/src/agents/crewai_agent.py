# SPDX-License-Identifier: Apache-2.0

import importlib
import asyncio

# from crewai import Agent, Crew, Task, Process, LLM
from .agent import Agent as BeeAgent

class CrewAIAgent(BeeAgent):
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
            self.module_name = agent["metadata"]["labels"].get("module")
            if self.module_name:
                self.class_name = agent["metadata"]["labels"]["class"]
                self.factory_name = agent["metadata"]["labels"]["factory"]
            else:
                self.provider_url = agent["spec"].get("url")
                self.crew_role = agent["metadata"]["labels"].get("crew_role")
                self.crew_goal = agent["metadata"]["labels"].get("crew_goal")
                self.crew_backstory = agent["metadata"]["labels"].get("crew_backstory")
                self.crew_description = agent["metadata"]["labels"].get("crew_description")
                self.crew_expected_output = agent["metadata"]["labels"].get("crew_expected_output")
        except Exception as e:
            print(f"🧑🏽‍✈️ Failed to load agent {self.agent_name}: {e}")
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
        print(f"🧑🏽‍✈️ RunningCrewAI agent: {self.agent_name} with prompt: {prompt}\n")

        try:
            if self.module_name:
                my_module = importlib.import_module(self.module_name)
                # Get the class object
                self.crew_agent_class = getattr(my_module, self.class_name)
                # Instantiate the class
                self.instance = self.crew_agent_class()
                factory = getattr(self.instance, self.factory_name)
                output = factory().kickoff({ 'prompt': prompt})
            else:
                # output = self.crew().kickoff({ 'prompt': prompt})
                print(f"Not implemeted\n")
                return(f"Not implemeted\n")
            print(f"🐝 Response from {self.agent_name}: {output.raw}\n")
            return { 'prompt': output.raw }

        # TODO address error handling
        except Exception as e:
            print(f"🧑🏽‍✈️ Failed to kickoff crew agent: {self.agent_name}: {e}\n")
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
        print(f"🧑🏽‍✈️Running CrewAI agent (streaming): {self.agent_name} with prompt: {prompt}\n")

        raise NotImplementedError("🧑🏽‍✈️CrewAI agent execution logic not implemented yet")

#    def agent(self) -> Agent:
#        llm = LLM(
#            model = self.agent_model,
#            base_url = self.provider_url
#        )
#        return Agent(
#            role = self.crew_role,
#            goal = self.crew_goal,
#            backstory = self.crew_backstory,
#            llm = llm,
#            verbose = False,
#        )
#
#    def task(self) -> Task:
#        return Task(
#            description = self.crew_description,
#            expected_output = self.crew_expected_output,
#            agent = self.agent()
#        )
#
#    def crew(self) -> Crew:
#        return Crew(
#            agents = [self.agent()],
#            tasks = [self.task()],
#            process = Process.sequential,
#            verbose = False
#        )
