#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import dotenv
from openai import OpenAI
import yaml

dotenv.load_dotenv()
from agent import Agent

class Step:
    def __init__(self, step):
        self.step_name = step["name"]
        self.step_agent = step.get("agent")
        self.step_condition = step.get("condition")
        self.step_dependencies = step.get("dependencies")

    def run(self, prompt):
        output = {}
        if self.step_agent:
            prompt = self.step_agent.run(prompt)
            output["prompt"] = prompt
        if self.step_condition:
            input = {"prompt": prompt}
            exec(self.step_condition, {}, input)
            output = locals()["input"].get("output")
            print(output)
        if self.step_dependencies:
            output["dependencies"] = self.step_dependencies
        return output
