#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0


from bee_hive.step import Step
from bee_hive.agent_factory import AgentFramework
import dotenv

# TODO: Refactor later to factory or similar
from bee_hive.crewai_agent import CrewAIAgent
from bee_hive.bee_agent import BeeAgent

dotenv.load_dotenv()


def find_index(steps, name):
    for step in steps:
        if step.get("name") == name:
            return steps.index(step)


@staticmethod
def get_agent_class(framework: str) -> type:
    if framework == "crewai":
        return CrewAIAgent
    else:
        return BeeAgent


class Workflow:
    agents = {}
    steps = {}
    workflow = {}

    def __init__(self, agent_defs, workflow):
        """Execute sequential workflow.
        input:
            agents: array of agent definitions
            workflow: workflow definition
        """
        for agent_def in agent_defs:
            # Use 'bee' if this value isn't set
            #
            agent_def["spec"]["framework"] = agent_def["spec"].get(
                "framework", AgentFramework.BEE
            )
            self.agents[agent_def["metadata"]["name"]] = get_agent_class(
                agent_def["spec"]["framework"]
            )(agent_def)
        self.workflow = workflow

    def run(self):
        """Execute workflow."""

        if self.workflow["spec"]["strategy"]["type"] == "sequence":
            return self._sequence()
        elif self.workflow["spec"]["strategy"]["type"] == "condition":
            return self._condition()
        else:
            print("not supported yet")

    def _sequence(self):
        prompt = self.workflow["spec"]["template"]["prompt"]
        for agent in self.agents.values():
            if (
                self.workflow["spec"]["strategy"]["output"]
                and self.workflow["spec"]["strategy"]["output"] == "verbose"
            ):
                prompt = agent.run_streaming(prompt)
            else:
                prompt = agent.run(prompt)
        return prompt

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
                    current_step = find_index(steps, current_step)
        return prompt

