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

import os, yaml, json, jsonschema, traceback
import asyncio

from openai import OpenAI
from jsonschema.exceptions import ValidationError, SchemaError

from src.deploy import Deploy
from src.workflow import Workflow, create_agents
from cli.common import Console, parse_yaml

# Root CLI class
class CLI:
    def __init__(self, args):
        self.args = args
        VERBOSE, DRY_RUN = False, False
        if self.args['--verbose']:
            VERBOSE = True
        if self.args['--dry-run']:
            DRY_RUN = True

    def command(self):
        if self.args.get('validate') and self.args['validate']:
            return ValidateCmd(self.args)
        elif self.args.get('create') and self.args['create']:
            return CreateCmd(self.args)
        elif self.args.get('run') and self.args['run']:
            return RunCmd(self.args)
        elif self.args.get('deploy') and self.args['deploy']:
            return DeployCmd(self.args)
        elif self.args.get('mermaid') and self.args['mermaid']:
            return MermaidCmd(self.args)
        else:
            raise Exception("Invalid command")

# Base class for all commands
class Command:
    def __init__(self, args):
        self.args = args
        self.__init_dry_run()
        
    def __init_dry_run(self):
        if self.args.get('--dry-run') and self.args['--dry-run']:
            self.__dry_run = True
            os.environ["DRY_RUN"] = "True"        
    
    def _check_verbose(self):
        if self.verbose():
            print(traceback.format_exc())

    def println(self, msg):
        self.print(msg + "\n")

    def print(self, msg):
        Console.print(msg)

    def warn(self, msg):
        Console.warn(msg)

    def verbose(self):
        return self.args['--verbose']
    
    def dry_run(self):
        return self.__dry_run

    def execute(self):
        func = self.dispatch()
        rc = func()
        if rc == None:
            return 0
        else:
            if isinstance(rc, int):
                return rc
            else:
                return 1

    def dispatch(self):
        if self.args['validate']:
            return self.validate
        elif self.args['create']:
            return self.create
        elif self.args['run']:
            return self.run
        elif self.args['deploy']:
            return self.deploy
        elif self.args['mermaid']:
            return self.mermaid
        else:
            raise Exception("Invalid subcommand")

# validate command group
#  maestro validate SCHEMA_FILE YAML_FILE [options]
class ValidateCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    def SCHEMA_FILE(self):
        return self.args['SCHEMA_FILE']

    def YAML_FILE(self):
        return self.args['YAML_FILE']

    def name(self):
      return "validate"

    def validate(self):
        Console.print(f"validating {self.YAML_FILE()} with schema {self.SCHEMA_FILE()}")
        with open(self.SCHEMA_FILE(), 'r') as f:
            schema = json.load(f)
        with open(self.YAML_FILE(), 'r') as f:
            yamls = yaml.safe_load_all(f)
            for yaml_data in yamls:
                json_data = json.dumps(yaml_data, indent=4)
                try:
                    jsonschema.validate(yaml_data, schema)
                    Console.ok("YAML file is valid.")
                except ValidationError as ve:
                    self._check_verbose()
                    Console.error(f"YAML file is NOT valid:\n {str(ve.message)}")
                    return 1
                except SchemaError as se:
                    self._check_verbose()
                    Console.error(f"Schema file is NOT valid:\n {str(se.message)}")
                    return 1
        return 0

# Create command group
#  maestro create AGENTS_FILE [options]
class CreateCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    def __create_agents(self, agents_yaml):
        try:
            create_agents(agents_yaml)
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"{str(e)}") from e

    def AGENTS_FILE(self):
        return self.args['AGENTS_FILE']

    def name(self):
      return "create"

    def create(self):
        agents_yaml = parse_yaml(self.AGENTS_FILE())
        try:
            self.__create_agents(agents_yaml)
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to create agents: {str(e)}")
        return 0

