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

from cli.commands import Validate, Create, Run, Deploy

class CLI:
    def __init__(self, args):
        self.args = args
        if self.args['--verbose']:
            VERBOSE = True

    def command(self):
        if self.args.get('validate') and self.args['validate']:
            return Validate(self.args)
        elif self.args.get('create') and self.args['create']:
            return Create(self.args)
        elif self.args.get('run') and self.args['run']:
            return Run(self.args)
        elif self.args.get('deploy') and self.args['deploy']:
            return Deploy(self.args)
        else:
            raise Exception("Invalid command")
