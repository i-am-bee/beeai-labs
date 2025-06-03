#!/usr/bin/env python3
import json
import os
import platform
import sys

def fixer_tool(reports: str, github_apikey: str) -> str:
    """
    The cbom problem fixer tool takes a remediation report (input parameter) in JSON format and applies the patches to the source code. It then returns this
        patchfile to the user

    Supported remediations:
    * KEYLEN01

    Args:
        report (str): The findings report in JSON format
        github_apikey (str): An api key for github

    Returns:
        str: git patch (which can be applied to source)
    """
    import os
    import re

    report=json.loads(reports)

    # TODO: This could be a tool, taking a single entry?
    # begin main

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [fixer-tool] " + "ENTRY")
        print("DEBUG: [fixer-tool] " + "reports: " + reports)
        print("DEBUG: [fixer-tool] " + "github_apikey: " + github_apikey)

    # hardcode for now
    email="patcher@research.ibm.com"
    name="patcher agent"


    repositoryURL: str = report["repository"]
    match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repositoryURL)
    if match:
        org = match.group(1)
        repo = match.group(2)
        repobase = org + "/" + repo

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [fixer-tool] " + "repositoryURL: " + repositoryURL)
        print("DEBUG: [fixer-tool] " + "org: " + org)
        print("DEBUG: [fixer-tool] " + "repo: " + repo)
        print("DEBUG: [fixer-tool] " + "Cloning & setting up working branch")


    os.system("rm -fr workspace && mkdir -p workspace && cd workspace && git clone " + "https://" + str(github_apikey) + "@github.com/" + org + "/" + repo + ".git" + " repo" + " && cd repo && git checkout -b staging")

    os.system("cd workspace/repo && git config user.email " + email + " && git config user.name " + name + " >../out 2>&1")

    # Only works for a single patch at a time
    patch=""
    for f in report["findings"]:
        if f["remediation"] == 'KEYLEN01':
            if os.environ.get("BEE_DEBUG") is not None:
                print("DEBUG: [fixer-tool] " + "Found remediation to process for: " + f["filename"] )
            # MacOS sed needs different parm for in-place edit

            if sys.platform == "darwin":
                sed_iparm="-i \'\'"
            else:
                sed_iparm="-i"
            os.system("cd workspace/repo && sed " + sed_iparm + " \'s/128/256/g\'"+ " " + f["filename"])

            os.system(command="cd workspace/repo && git add . > ../out 2>&1")
            os.system(command="cd workspace/repo && git commit -m 'Bee patched!' > ../out 2>&1")
            os.system(command="cd workspace/repo && git format-patch --stdout -1 HEAD > ../patch 2>&1")



    with open('workspace/patch','r') as f:
        patch=f.read()


    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [fixer-tool] " + "patch: " + patch)
        print("DEBUG: [patcher-tool] " + "clearing up workspace")

    os.system("cd workspace && rm -fr repo")

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [fixer-tool] " + "EXIT")


    return(patch)
    # end main

# END
# Run the pipeline (unless in library) - useful test case
if __name__ == "__main__":
    api_token=os.environ.get("GH_TOKEN")
    with open('data/findings.json','r') as f:
        report=f.read()
        patch=fixer_tool(report,api_token)
        print(patch)