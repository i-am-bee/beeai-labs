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

import os, dotenv, inspect
import shutil
import subprocess
import yaml
import tempfile

dotenv.load_dotenv()

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
    def __init__(self, agent_defs, workflow_defs, env="", target=None):
        self.agent = agent_defs
        self.workflow = workflow_defs
        self.env = env
        self.target = target or "127.0.0.1:5000"
        self.cmd = os.getenv("CONTAINER_CMD", "docker")
        self.flags = os.getenv("BUILD_FLAGS")

    def build_image(self, agent, workflow):
        module_path = os.path.abspath(inspect.getsourcefile(lambda:0))
        module_dir = os.path.dirname(module_path)
        self.tmp_dir = os.path.join(tempfile.gettempdir(), "maestro")
        shutil.copytree(os.path.join(module_dir, ".."), self.tmp_dir, dirs_exist_ok=True)
        shutil.copytree(os.path.join(module_dir, "../deployments"), os.path.join(self.tmp_dir, "tmp"), dirs_exist_ok=True)
        shutil.copy(agent, os.path.join(self.tmp_dir, "tmp/agents.yaml"))
        shutil.copy(workflow, os.path.join(self.tmp_dir, "tmp/workflow.yaml"))

        cwd = os.getcwd()
        os.chdir(os.path.join(self.tmp_dir, "tmp"))
        subprocess.run(create_build_args(self.cmd, self.flags))
        os.chdir(cwd)

    def deploy_to_docker(self):
        self.build_image(self.agent, self.workflow)
        subprocess.run(create_docker_args(self.cmd, self.target, self.env))
        shutil.rmtree(self.tmp_dir)

    def deploy_to_kubernetes(self):
        module_path = os.path.abspath(inspect.getsourcefile(lambda:0))
        module_dir = os.path.dirname(module_path)

        self.build_image(self.agent, self.workflow)
        update_yaml(os.path.join(self.tmp_dir, "tmp/deployment.yaml"), self.env)
        image_tag_command  = os.getenv("IMAGE_TAG_CMD")
        if image_tag_command:
            subprocess.run(image_tag_command.split())
        image_push_command  = os.getenv("IMAGE_PUSH_CMD")
        if image_push_command:
            subprocess.run(image_push_command.split())
        subprocess.run(["kubectl", "apply", "-f", os.path.join(self.tmp_dir, "tmp/deployment.yaml")])
        subprocess.run(["kubectl", "apply", "-f", os.path.join(self.tmp_dir, "tmp/service.yaml")])
        shutil.rmtree(self.tmp_dir)

