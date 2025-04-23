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

import os, signal, sys, yaml, json, jsonschema, traceback, asyncio, psutil

import streamlit.web

from subprocess import Popen

from openai import OpenAI
from jsonschema.exceptions import ValidationError, SchemaError

from src.deploy import Deploy
from src.workflow import Workflow, create_agents
from cli.common import Console, parse_yaml, read_file
from cli.streamlit_deploy import deploy_agents_workflow_streamlit

# Root CLI class
class CLI:
    def __init__(self, args):
        self.args = args
        VERBOSE, DRY_RUN, SILENT = False, False, False
        if self.args['--verbose']:
            VERBOSE = True
        if self.args['--dry-run']:
            DRY_RUN = True
        if self.args['--silent']:
            SILENT = True

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
        elif self.args.get('meta-agents') and self.args['meta-agents']:
            return MetaAgentsCmd(self.args)
        elif self.args.get('clean') and self.args['clean']:
            return CleanCmd(self.args)
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
    
    def silent(self):
        return self.args['--silent']

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
        elif self.args['meta-agents']:
            return self.meta_agents
        elif self.args['clean']:
            return self.clean
        else:
            raise Exception("Invalid subcommand")

# validate command group
#  maestro validate SCHEMA_FILE YAML_FILE [options]
class ValidateCmd(Command):
    TOOL_SCHEMA_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/../schemas/tool_schema.json"
    AGENT_SCHEMA_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/../schemas/agent_schema.json"
    WORKFLOW_SCHEMA_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/../schemas/workflow_schema.json"
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    # private

    def __discover_schema_file(self, yaml_file):
        try:
            yaml_data = parse_yaml(yaml_file)
            if type(yaml_data) == list:
                yaml_data = yaml_data[0]

            kind = yaml_data.get('kind')
            if kind == 'Agent':
                return ValidateCmd.AGENT_SCHEMA_FILE
            elif kind == 'Tool':
                return ValidateCmd.TOOL_SCHEMA_FILE
            elif kind == 'Workflow':
                return ValidateCmd.WORKFLOW_SCHEMA_FILE
            else:
                raise f"Unknown kind: {kind}"
        except Exception as e:
            Console.error(f"Could not parse yaml file: {yaml_file}")
            raise e

    def __validate(self, schema_file, yaml_file):
        Console.print(f"validating {yaml_file} with schema {schema_file}")
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        with open(yaml_file, 'r') as f:
            yamls = yaml.safe_load_all(f)
            for yaml_data in yamls:
                json_data = json.dumps(yaml_data, indent=4)
                try:
                    jsonschema.validate(yaml_data, schema)
                    if not self.silent():
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

    # public

    def SCHEMA_FILE(self):
        return self.args['SCHEMA_FILE']

    def YAML_FILE(self):
        return self.args['YAML_FILE']

    def name(self):
      return "validate"

    def validate(self):
        if self.SCHEMA_FILE() == None or self.SCHEMA_FILE() == '':
            discovered_schema_file = ''
            try:
                discovered_schema_file = self.__discover_schema_file(self.YAML_FILE())
            except Exception as e:
                Console.error(f"Invalid YAML file: {self.YAML_FILE()}: {str(e)}")
                return 1
            return self.__validate(discovered_schema_file, self.YAML_FILE())
        return self.__validate(self.SCHEMA_FILE(), self.YAML_FILE())

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

    # private

    def __run_agents_workflow(self, agents_yaml, workflow_yaml):
        try:
            workflow = Workflow(agents_yaml, workflow_yaml[0])
            asyncio.run(workflow.run())
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"{str(e)}") from e
        return 0

    def __read_prompt(self):
        return Console.read('Enter your prompt: ')

    # public

    def AGENTS_FILE(self):
        return self.args['AGENTS_FILE']

    def WORKFLOW_FILE(self):
        return self.args['WORKFLOW_FILE']

    def prompt(self):
        return self.args.get('--prompt')

    def name(self):
      return "run"

    def run(self):
        agents_yaml, workflow_yaml = None, None
        if self.AGENTS_FILE() != None and self.AGENTS_FILE() != 'None':
            agents_yaml = parse_yaml(self.AGENTS_FILE())
        workflow_yaml = parse_yaml(self.WORKFLOW_FILE())

        if self.prompt():
            prompt = self.__read_prompt()
            workflow_yaml[0]['spec']['template']['prompt'] = prompt

        try:
            self.__run_agents_workflow(agents_yaml, workflow_yaml)
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
    
    def __deploy_agents_workflow_streamlit(self):
        try:
            sys.argv = ["streamlit", "run", "--ui.hideTopBar", "True", "--client.toolbarMode", "minimal", f"{os.getcwd()}/cli/streamlit_deploy.py", self.AGENTS_FILE(), self.WORKFLOW_FILE()]
            process = Popen(sys.argv)
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"{str(e)}") from e
        return 0

    def __deploy_agents_workflow(self, agents_yaml, workflow_yaml, env):
        try:
            if self.docker():
                deploy = Deploy(agents_yaml, workflow_yaml, env)
                deploy.deploy_to_docker()  
                if not self.silent():
                    Console.ok(f"Workflow deployed: http://127.0.0.1:5000")
            elif self.k8s():
                deploy = Deploy(agents_yaml, workflow_yaml, env)
                deploy.deploy_to_kubernetes()
                if not self.silent():
                    Console.ok(f"Workflow deployed: http://<kubernetes address>:30051")            
            else:
                self.__deploy_agents_workflow_streamlit()
                if not self.silent():
                    Console.ok(f"Workflow deployed: http://localhost:8501/?embed=true")
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"Unable to deploy workflow: {str(e)}") from e
        return 0            

    def auto_prompt(self):
        return self.args.get('--auto-prompt', False)

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

    def streamlit(self):
        return self.args['--streamlit']

    def AGENTS_FILE(self):
        return self.args['AGENTS_FILE']

    def WORKFLOW_FILE(self):
        return self.args['WORKFLOW_FILE']

    def ENV(self):
        env_vars = self.args['ENV']
        if self.auto_prompt():
            env_vars.append("AUTO_RUN=true")
        return " ".join(env_vars)

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
            if not self.silent():
                Console.ok("Created mermaid for workflow\n")
            Console.print(mermaid + "\n")
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to generate mermaid for workflow: {str(e)}")
            return 1
        return 0

