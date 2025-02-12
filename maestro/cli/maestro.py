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

"""Maestro

Usage:
  maestro validate SCHEMA_FILE YAML_FILE [options]
  maestro create AGENTS_FILE [options]
  maestro run AGENTS_FILE WORKFLOW_FILE [options]
  maestro deploy AGENTS_FILE WORKFLOW_FILE [options]

  maestro (-h | --help)
  maestro (-v | --version)

Options:
  --verbose                      Show all output.
  --dry-run                      Mocks agents and other parts of workflow execution.

  -h --help                      Show this screen.
  -v --version                   Show version.

"""

import sys

from docopt import docopt

from .cli import CLI
from .common import Console

def __execute(command):
    try:
        rc = command.execute()
        if rc != 0:
            Console.error("executing command: {rc}".format(rc=rc))
        return rc
    except Exception as e:
        Console.error(str(e))
        return 1

def __run_cli():
    args = docopt(__doc__, version='beeAI CLI v0.0.1')
    command = CLI(args).command()
    rc = __execute(command)
    sys.exit(rc)
        
if __name__ == '__main__':
    __run_cli()
