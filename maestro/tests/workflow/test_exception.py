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

import os, yaml, sys, io
import pytest
from unittest import TestCase
from src.workflow import Workflow

import asyncio

def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data

# `exception` tests
class TestException(TestCase):
    def tearDown(self):
        self.workflow = None

    def test_exception(self):
        self.agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/agents/simple_agent.yaml"))
        self.workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/workflows/exception_workflow.yaml"))
        self.workflow = Workflow(self.agents_yaml, self.workflow_yaml[0])
        output = io.StringIO()
        sys.stdout = output
        response = asyncio.run(self.workflow.run())
        assert "Running test4..." in output.getvalue()

    def test_exception_no_exception(self):
        self.agents_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/agents/simple_agent.yaml"))
        self.workflow_yaml = parse_yaml(os.path.join(os.path.dirname(__file__),"../yamls/workflows/exception_no_exception_workflow.yaml"))
        self.workflow = Workflow(self.agents_yaml, self.workflow_yaml[0])
        try:
            response = asyncio.run(self.workflow.run())
        except Exception as excep:
            print(excep)
            assert "Agent doesn't exist" in str(excep)

if __name__ == '__main__':
    unittest.main()