# MetaAgents command group
# $ maestro meta-agents TEXT_FILE [options]
class MetaAgentsCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    # private    
    def __meta_agents(self, text_file) -> int:
        try:
            sys.argv = ["streamlit", "run", "--ui.hideTopBar", "True", "--client.toolbarMode", "minimal", f"{os.getcwd()}/cli/streamlit_meta_agents_deploy.py", text_file]
            process = Popen(sys.argv)
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"{str(e)}") from e
        return 0

    # public options
    def TEXT_FILE(self):
        return self.args.get('TEXT_FILE')

    def name(self):
      return "meta-agents"

    # public command method
    def meta_agents(self):
        try:
            rc = self.__meta_agents(self.TEXT_FILE())
            if not self.silent():
                Console.ok("Running meta-agents\n")
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to run meta-agents: {str(e)}")
            return 1
        return 0

# Create command group
#  maestro create AGENTS_FILE [options]
class CleanCmd(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    def __clean(self):
        try:
            for pid in psutil.pids():
                try:
                    process = psutil.Process(pid)
                    cmd = process.cmdline()
                    if len(cmd) > 3 and "streamlit" in cmd[1]:
                        process.send_signal(signal.SIGTERM)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            self._check_verbose()
            raise RuntimeError(f"{str(e)}") from e

    def name(self):
      return "clean"

    def clean(self):
        try:
            self.__clean()
        except Exception as e:
            self._check_verbose()
            Console.error(f"Unable to clean: {str(e)}")
            return 1
        return 0