# Run command group
#  maestro run AGENTS_FILE WORKFLOW_FILE [options]
class RunCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    def __run_agents_workflow(self, agents_yaml, workflow_yaml):
        try:
            workflow = Workflow(agents_yaml, workflow_yaml[0])
            asyncio.run(workflow.run())
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"{str(e)}") from e
        return 0
    
    def AGENTS_FILE(self):
        return self.args['AGENTS_FILE']

    def WORKFLOW_FILE(self):
        return self.args['WORKFLOW_FILE']

    def name(self):
      return "run"

    def run(self):
        agent_yaml = None
        if self.AGENTS_FILE() != "None":
            agent_yaml = parse_yaml( self.AGENTS_FILE())
        workflow_yaml = parse_yaml( self.WORKFLOW_FILE())
        try:
            self.__run_agents_workflow(agent_yaml, workflow_yaml)
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to run workflow: {str(e)}")
            return 1
        return 0
        
# Deploy command group
#  maestro deploy AGENTS_FILE WORKFLOW_FILE [options]
class DeployCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)
    
    def __deploy_agents_workflow(self, agents_yaml, workflow_yaml, env):
        try:
            if self.docker():
                deploy = Deploy(agents_yaml, workflow_yaml, env)
                deploy.deploy_to_docker()            
                Console.ok(f"Workflow deployed: http://127.0.0.1:5000")
            elif self.k8s():
                deploy = Deploy(agents_yaml, workflow_yaml, env)
                deploy.deploy_to_kubernetes()
                Console.ok(f"Workflow deployed: http://<kubernates address>:30051")
            else:
                Console.error("Need to specify --docker or --k8s | --kubernetes")
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"Unable to deploy workflow: {str(e)}") from e
        return 0            

    def url(self):
        if self.args['--url'] == "" or self.args['--url'] == None:
            return "127.0.0.1:5000"
        return self.args['--url'] 

    def k8s(self):
        if self.args['--k8s'] != "":
            return self.args['--k8s']
        return self.args['--kubernetes'] 

    def docker(self):
        return self.args['--docker']

    def AGENTS_FILE(self):
        return self.args['AGENTS_FILE']

    def WORKFLOW_FILE(self):
        return self.args['WORKFLOW_FILE']

    def ENV(self):
        return " ".join(self.args['ENV'])

    def name(self):
      return "deploy"

    def deploy(self):
        try:
            self.__deploy_agents_workflow(self.AGENTS_FILE(), self.WORKFLOW_FILE(), self.ENV())
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to deploy workflow: {str(e)}")
            return 1
        return 0

# Mermaid command group
# $ maestro mermaid WORKFLOW_FILE [options]
class MermaidCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    # private    
    def __mermaid(self, workflow_yaml) -> str:
        mermaid = ""
        workflow = Workflow(None, workflow_yaml)
        if self.sequenceDiagram():
            mermaid = workflow.to_mermaid("sequenceDiagram")
        elif self.flowchart_td():
            mermaid = workflow.to_mermaid("flowchart", "TD")
        elif self.flowchart_lr():            
            mermaid = workflow.to_mermaid("flowchart", "LR")
        else:
            mermaid = workflow.to_mermaid("sequenceDiagram")
        return mermaid

    # public options
    def WORKFLOW_FILE(self):
        return self.args.get('WORKFLOW_FILE')

    def sequenceDiagram(self):
        return self.args.get('--sequenceDiagram')

    def flowchart_td(self):
        return self.args.get('--flowchart-td')

    def flowchart_lr(self):
        return self.args.get('--flowchart-lr')

    def name(self):
      return "mermaid"

    # public command method
    def mermaid(self):
        workflow_yaml = parse_yaml(self.WORKFLOW_FILE())
        try:            
            mermaid = self.__mermaid(workflow_yaml)
            Console.ok("Created mermaid for workflow\n")
            Console.print(mermaid + "\n")
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to generate mermaid for workflow: {str(e)}")
            return 1
        return 0
