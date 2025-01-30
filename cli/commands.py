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

import io, sys, yaml, json, jsonschema

from common import Console

# Base class for all commands
class Command:
    def __init__(self, args):
        self.args = args
    
    def println(self, msg):
        self.print(msg + "\n")

    def print(self, msg):
        Console.print(msg)

    def warn(self, msg):
        Console.warn(msg)

    def verbose(self):
        return self.args['--verbose']
    
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
        else:
            raise Exception("Invalid subcommand")

# validate command group
class Validate(Command):
    def __init__(self, args):
        self.args = args
        super().__init__(self.args)

    def SCHEMA_FILE(self):
        return self.args['SCHEMA_FILE']

    def YAML_FILE(self):
        return self.args['SCHEMA_FILE']

    def name(self):
      return "validate"

    def validate(self):
        Console.print("validate {yaml_file} with schema {schema_file}".format(yaml_file=self.YAML_FILE(), schema_file=self.SCHEMA_FILE()))
        with open(self.SCHEMA_FILE(), 'r') as f:
            schema = json.load(f)
        with open(self.YAML_FILE(), 'r') as f:
            yamls = yaml.safe_load_all(f)
            for yaml_data in yamls:
                json_data = json.dumps(yaml_data, indent=4)
                jsonschema.validate(yaml_data, schema)
                Console.print("YAML file is valid.")
        return 0
