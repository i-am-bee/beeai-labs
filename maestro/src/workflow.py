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

from src.step import Step
from src.agent_factory import AgentFramework

from src.crewai_agent import CrewAIAgent
from src.bee_agent import BeeAgent
from src.mock_agent import MockAgent
from src.agent import save_agent, restore_agent

dotenv.load_dotenv() #TODO is this needed now that __init__.py in package runs this?

def get_agent_class(framework: str) -> type:
    if os.getenv("DRY_RUN"):
        return MockAgent
    if framework == "crewai":
        return CrewAIAgent
    else:
        return BeeAgent

def create_agents(agent_defs):
    for agent_def in agent_defs:
        # Use 'bee' if this value isn't set
        #
        agent_def["spec"]["framework"] = agent_def["spec"].get(
            "framework", AgentFramework.BEE
        )
        save_agent(get_agent_class(agent_def["spec"]["framework"])(agent_def))

class Workflow:
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

    def run(self):
        """Execute workflow."""
        self.create_or_restore_agents(self.agent_defs, self.workflow)
        if self.workflow["spec"]["strategy"]["type"] == "sequence":
            return self._sequence()
        elif self.workflow["spec"]["strategy"]["type"] == "condition":
            return self._condition()
        else:
            print("not supported yet")

    # private methods
    def create_or_restore_agents(self, agent_defs, workflow):
        if agent_defs:
            if type(agent_defs[0]) == str:
                for agent_name in agent_defs:
                    self.agents[agent_name] = restore_agent(agent_def)
            else:
                for agent_def in agent_defs:
                  # Use 'bee' if this value isn't set
                  #
                  agent_def["spec"]["framework"] = agent_def["spec"].get(
                      "framework", AgentFramework.BEE
                  )
                  self.agents[agent_def["metadata"]["name"]] = get_agent_class(agent_def["spec"]["framework"])(agent_def)
        else:
            for agent in workflow["spec"]["template"]["agents"]:
                self.agents[agent] = restore_agent(agent)
    
    def find_index(self, steps, name):
        for step in steps:
            if step.get("name") == name:
                return steps.index(step)
    
    def _sequence(self):
        prompt = self.workflow["spec"]["template"].get("prompt", "")
        steps = self.workflow["spec"]["template"].get("steps", [])
        if not steps:
            raise ValueError("Workflow is missing required 'steps' key in 'spec'")
        step_results = {}
        for i, step in enumerate(steps):
            agent_name = step["agent"]
            agent_instance = self.agents.get(agent_name)
            if not agent_instance:
                raise ValueError(f"Agent {agent_name} not found for step {step['name']}")
            step_results[f"step_{i}"] = prompt
            response = agent_instance.run(prompt)
            prompt = response if isinstance(response, str) else response.get("prompt", prompt)
        step_results["final_prompt"] = prompt
        return step_results

    def _condition(self):
        prompt = self.workflow["spec"]["template"]["prompt"]
        steps = self.workflow["spec"]["template"]["steps"]
        for step in steps:
            if step.get("agent"):
                step["agent"] = self.agents.get(step["agent"])
            self.steps[step["name"]] = Step(step)
        current_step = self.workflow["spec"]["template"]["steps"][0]["name"]
        while True:
            response = self.steps[current_step].run(prompt)
            prompt = response["prompt"]
            if response.get("next"):
                current_step = response["next"]
            else:
                if current_step == steps[len(steps)-1].get("name"):
                    break
                else:
                    current_step = steps[self.find_index(steps, current_step)+1].get("name")
        return prompt
