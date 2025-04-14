#!/usr/bin/env python3

# Copyright © 2025 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, dotenv
from src.mermaid import Mermaid

from src.step import Step
from src.agents.agent_factory import AgentFramework, AgentFactory

from src.agents.beeai_agent import BeeAIAgent
from src.agents.crewai_agent import CrewAIAgent
from src.agents.openai_agent import OpenAIAgent
from src.agents.remote_agent import RemoteAgent
from src.agents.mock_agent import MockAgent

from src.agents.agent import save_agent, restore_agent

dotenv.load_dotenv() #TODO is this needed now that __init__.py in package runs this?

def get_agent_class(framework: str, mode="local") -> type:
    """
    Returns the agent class based on the provided framework.

    Args:
        framework (str): The framework to get the agent class for.

    Returns:
        type: The agent class based on the provided framework.
    """
    if os.getenv("DRY_RUN"):
        return MockAgent

    return AgentFactory.create_agent(framework, mode)

def create_agents(agent_defs):
    """
    Creates agents based on the provided definitions.

    Args:
        agent_defs (list): A list of agent definitions. Each definition is a dictionary with the following keys:
            "spec": A dictionary containing the specification of the agent.
                "framework": The framework of the agent (e.g., "bee").

    Returns:
        None
    """
    for agent_def in agent_defs:
        # Use 'bee' if this value isn't set
        #
        agent_def["spec"]["framework"] = agent_def["spec"].get(
            "framework", AgentFramework.BEEAI
        )
        save_agent(get_agent_class(agent_def["spec"]["framework"], agent_def["spec"].get("mode"))(agent_def))

class Workflow:
    """Execute sequential workflow.

    Args:
        agent_defs (dict): Dictionary of agent definitions.
        workflow (dict): Workflow definition.

    Attributes:
        agents (dict): Dictionary of agents.
        steps (dict): Dictionary of steps.
    """
    def __init__(self, agent_defs={}, workflow={}):
        """Execute sequential workflow.
        input:
            agents: array of agent definitions, saved agent names, or None (agents in workflow must be pre-created)
            workflow: workflow definition
        """
        self.agents = {}
        self.steps = {}

        self.agent_defs = agent_defs
        self.workflow = workflow

    # generates a mermaid markdown representation of the workflow
    # kind: sequenceDiagram or flowchart
    # orientation: TD (top down) or RL (right left) when kind is flowchart
    def to_mermaid(self, kind="sequenceDiagram", orientation="TD") -> str:
        #TODO: why is self.workflow an array?
        workflow = self.workflow
        if isinstance(self.workflow, list):
            workflow = self.workflow[0]

        return Mermaid(workflow, kind, orientation).to_markdown()

    async def run(self, prompt=''):
        """Execute workflow."""
        try:
          if prompt != '':
            self.workflow['spec']['template']['prompt'] = prompt
          self.create_or_restore_agents(self.agent_defs, self.workflow)
          return await self._condition()
        except Exception as err:
            if self.workflow["spec"]["template"].get("exception"):
                exp = self.workflow["spec"]["template"].get("exception")
                exp_agent = self.agents.get(exp["agent"])
                if exp_agent:
                    await exp_agent.run(err)
            else:
                raise err

    # private methods
    def create_or_restore_agents(self, agent_defs, workflow):
        """
        Creates or restores agents based on the provided definitions and workflow.

        Args:
            agent_defs (list): A list of agent definitions. Each definition can be either a string (agent name) or a dictionary (agent definition).
            workflow (dict): A dictionary representing the workflow.

        Returns:
            None
        """
        if agent_defs:
            if type(agent_defs[0]) == str:
                for agent_name in agent_defs:
                    self.agents[agent_name] = restore_agent(agent_def)
            else:
                for agent_def in agent_defs:
                  # Use 'bee' if this value isn't set
                  #
                  agent_def["spec"]["framework"] = agent_def["spec"].get(
                      "framework", AgentFramework.BEEAI
                  )
                  self.agents[agent_def["metadata"]["name"]] = get_agent_class(agent_def["spec"]["framework"], agent_def["spec"].get("mode"))(agent_def)
        else:
            for agent in workflow["spec"]["template"]["agents"]:
                self.agents[agent] = restore_agent(agent)

    #TODO: why is this public? It should be private by naming: _find_index(...) @aki
    def find_index(self, steps, name):
        for step in steps:
            if step.get("name") == name:
                return steps.index(step)

    async def _condition(self):
        """
        This function is responsible for executing the workflow steps based on the provided prompt.
        It iterates through the steps and runs each step using the `run` method of the `Step` class.
        The function takes in the workflow template as input, which includes the prompt and the steps.
        It also uses the `agents` dictionary to map the agent names to their corresponding objects.
        The function returns a dictionary containing the final prompt after all the steps have been executed.
        """
        prompt = self.workflow["spec"]["template"]["prompt"]
        steps = self.workflow["spec"]["template"]["steps"]
        for step in steps:
            if step.get("agent"):
                step["agent"] = self.agents.get(step["agent"])
                if not step["agent"]:
                    raise Exception("Agent doesn't exist")
            if step.get("parallel"):
                agents = []
                for agent in step.get("parallel"):
                    agents.append(self.agents.get(agent))
                step["parallel"] = agents
            if step.get("loop"):
                step["loop"]["agent"] = self.agents.get(step["loop"]["agent"])
            self.steps[step["name"]] = Step(step)
        current_step = self.workflow["spec"]["template"]["steps"][0]["name"]
        step_results = {}
        while True:
            response = await self.steps[current_step].run(prompt)
            prompt = response["prompt"]
            if response.get("next"):
                current_step = response["next"]
            else:
                if current_step == steps[len(steps)-1].get("name"):
                    break
                else:
                    current_step = steps[self.find_index(steps, current_step)+1].get("name")
        step_results["final_prompt"] = prompt
        return step_results
