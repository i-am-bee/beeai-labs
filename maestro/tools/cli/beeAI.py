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

  beeAI (-h | --help)
  beeAI (-v | --version)

Options:
  --verbose                      Show all output.

  -h --help                      Show this screen.
  -v --version                   Show version.

"""
import os, sys, traceback

import warnings

# TODO: remoce this after solving doctopt warnings or using different CLI library
with warnings.catch_warnings():
    warnings.simplefilter("ignore", SyntaxWarning)

from docopt import docopt

from cli import *

if __name__ == '__main__':
    args = docopt(__doc__, version='beeAI CLI v0.0.0')
    command = CLI(args).command()
    rc = command.execute()
    if rc != 0:
        Console.error("executing command: {rc}".format(rc=rc))
        sys.exit(rc)
