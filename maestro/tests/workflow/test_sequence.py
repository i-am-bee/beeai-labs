#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import yaml
import dotenv
from unittest import TestCase
from pytest_mock import mocker
import os

from maestro import Workflow
from maestro import BeeAgent

dotenv.load_dotenv()

def test_sequence_method(mocker):
    def parse_yaml(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            yaml_data = list(yaml.safe_load_all(file))
        return yaml_data

    execution_order = []
    class MockAgent:
        def __init__(self, name):
            self.name = name
        def run(self, prompt):
            execution_order.append(self.name)
            return f"{prompt} processed by {self.name}"

    mock_agent1 = MockAgent("agent1")
    mock_agent2 = MockAgent("agent2")
    mock_agents = {"agent1": mock_agent1, "agent2": mock_agent2}
    mocker.patch.object(BeeAgent, "__new__", side_effect=lambda name: mock_agents[name])
    workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"workflow.yaml"))
    workflow_yaml[0]["spec"]["template"]["agents"] = []
    try:
        workflow = Workflow(agent_defs=[], workflow=workflow_yaml[0])
        workflow.agents = mock_agents
    except Exception as excep:
        raise RuntimeError("Unable to create workflow") from excep
    step_results = workflow._sequence()
    assert step_results["step_0"] == "Start of the workflow"
    assert step_results["step_1"] == "Start of the workflow processed by agent1"
    assert step_results["step_2"] == "Start of the workflow processed by agent1 processed by agent2"
    assert step_results["final_prompt"] == "Start of the workflow processed by agent1 processed by agent2 processed by agent1"
    expected_order = ["agent1", "agent2", "agent1"]
    assert execution_order == expected_order, f"Expected order {expected_order}, but got {execution_order}"
