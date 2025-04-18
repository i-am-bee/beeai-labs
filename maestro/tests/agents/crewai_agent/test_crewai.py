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

import dotenv, os, yaml
import asyncio

from unittest import TestCase

from cli.common import parse_yaml

from src.workflow import Workflow

dotenv.load_dotenv()

class CrewAITest(TestCase):
    def test_agent_runs(self) -> None:
        agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__), 'agents.yaml'))
        workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__), 'workflow.yaml'))

        try:
            workflow = Workflow(agents_yaml, workflow_yaml[0])
        except Exception as excep:
            raise RuntimeError("Unable to create agents") from excep

        result = asyncio.run(workflow.run())
        print(result)

        assert result is not None
        assert result["final_prompt"] == "OK"

if __name__ == "__main__":
    crewtest = CrewAITest()
    crewtest.test_agent_runs()
