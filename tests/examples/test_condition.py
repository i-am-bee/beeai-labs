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

import os, sys, json, dotenv, yaml
import asyncio

from openai import OpenAI

from src.workflow import Workflow

dotenv.load_dotenv()

def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data

if __name__ == "__main__":
    agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"condition_agents.yaml"))
    workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"condition_workflow.yaml"))
    try:
        workflow = Workflow(agents_yaml, workflow_yaml[0])
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep
    asyncio.run(workflow.run())
