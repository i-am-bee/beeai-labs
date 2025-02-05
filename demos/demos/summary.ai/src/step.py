#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import dotenv
from utils import run_agent

dotenv.load_dotenv()

class Step:
    def __init__(self, step):
        self.step_name = step["name"]
        self.step_agent = step["agent"]

    def run(self, prompt):
        """Executes the step's agent and returns the result."""
        print(f"🐝 Executing step: {self.step_name}")
        output = run_agent(self.step_agent, prompt)
        return {"prompt": output}
