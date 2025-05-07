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

import sys, subprocess

def lint():
    try:
        subprocess.run(["black", "."], check=True)
        subprocess.run(["ruff", "check", "."], check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)

def commit():
    try:
        if len(sys.argv) < 2:
            print("Error: Please provide a commit message")
            print('Usage: poetry run commit "<commit message>"')
            sys.exit(1)

        commit_message = sys.argv[1]

        print("📦 Adding files...")
        subprocess.run(["git", "add", "--all"], check=True)

        print("📝 Committing changes...")
        subprocess.run(["git", "commit", "-s", "-m", commit_message], check=True)

        print("Successfully committed changes")

    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
