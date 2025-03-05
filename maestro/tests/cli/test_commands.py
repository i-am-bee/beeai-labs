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

import os

from unittest import TestCase

from cli.commands import CLI

class TestCommand(TestCase):
    TEST_FIXTURES_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
    SCHEMAS_ROOT_PATH = os.path.join(os.path.dirname(__file__), "../../schemas")
    
    def get_fixture(self, file_name):
        return os.path.join(self.TEST_FIXTURES_ROOT_PATH, file_name)

    def get_schema(self, file_name):
        return os.path.join(self.SCHEMAS_ROOT_PATH, file_name)

# `deploy` commmand tests
class DeployCommand(TestCommand):
    def setUp(self):
        self.args = {
                        '--dry-run': True,
                        '--help': False,
                        '--verbose': True,
                        '--version': False,
                        '--url': "127.0.0.1:5000",
                        '--k8s': False,
                        '--kubernetes': False,
                        '--docker': False,
                        'AGENTS_FILE': self.get_fixture('yamls/agents/simple_agent.yaml'),
                        'SCHEMA_FILE': None,
                        'WORKFLOW_FILE': self.get_fixture('yamls/workflows/simple_workflow.yaml'),
                        'YAML_FILE': None,
                        'deploy': True,
                        'run': False,
                        'create': False,
                        'validate': False
                    }
        self.command = CLI(self.args).command()
    
    def tearDown(self):
        self.args = {}
        self.command = None
        
    def test_deploy__dry_run_k8s(self):
        self.args["--k8s"] = True
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'deploy')
        self.assertTrue(self.command.execute() == 0)

    def test_deploy__dry_run_kubernetes(self):
        self.args["--kubernetes"] = True
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'deploy')
        self.assertTrue(self.command.execute() == 0)
        
    def test_deploy__dry_run_docker(self):
        self.args["--docker"] = True
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'deploy')
        self.assertTrue(self.command.execute() == 0)

# `run` commmand tests
class RunCommand(TestCommand):
    def setUp(self):
        self.args = {
                        '--dry-run': True,
                        '--help': False,
                        '--verbose': False,
                        '--version': False,
                        'AGENTS_FILE': self.get_fixture('yamls/agents/simple_agent.yaml'),
                        'SCHEMA_FILE': None,
                        'WORKFLOW_FILE': self.get_fixture('yamls/workflows/simple_workflow.yaml'),
                        'YAML_FILE': None,
                        'deploy': False,
                        'run': True,
                        'create': False,
                        'validate': False
                    }
        self.command = CLI(self.args).command()
    
    def tearDown(self):
        self.args = {}
        self.command = None
        
    def test_run__dry_run(self):
        self.assertTrue(self.command.name() == 'run')
        try:
            self.command.execute()
        except Exception as e:
            self.fail("Exception running command: {message}".format(message=str(e)))

# `create` commmand tests
class CreateCommand(TestCommand):
    def setUp(self):
        self.args = {
                        '--dry-run': True,
                        '--help': False,
                        '--verbose': False,
                        '--version': False,
                        'AGENTS_FILE': self.get_fixture('yamls/agents/simple_agent.yaml'),
                        'SCHEMA_FILE': None,
                        'WORKFLOW_FILE': None,
                        'YAML_FILE': None,
                        'deploy': False,
                        'create': True,
                        'run': False,
                        'validate': False
                    }
        self.command = CLI(self.args).command()
    
    def tearDown(self):
        self.args = {}
        self.command = None
        
    def test_run__dry_run(self):
        self.assertTrue(self.command.name() == 'create')
        self.assertTrue(self.command.execute() == 0)

# `create` and `run` commmand tests
class CreateAndRunCommand(TestCommand):
    def setUp(self):
        self.args = {
                        '--dry-run': True,
                        '--help': False,
                        '--verbose': False,
                        '--version': False,
                        'AGENTS_FILE': self.get_fixture('yamls/agents/simple_agent.yaml'),
                        'SCHEMA_FILE': None,
                        'WORKFLOW_FILE': self.get_fixture('yamls/workflows/simple_workflow.yaml'),
                        'YAML_FILE': None,
                        'deploy': False,
                        'create': True,
                        'run': False,
                        'validate': False
                    }

    def tearDown(self):
        self.args = {}
        self.command = None

    def test_create_dry_run(self):
        self.args['create'] = True
        self.args['run'] = False
        self.args['WORKFLOW_FILE'] = None
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'create')
        self.assertTrue(self.command.execute() == 0)

    def test_run_dry_run(self):
        self.args['create'] = False
        self.args['run'] = True
        self.args['AGENTS_FILE'] = "None"
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'run')
        self.assertTrue(self.command.execute() == 0)

# `validate` commmand tests
class ValidateCommand(TestCommand):
    def setUp(self):
        self.args = {
                        '--dry-run': False,
                        '--help': False,
                        '--verbose': False,
                        '--version': False,
                        'AGENTS_FILE': self.get_fixture('yamls/agents/simple_agent.yaml'),
                        'SCHEMA_FILE': None,
                        'WORKFLOW_FILE': self.get_fixture('yamls/workflows/simple_workflow.yaml'),
                        'YAML_FILE': None,
                        'deploy': False,
                        'run': False,
                        'create': False,
                        'validate': True
                    }
    
    def tearDown(self):
        self.args = {}
        self.command = None
        
    def test_validate_agents_file(self):
        self.args['SCHEMA_FILE'] = self.get_schema('agent_schema.json')
        self.args['YAML_FILE'] = self.args['AGENTS_FILE']
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'validate')
        self.assertTrue(self.command.execute() == 0)

    def test_validate_workflow_file(self):
        self.args['SCHEMA_FILE'] = self.get_schema('workflow_schema.json')
        self.args['YAML_FILE'] = self.args['WORKFLOW_FILE']
        self.command = CLI(self.args).command()
        self.assertTrue(self.command.name() == 'validate')
        self.assertTrue(self.command.execute() == 0)

if __name__ == '__main__':
    unittest.main()
