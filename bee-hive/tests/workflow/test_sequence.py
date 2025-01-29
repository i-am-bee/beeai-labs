import unittest
from unittest.mock import MagicMock
from bee_hive.workflow import Workflow

class TestSequenceMethod(unittest.TestCase):
    def setUp(self):
        self.mock_workflow = {
            "spec": {
                "prompt": "Start of the workflow",
                "steps": [
                    {"name": "step1", "agent": "agent1"},
                    {"name": "step2", "agent": "agent2"},
                    {"name": "step3", "agent": "agent1"}
                ]
            }
        }
        self.mock_agent1 = MagicMock()
        self.mock_agent1.run.side_effect = lambda prompt: f"{prompt} processed by agent1"
        self.mock_agent2 = MagicMock()
        self.mock_agent2.run.side_effect = lambda prompt: f"{prompt} processed by agent2"

        self.mock_agents = {
            "agent1": self.mock_agent1,
            "agent2": self.mock_agent2
        }

    def test_sequence_method(self):
        workflow = Workflow(agent_defs=[], workflow=self.mock_workflow)
        workflow.agents = self.mock_agents
        final_prompt = workflow._sequence()

        self.mock_agent1.run.assert_any_call("Start of the workflow")
        self.mock_agent2.run.assert_any_call("Start of the workflow processed by agent1")
        self.mock_agent1.run.assert_any_call("Start of the workflow processed by agent1 processed by agent2")

        expected_final_prompt = "Start of the workflow processed by agent1 processed by agent2 processed by agent1"
        self.assertEqual(final_prompt, expected_final_prompt)
    
if __name__ == "__main__":
    unittest.main()