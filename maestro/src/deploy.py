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

import os, dotenv
import shutil
import subprocess
import yaml

# cmd="podman"
# env="BEE_API_KEY=sk-proj-testkey BEE_API=http://192.168.86.45:4000"
# target="127.0.0.1:5000"

dotenv.load_dotenv() #TODO is this needed now that __init__.py in package runs this?

def env_array_docker(str_envs):
    env_array = str_envs.split()
    env_args = []
    for env in env_array:
        env_args.append("-e")
        env_args.append(env)
    return(env_args)

def flag_array_build(str_flags):
    flag_array = str_flags.split()
    flags = []
    for flag in flag_array:
        key, value = flag.split("=")
        flags.append(key)
        flags.append(value)
    return(flags)

def create_docker_args(cmd, target, env):
    arg = [f"{cmd}", "run", "-d", "-p", f"{target}:5000"]
    arg.extend(env_array_docker(env))
    arg.append("maestro")
    return arg

def create_build_args(cmd, flags):
    arg = [f"{cmd}", "build"]
    if flags:
        print(flags)
        arg.extend(flag_array_build(flags))
    arg.extend(["-t", "maestro", "-f", "Dockerfile", ".."])
    return arg

def update_yaml(yaml_file, str_envs):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    pairs = str_envs.split()
    for pair in pairs:
        key, value = pair.split('=')
        data['spec']['template']['spec']['containers'][0]['env'].append({'name': key, 'value': value})
    with open(yaml_file, 'w') as f:
        yaml.safe_dump(data, f)

class Deploy:
    def __init__(self, agent_defs, workflow_defs, env=None, target=None):
        self.agent = agent_defs
        self.workflow = workflow_defs
        self.env = env
        self.target = target or "127.0.0.1:5000"
        self.cmd = os.getenv("CONTAINER_CMD", "docker")
        self.flags = os.getenv("BUILD_FLAGS")

    def build_image(self, agent, workflow):
        shutil.copytree("../deployments", "../tmp", dirs_exist_ok=True)
        shutil.copy(agent, "../tmp/agents.yaml")
        shutil.copy(workflow, "../tmp/workflow.yaml")

        os.chdir("../tmp")
        subprocess.run(create_build_args(self.cmd, self.flags))

    def deploy_to_docker(self):
        self.build_image(self.agent, self.workflow)
        subprocess.run(create_docker_args(self.cmd, self.target, self.env))
    
    def deploy_to_kubernetes(self):
        self.build_image(self.agent, self.workflow)
        update_yaml("deployment.yaml", self.env)
        subprocess.run(["kubectl", "apply", "-f", "deployment.yaml"])
        subprocess.run(["kubectl", "apply", "-f", "service.yaml"])

#if __name__ == '__main__':
    #deploy = Deploy("../tests/examples/condition_agents.yaml", "../tests/examples/condition_workflow.yaml", "BEE_API_KEY=sk-proj-testkey BEE_API=http://192.168.86.45:4000", "127.0.0.1:5000")
    #deploy.deploy_to_docker()
    #deploy = Deploy("../tests/examples/condition_agents.yaml", "../tests/examples/condition_workflow.yaml", "BEE_API_KEY=sk-proj-testkey BEE_API=http://192.168.86.45:4000")
    #deploy.deploy_to_kubernetes()
