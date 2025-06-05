import os
import json
import re
import sys

# Make everything relative to where the script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cbom_path = os.path.join(BASE_DIR, "example-cbom.json")
workspace_dir = os.path.join(BASE_DIR, "workspace")
patch_path = os.path.join(workspace_dir, "patch")

# Load the CBOM file
with open(cbom_path) as f:
    cbom = json.load(f)

github_token = os.getenv("GITHUB_TOKEN")
email = "patcher@cbom.ai"
name = "Fixer Agent"

# Extract repo info
props = {p["name"]: p["value"] for p in cbom["metadata"]["properties"]}
repo_url = props["git-url"]
match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repo_url)
org, repo = match.group(1), match.group(2)

# Identify remediation targets
findings = []
for component in cbom.get("components", []):
    algo = component.get("cryptoProperties", {}).get("algorithmProperties", {})
    if algo.get("parameterSetIdentifier") == "128":
        for occ in component.get("evidence", {}).get("occurrences", []):
            findings.append({"filename": occ["location"], "remediation": "KEYLEN01"})

# Clone and patch
os.system(f"rm -fr {workspace_dir} && mkdir -p {workspace_dir} && cd {workspace_dir} && git clone https://{github_token}@github.com/{org}/{repo}.git repo && cd repo && git checkout -b staging")
os.system(f"cd {workspace_dir}/repo && git config user.email {email} && git config user.name {name} >../out 2>&1")

for f in findings:
    filename = f["filename"]
    if sys.platform == "darwin":
        sed_iparm = "-i ''"
    else:
        sed_iparm = "-i"
    os.system(f"cd {workspace_dir}/repo && sed {sed_iparm} 's/128/256/g' {filename}")

os.system(f"cd {workspace_dir}/repo && git add . > ../out 2>&1")
os.system(f"cd {workspace_dir}/repo && git commit -m 'CBOM patch applied' > ../out 2>&1")
os.system(f"cd {workspace_dir}/repo && git format-patch --stdout -1 HEAD > {patch_path} 2>&1")

with open(patch_path, "r") as f:
    patch = f.read()

os.system(f"cd {workspace_dir} && rm -fr repo")
print("✅ Patch updated successfully.")
