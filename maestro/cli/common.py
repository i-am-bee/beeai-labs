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

import sys

VERBOSE=False

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Console:
    def verbose(msg):
        if VERBOSE:
            print(f"{Colors.OKBLUE}{msg}{Colors.ENDC}".format(msg=str(msg)))

    def print(msg=''):
        print(msg)

    def println(no=1):
        for i in range(no):
            print()

    def ok(msg):
        print(f"{Colors.OKGREEN}{msg}{Colors.ENDC}".format(msg=str(msg)))

    def error(msg):
        Console.fail(msg)

    def fail(msg):
        print(f"{Colors.FAIL}Error: {msg}{Colors.ENDC}".format(msg=str(msg)))

    def warn(msg):
        print(f"{Colors.WARNING}Warning: {msg}{Colors.ENDC}".format(msg=str(msg)))

    def progress(count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()