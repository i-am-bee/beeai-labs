from fixer_agent import main
import json
import os

with open("example-cbom.json") as f:
    cbom_data = f.read()

os.environ["GITHUB_TOKEN"] = "placeholder"
patch = main([cbom_data], context=None)
print(patch)