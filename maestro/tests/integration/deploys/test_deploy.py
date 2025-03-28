#/usr/bin/env python3

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

import os
import subprocess
import requests

import pytest
from unittest import TestCase
from src.deploy import Deploy

# `deploy` tests
class TestDeploy(TestCase):
    def setUp(self):        
        self.cwd = os.getcwd()
        self.deploy = Deploy("tests/examples/condition_agents.yaml", "tests/examples/condition_workflow.yaml", "BEEAI_API_KEY=sk-proj-testkey BEEAI_API=http://192.168.86.45:4000 DRY_RUN=1")
        
    def tearDown(self):
        self.deploy = None

    @pytest.mark.skipif(os.getenv('DEPLOY_KUBERNETES_TEST') != "1", reason="Kubernetes deploy skipped")
    def test_deploy_to_kubernetes(self):
        self.deploy.deploy_to_kubernetes()
        if os.getenv('IN_GITHUB_ACTION') != "1":
            response = requests.get("http://127.0.0.1:30051/").text
            self.assertTrue(response.find("Running expert...") != -1)
            self.assertTrue(response.find("Running colleague...") != -1)

    @pytest.mark.skipif(os.getenv('DEPLOY_DOCKER_TEST') != "1", reason="Docker deploy skipped")
    def test_deploy_to_docker(self):
        self.deploy.deploy_to_docker()
        if os.getenv('IN_GITHUB_ACTION') != "1":
            response = requests.get("http://127.0.0.1:5000/").text
            self.assertTrue(response.find("Running expert...") != -1)
            self.assertTrue(response.find("Running colleague...") != -1)

if __name__ == '__main__':
    unittest.main()

