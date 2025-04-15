#!/usr/bin/env python3
import json
import os
import re
import dotenv
import time

from agents.agent_finder import run_finder_agent
from agents.agent_fixer import run_fixer_agent
from agents.agent_patcher import run_patcher_agent

dotenv.load_dotenv()

if __name__ == "__main__":

    # If set we don't use the output of Agent 1 for Agent 2, but instead use pre-setup files
    # -- backup only for testing/demos in case of issues
    #use_files  = ( os.environ.get("BEE_NOCHAIN") is not None)
    use_files= False

    def heading(text: str) -> str:
        """Helper function for centering text."""
        return "\n" + f"".center(80, "*") + "\n" + f" {text} ".center(80, "=") + "\n" + f"".center(80, "*") + "\n"

    # 1. Using the CBOM, figure out the relevant findings we want to remediate
    #    This is a scan from the sonarqube scanner (not cbom-ai)

    print(heading(text="1. CBOM-AI Remediation Finder"))
    if ((pause:=os.environ.get("BEE_DEMOPAUSE")) is not None):
        time.sleep(int(pause))

    with open('data/Mastercard-client-encryption-java.cbom','r') as c:
        cbom=json.load(c)

    findings_full = run_finder_agent(cbom)
    if ((pause:=os.environ.get("BEE_DEMOPAUSE")) is not None):
        time.sleep(int(pause))

    if use_files is not True:
        # File is returned within  ```json / ``` markers. Extract to chain into next step
        #match = re.search(r'```json(.*?)```', findings_full, re.DOTALL)
        match = re.search(r'```(.*?)```', findings_full, re.DOTALL)
        if match:
            code_block = match.group(1)
        else:
            print("ERROR: No code block found.")
            exit(1)
    else:
        with open('data/findings.json','r') as f:
            code_block=f.read()

    # 2. Using the findings above, create a git patch
    #    This is edited from results of above - just to extract the json

    print(heading(text="2. CBOM-AI Remediation Fixer"))
    if ((pause:=os.environ.get("BEE_DEMOPAUSE")) is not None):
        time.sleep(int(pause))

    # uncomment to use a hardcoded file - in case of issues with the above
    #with open('data/findings.json','r') as f:
    #    findings=f.read()

    patch_full=run_fixer_agent(code_block)

    if use_files is not True:
        # File is returned within  ``` / ``` markers. Extract to chain into next step
        #match = re.search(r'```json(.*?)```', patch_full, re.DOTALL)
        match = re.search(r'```(.*?)```', patch_full, re.DOTALL)
        if match:
            patch_block = match.group(1)
        else:
            print("ERROR: No patch found.")
            exit(1)
    else:
        with open('data/patchfile') as f:
            patch_block=f.read()

    # 3. Apply the above patchfile
    #    Again, this is edited to strip out the relevant information

    print(heading(text="3. CBOM-AI Remediation Patcher"))
    if ((pause:=os.environ.get("BEE_DEMOPAUSE")) is not None):
        time.sleep(int(pause))
    output = run_patcher_agent("https://github.com/planetf1/client-encryption-java",patch_block)
