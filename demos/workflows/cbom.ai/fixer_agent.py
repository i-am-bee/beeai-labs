import os
import json
import re
import sys

def main(args, context):
    cbom = json.loads(args[0])
    github_token = os.getenv("GITHUB_TOKEN")

    # Extract repo URL
    props = {p["name"]: p["value"] for p in cbom["metadata"]["properties"]}
    repo_url = props["git-url"]
    match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repo_url)
    org, repo = match.group(1), match.group(2)

    # Prepare findings
    findings = []
    for component in cbom.get("components", []):
        algo = component.get("cryptoProperties", {}).get("algorithmProperties", {})
        if algo.get("parameterSetIdentifier") == "128":
            for occ in component.get("evidence", {}).get("occurrences", []):
                findings.append({"filename": occ["location"], "remediation": "KEYLEN01"})

    # Git operations
    email = "patcher@cbom.ai"
    name = "Fixer Agent"
    os.system("rm -fr workspace && mkdir -p workspace && cd workspace && git clone https://"
              + github_token + "@github.com/" + org + "/" + repo + ".git repo && cd repo && git checkout -b staging")
    os.system(f"cd workspace/repo && git config user.email {email} && git config user.name {name} >../out 2>&1")

    for f in findings:
        filename = f["filename"]
        if sys.platform == "darwin":
            sed_iparm = "-i ''"
        else:
            sed_iparm = "-i"
        os.system(f"cd workspace/repo && sed {sed_iparm} 's/128/256/g' {filename}")
    os.system("cd workspace/repo && git add . > ../out 2>&1")
    os.system("cd workspace/repo && git commit -m 'CBOM patch applied' > ../out 2>&1")
    os.system("cd workspace/repo && git format-patch --stdout -1 HEAD > ../patch 2>&1")

    with open("workspace/patch", "r") as f:
        patch = f.read()

    os.system("cd workspace && rm -fr repo")
    return patch
