#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import yaml
import dotenv

dotenv.load_dotenv()
from agent import Agent

class Workflow:
    agents = []
    workflow = {}
    def __init__(self, agent_defs, workflow):
        """Execute sequential workflow.
        input:
            agents: array of agent definitions
            workflow: workflow definition
        """
        for agent_def in agent_defs:
            self.agents.append(Agent(agent_def))
        self.workflow = workflow


    def run(self):
        """Execute workflow."""

        if (self.workflow["spec"]["strategy"]["type"]  == "sequence"):
            return self._sequence()
        else:
            print("not supported yet")   

    def _sequence(self):
        prompt = self.workflow["spec"]["template"]["prompt"]
        for agent in self.agents:
            if (
                self.workflow["spec"]["strategy"]["output"]
                and self.workflow["spec"]["strategy"]["output"] == "verbose"
            ):
                prompt = agent.run_streaming(prompt)
            else:
                prompt = agent.run(prompt)
        return prompt
