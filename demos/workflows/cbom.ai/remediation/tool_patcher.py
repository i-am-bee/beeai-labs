#!/usr/bin/env python3
import json
import os
import random


def patcher_tool(
    repositoryURL: str, patch: str, github_apikey: str, email: str, name: str
) -> str:
    """
    The cbom patcher tool takes a github repository URL (input parameter) and
    applies the supplied patch to the source code. It then raises a pull
    request for the change.

    Args:
        repositoryURL (str): The repository URL on github
        patch (str): A 'git-patch' formatted patch as a string. This must not be a file
        github_apikey (str): Valid github api token to access repository
        email (str): Email address of the person or system making the commits
        name (str): Name of the person or system making the commits

    Returns:
        str: The URL of the Pull Request
    """
    import os
    import re

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "ENTRY")
        print("DEBUG: [patcher-tool] " + "repositoryURL: " + repositoryURL)
        print("DEBUG: [patcher-tool] " + "patch: " + patch)
        print("DEBUG: [patcher-tool] " + "github_apikey: " + github_apikey)
        print("DEBUG: [patcher-tool] " + "email: " + email)
        print("DEBUG: [patcher-tool] " + "name: " + name)

    match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repositoryURL)
    if match:
        org = match.group(1)
        repo = match.group(2)
        repobase = org + "/" + repo

    branch = "remediation_" + str(random.randint(0, 9999))

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "repositoryURL: " + repositoryURL)
        print("DEBUG: [patcher-tool] " + "org: " + org)
        print("DEBUG: [patcher-tool] " + "repo: " + repo)
        print(
            "DEBUG: [patcher-tool] "
            + "Cloning, assigning email/name, and setting up working branch"
        )

    os.system(
        "rm -fr workspace && mkdir -p workspace && cd workspace && git clone "
        + "https://"
        + github_apikey
        + "@github.com/"
        + org
        + "/"
        + repo
        + ".git"
        + " repo"
        + " && cd repo && git checkout -b "
        + branch
        + " >../out 2>&1"
    )
    os.system(
        "cd workspace/repo && git config user.email "
        + email
        + " && git config user.name "
        + name
        + " >../out 2>&1"
    )

    # patch
    patch_len = len(patch)
    if patch_len < 200:
        return "ERROR. Specify a valid patch. " + str(patch_len) + " is too short"

    with open("workspace/patchfile", "w") as f:
        f.write(patch)
        f.close()

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "Applying patch")
    os.system("cd workspace/repo && git am < '../patchfile' >../out 2>&1")

    with open("workspace/out", "r") as f:
        patch_output = f.read()

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "Pushing update")
    os.system(
        "cd workspace/repo && git push --force --set-upstream origin "
        + branch
        + " >../out 2>&1"
    )

    with open("workspace/out", "r") as f:
        patch_output = f.read()

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "Opening PR")
    os.environ["GH_TOKEN"] = github_apikey
    os.system("cd workspace/repo && gh repo set-default " + repobase + " >../out 2>&1")
    # Currently fails in agent only with 'pull request create failed: GraphQL: No commits between main and remediation_4895 (createPullRequest)'
    os.system(
        "cd workspace/repo && gh pr create --title 'QSC Remediation fix' --body 'Autofix by agent' --base main > ../out 2>&1"
    )

    with open("workspace/out", "r") as f:
        patch_output = f.read()

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "Output from patch: " + patch_output)
        print("DEBUG: [patcher-tool] " + "Output from patch: " + patch_output)
        print("DEBUG: [patcher-tool] " + "Clearing up workspace")

    os.system("cd workspace && rm -fr repo >out 2>&1")

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "EXIT")

    # return as json
    return patch_output


# Run the pipeline (unless in library) - useful test case
# END
if __name__ == "__main__":

    with open("data/patchfile.master", "r") as f:
        patch = f.read()
        api_token = os.environ.get("GH_TOKEN")
        result = patcher_tool(
            "https://github.com/planetf1/client-encryption-java",
            patch,
            api_token,
            "test@research.ibm.com",
            "Test User",
        )
        print(result)
