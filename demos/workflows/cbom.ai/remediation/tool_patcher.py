#!/usr/bin/env python3
import json
import os
import random


def patcher_tool(
    repositoryURL: str,
    patch: str,
) -> str:
    """
    The cbom patcher tool takes a github repository URL (input parameter) and
    applies the supplied patch to the source code. It then raises a pull
    request for the change.

    Args:
        repositoryURL (str): The repository URL on github
        patch (str): A 'git-patch' formatted patch as a string. This must not be a file

    The GitHub API key is sourced from the `GITHUB_TOKEN` environment variable.
    The email address for commits is taken from the `PATCHER_EMAIL` environment
    variable (defaulting to 'cbom-ai@research.ibm.com' if not set).
    The name for commits is taken from the `PATCHER_NAME` environment
    variable (defaulting to 'CBOM-AI remediation' if not set).

    Returns:
        str: The URL of the Pull Request, or an error string if the GitHub API
             key (from GITHUB_TOKEN environment variable) is not found.
    """
    import re

    # Resolve the GitHub API key from environment variable
    _effective_apikey = os.environ.get("GITHUB_TOKEN")
    if not _effective_apikey:
        return "ERROR: GitHub API key not provided and GITHUB_TOKEN environment variable is not set."

    # Resolve email and name from environment variables or use defaults
    _effective_email = os.environ.get("PATCHER_EMAIL", "cbom-ai@research.ibm.com")
    _effective_name = os.environ.get("PATCHER_NAME", "CBOM-AI remediation")

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "ENTRY")
        print("DEBUG: [patcher-tool] " + "repositoryURL: " + repositoryURL)
        print("DEBUG: [patcher-tool] " + "patch: " + patch)
        # Changed: Reflect that API key comes from env var
        print("DEBUG: [patcher-tool] " + "github_apikey (from GITHUB_TOKEN): " + (_effective_apikey if _effective_apikey else "Not Set"))
        print("DEBUG: [patcher-tool] " + "email (from PATCHER_EMAIL or default): " + _effective_email)
        print("DEBUG: [patcher-tool] " + "name (from PATCHER_NAME or default): " + _effective_name)

    match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repositoryURL)
    if match:
        org = match.group(1)
        repo = match.group(2)
        repobase = org + "/" + repo
    else:
        return f"ERROR: Could not parse repository URL: {repositoryURL}"

    branch = "remediation_" + str(random.randint(0, 9999))

    if os.environ.get("BEE_DEBUG") is not None:
        print("DEBUG: [patcher-tool] " + "repositoryURL: " + repositoryURL)
        print("DEBUG: [patcher-tool] " + "org: " + org)
        print("DEBUG: [patcher-tool] " + "repo: " + repo)
        print(
            "DEBUG: [patcher-tool] "
            + "Cloning, assigning email/name, and setting up working branch"
        )

    # Use f-string for clarity and the resolved _effective_apikey
    os.system(
        f"rm -fr workspace && mkdir -p workspace && cd workspace && "
        f"git clone https://{_effective_apikey}@github.com/{org}/{repo}.git repo && "
        f"cd repo && git checkout -b {branch} >../out 2>&1"
    )
    os.system(
        "cd workspace/repo && git config user.email "
        + _effective_email
        + " && git config user.name "
        + _effective_name
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
    os.environ["GH_TOKEN"] = _effective_apikey # Use the resolved key for gh cli
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
        # Test with explicit None to check env var fallback for apikey
        result = patcher_tool(
            "https://github.com/planetf1/client-encryption-java",
            patch,
        )
        print(result)
