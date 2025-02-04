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

"""BeeAI

Usage:
  beeAI validate SCHEMA_FILE YAML_FILE [options]
  beeAI create AGENTS_FILE [options]
  beeAI run AGENTS_FILE WORKFLOW_FILE [options]
  beeAI deploy AGENTS_FILE WORKFLOW_FILE [options]

  beeAI (-h | --help)
  beeAI (-v | --version)

Options:
  --verbose                      Show all output.

  -h --help                      Show this screen.
  -v --version                   Show version.

"""
import sys

from docopt import docopt
from cli.common import Console
from cli.cli import CLI

def run_cli():
    """
    run CLI command
    """
    args = docopt(__doc__, version='beeAI CLI v0.0.1')
    command = CLI(args).command()
    try:
        rc = command.execute()
        if rc != 0:
            Console.error("executing command: {rc}".format(rc=rc))
            sys.exit(rc)
    except Exception as e:
        Console.error(str(e))
        sys.exit(1)
        
if __name__ == '__main__':
    run_cli()