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

import os, dotenv, yaml
import asyncio

from unittest import TestCase
from pytest_mock import mocker

from src.workflow import Workflow
from src.agents.beeai_agent import BeeAIAgent

dotenv.load_dotenv()

# TODO: consider moving setup here
#@pytest.fixture(scope="module")

class BeeAIAgentMock:
    def __init__(self):
        pass

    async def run(self, prompt: str) -> str:
        return 'OK:'+prompt

def test_agent_runs(mocker) -> None:
    def parse_yaml(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            yaml_data = list(yaml.safe_load_all(file))
        return yaml_data

    # setup mocks
    mock_beeai=BeeAIAgentMock()
    mocker.patch.object(BeeAIAgent, "__new__", return_value = mock_beeai)

    agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"agents.yaml"))
    workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"workflow.yaml"))
    try:
        workflow = Workflow(agents_yaml, workflow_yaml[0])
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep
    result = asyncio.run(workflow.run())
    print(result)

    assert result is not None
    assert result["final_prompt"].startswith("OK:Welcome") or result["final_prompt"].startswith("Mock agent")
