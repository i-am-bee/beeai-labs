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

import os, yaml, unittest

from unittest import TestCase

from src.mermaid import Mermaid
from src.workflow import Workflow

def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data

class TestMermaid(TestCase):
    def setUp(self):        
        self.workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/workflows/simple_workflow.yaml"))[0]
        
    def tearDown(self):
        self.workflow_yaml = None

    def test_markdown_sequenceDiagram(self):
        mermaid = Mermaid(self.workflow_yaml, "sequenceDiagram")
        self.assertTrue(mermaid.to_markdown().startswith("sequenceDiagram"))

        for agent in ['test1', 'test2', 'test3']:
            self.assertTrue(f"participant {agent}" in mermaid.to_markdown())
        
        self.assertTrue(f"test1->>test2: step1" in mermaid.to_markdown())
        self.assertTrue(f"test2->>test3: step2" in mermaid.to_markdown())
        self.assertTrue(f"test3->>test3: step3" in mermaid.to_markdown())

    def test_markdown_flowchart(self):
        for orientation in ["TD", "LR"]:        
            mermaid = Mermaid(self.workflow_yaml, "flowchart", f"{orientation}")
            self.assertTrue(mermaid.to_markdown().startswith(f"flowchart {orientation}"))

            self.assertTrue(f"test1-- step1 -->test2" in mermaid.to_markdown())
            self.assertTrue(f"test2-- step2 -->test3" in mermaid.to_markdown())
            self.assertTrue(f"test3-- step3 -->test3" in mermaid.to_markdown())

class TestMermaidCondition_case(TestCase):
    def setUp(self):        
        self.workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/workflows/conditional_case_workflow.yaml"))[0]
        
    def tearDown(self):
        self.workflow_yaml = None

    #
    # # expected mermaid code
    # sequenceDiagram
    # sequenceDiagram
    # participant agent1
    # participant agent2
    # participant agent3
    # agent1->>agent2: step1
    # agent2->>agent3: step2
    # agent3->>agent3: step3
    # agent3->>None: step2 (input.some_condition == True)
    # agent3->>None: step3 (input.some_condition == False)
    # agent3->>None: step3 default
    # 
    def test_markdown_sequenceDiagram(self):
        mermaid = Mermaid(self.workflow_yaml, "sequenceDiagram")
        self.assertTrue(mermaid.to_markdown().startswith("sequenceDiagram"))

        for agent in ['agent1', 'agent2', 'agent3']:
            self.assertTrue(f"participant {agent}" in mermaid.to_markdown())
        
        self.assertTrue(f"agent1->>agent2: step1" in mermaid.to_markdown())
        self.assertTrue(f"agent2->>agent3: step2" in mermaid.to_markdown())
        self.assertTrue(f"agent3->>agent3: step3" in mermaid.to_markdown())
        self.assertTrue(f"agent3->>None: step2 (input.some_condition == True)" in mermaid.to_markdown())
        self.assertTrue(f"agent3->>None: step3 (input.some_condition == False)" in mermaid.to_markdown())
        self.assertTrue(f"agent3->>None: step3 default" in mermaid.to_markdown())

    #
    # # expected mermaid code
    # flowchart LR #or TD
    # agent1-- step1 -->agent2
    # agent2-- step2 -->agent3
    # agent3-- step2 (input.some_condition == True) -->agent2
    # agent3-- step3 (input.some_condition == False) -->agent3
    #
    # TODO: complete
    def _test_markdown_flowchart(self):
        for orientation in ["TD", "LR"]:
            mermaid = Mermaid(self.workflow_yaml, "flowchart", f"{orientation}")
            self.assertTrue(mermaid.to_markdown().startswith(f"flowchart {orientation}"))

            self.assertTrue(f"agent1-- step1 -->agent2" in mermaid.to_markdown())
            self.assertTrue(f"agent3-- step2 (input.some_condition == True) -->agent2" in mermaid.to_markdown())
            self.assertTrue(f"agent3-- step3 (input.some_condition == False) -->agent3" in mermaid.to_markdown())


class TestMermaidCondition_if(TestCase):
    def setUp(self):        
        self.workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/workflows/conditional_if_workflow.yaml"))[0]
        
    def tearDown(self):
        self.workflow_yaml = None
    
    def _test_markdown_sequenceDiagram(self):
        mermaid = Mermaid(self.workflow_yaml, "sequenceDiagram")
        self.assertTrue(mermaid.to_markdown().startswith("sequenceDiagram"))
        #TODO: complete
    
    def _test_markdown_flowchart(self):
        for orientation in ["TD", "LR"]:
            mermaid = Mermaid(self.workflow_yaml, "flowchart", f"{orientation}")
            self.assertTrue(mermaid.to_markdown().startswith(f"flowchart {orientation}"))
        #TODO: complete

class TestWorkflow_to_mermaid(TestCase):
    def setUp(self):        
        self.workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/workflows/simple_workflow.yaml"))[0]
        self.workflow = Workflow({}, self.workflow_yaml)
        
    def tearDown(self):
        self.workflow_yaml = None
        self.workflow = None

    def test_markdown_sequenceDiagram(self):
        markdown = self.workflow.to_mermaid("sequenceDiagram")
        self.assertTrue(markdown.startswith("sequenceDiagram"))

        self.assertTrue(f"test1->>test2: step1" in markdown)
        self.assertTrue(f"test2->>test3: step2" in markdown)
        self.assertTrue(f"test3->>test3: step3" in markdown)

    def test_markdown_flowchart(self):
        for orientation in ["TD", "LR"]:
            markdown = self.workflow.to_mermaid("flowchart", f"{orientation}")
            self.assertTrue(markdown.startswith(f"flowchart {orientation}"))

            self.assertTrue(f"test1-- step1 -->test2" in markdown)
            self.assertTrue(f"test2-- step2 -->test3" in markdown)
            self.assertTrue(f"test3-- step3 -->test3" in markdown)

if __name__ == '__main__':
    unittest.main()
