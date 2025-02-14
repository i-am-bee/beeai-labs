#!/usr/bin/env python3

import os, sys, yaml
from src.workflow import Workflow

sys.path.append(os.path.realpath(__file__)) + "/../../../src")
sys.path.append(os.path.realpath(__file__)) + "/../../../demos/agents/crewai/activity_planner")

def test_agent_runs() -> None:
    """
    Verify the test agent runs correctly
    """
    def parse_yaml(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            yaml_data = list(yaml.safe_load_all(file))
        return yaml_data

    agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"agents.yaml"))
    workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"workflow.yaml"))
    try:
        workflow = Workflow(agents_yaml, workflow_yaml[0])
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep
    result = workflow.run()
    print(result)

if __name__ == "__main__":
    test_agent_runs()


