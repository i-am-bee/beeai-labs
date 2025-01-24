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
        # NOTE: "template" is an arbitrary key name that we use for now, it could be anything
        prompt = self.workflow["spec"]["template"]["prompt"]
        steps = self.workflow["spec"]["template"]["steps"]

        # Create a Step object for each step in the workflow
        for step in steps:
            if step["agent"]:
                step["agent"] = self.agents.get(step["agent"])
            self.steps[step["name"]] = Step(step)

        # Run each step in sequence, assuming that the output of each step is the input to the next
        for step_name in self.steps:
            step = self.steps[step_name]
            response = step.run(prompt)
            prompt = response.get("prompt", prompt)

        if (
            self.workflow["spec"]["strategy"]["output"]
            and self.workflow["spec"]["strategy"]["output"] == "verbose"
        ):
            print(f"Step {step_name} output: {response}")

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
