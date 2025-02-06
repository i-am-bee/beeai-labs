#!/usr/bin/env python3

from unittest import TestCase
import dotenv
import yaml
import os
from pytest_mock import mocker

from bee_hive.workflow import Workflow
from bee_hive.bee_agent import BeeAgent

dotenv.load_dotenv()

# TODO: consider moving setup here
#@pytest.fixture(scope="module")

class BeeAgentMock:
    def __init__(self):
        pass
        
    def run(self, prompt: str) -> str:
        return 'OK:'+prompt
    
def test_agent_runs(mocker) -> None:
    def parse_yaml(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            yaml_data = list(yaml.safe_load_all(file))
        return yaml_data

    # setup mocks
    mock_bee=BeeAgentMock()
    mocker.patch.object(BeeAgent, "__new__", return_value = mock_bee)
        
    agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"agents.yaml"))
    workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"workflow.yaml"))
    try:
        workflow = Workflow(agents_yaml, workflow_yaml[0])
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep
    result = workflow.run()
    print(result)
       
    assert result is not None
    # This gets returned by the mock function which uses the prompt from the workflow
    assert (result["final_prompt"]=="OK:Welcome")

