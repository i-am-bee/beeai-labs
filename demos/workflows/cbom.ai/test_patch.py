import os
import random
import re

# Base directory (the folder where this script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Read the patch file from workspace/
patch_path = os.path.join(BASE_DIR, "workspace", "patch")
with open(patch_path, "r") as f:
    patch = f.read()

# GitHub repo info
repo_url = "https://github.com/george-lhj/client-encryption-java"
github_token = os.getenv("GITHUB_TOKEN")
email = "patcher@cbom.ai"
name = "Patcher Bot"

match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repo_url)
org, repo = match.group(1), match.group(2)
repobase = f"{org}/{repo}"
branch = f"remediation_{random.randint(1000, 9999)}"

print("⚠️  About to run patch workflow")
print(f"🔗 Repo URL: {repo_url}")
print(f"🌿 New branch: {branch}")
print("📄 Patch preview (first 10 lines):")
print("\n".join(patch.strip().splitlines()[:10]))
input("\n⏎ Press ENTER to continue, or Ctrl+C to cancel...")

# Setup workspace path
workspace_dir = os.path.join(BASE_DIR, "workspace")
os.system(f"rm -fr {workspace_dir} && mkdir -p {workspace_dir} && cd {workspace_dir} && git clone https://{github_token}@github.com/{org}/{repo}.git repo && cd repo && git checkout -b {branch}")
os.system(f"cd {workspace_dir}/repo && git config user.email {email} && git config user.name {name}")

# Write the patchfile
patchfile_path = os.path.join(workspace_dir, "patchfile")
with open(patchfile_path, "w") as f:
    f.write(patch)

# Apply patch and open PR
os.system(f"cd {workspace_dir}/repo && git am < ../patchfile")
os.system(f"cd {workspace_dir}/repo && git push --force --set-upstream origin {branch}")
os.environ["GH_TOKEN"] = github_token
os.system(f"cd {workspace_dir}/repo && gh repo set-default {repobase}")
os.system(f"cd {workspace_dir}/repo && gh pr create --title 'CBOM Fix' --body 'Auto-applied fix from patch' --base main")

# Cleanup
os.system(f"cd {workspace_dir} && rm -fr repo")
print(f"✅ Patch applied and PR created on branch: {branch}")
