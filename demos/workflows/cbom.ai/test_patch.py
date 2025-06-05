import os
import random
import re

# Load the patch file
with open("/Users/gliu/Desktop/work/maestro/demos/workflows/cbom.ai/workspace/patch", "r") as f:
    patch = f.read()

repo_url = "https://github.com/george-lhj/client-encryption-java"
github_token = os.getenv("GITHUB_TOKEN")
email = "patcher@cbom.ai"
name = "Patcher Bot"

# Parse GitHub repo info
match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", repo_url)
org, repo = match.group(1), match.group(2)
repobase = f"{org}/{repo}"
branch = f"remediation_{random.randint(1000, 9999)}"

# 🔒 Confirmation before proceeding
print("⚠️  About to run patch workflow")
print(f"🔗 Repo URL: {repo_url}")
print(f"🌿 New branch: {branch}")
print("📄 Patch preview (first 10 lines):")
print("\n".join(patch.strip().splitlines()[:10]))
input("\n⏎ Press ENTER to continue, or Ctrl+C to cancel...")

# Clone + setup
os.system(f"rm -fr workspace && mkdir -p workspace && cd workspace && git clone https://{github_token}@github.com/{org}/{repo}.git repo && cd repo && git checkout -b {branch}")
os.system(f"cd workspace/repo && git config user.email {email} && git config user.name {name}")

# Write and apply patch
with open("workspace/patchfile", "w") as f:
    f.write(patch)

os.system("cd workspace/repo && git am < ../patchfile")
os.system(f"cd workspace/repo && git push --force --set-upstream origin {branch}")
os.environ["GH_TOKEN"] = github_token
os.system(f"cd workspace/repo && gh repo set-default {repobase}")
os.system("cd workspace/repo && gh pr create --title 'CBOM Fix' --body 'Auto-applied fix from patch' --base main")

# Cleanup
os.system("cd workspace && rm -fr repo")
print(f"✅ Patch applied and PR created on branch: {branch}")
