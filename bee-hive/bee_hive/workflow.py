#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import yaml
import dotenv

dotenv.load_dotenv()
from agent import Agent
from step import Step

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
            self.agents[agent_def["metadata"]["name"]] = Agent(agent_def)
        self.workflow = workflow


    def run(self):
        """Execute workflow."""

        if (self.workflow["spec"]["strategy"]["type"]  == "sequence"):
            return self._sequence()
        elif (self.workflow["spec"]["strategy"]["type"]  == "condition"):
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
            if step["agent"]:
                step["agent"] = self.agents.get(step["agent"])
            self.steps[step["name"]] = Step(step)
        current_step = self.workflow["spec"]["template"]["start"]
        while current_step != "end":
            response = self.steps[current_step].run(prompt)
            prompt = response["prompt"]
            current_step = response["next"]
        return prompt
