# Assisted by watsonx Code Assistant
from flask import Flask, request, jsonify
import os
import json
import sys
import io
import asyncio

import yaml
from src.workflow import Workflow

app = Flask(__name__)

def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data

@app.route('/', methods=['GET'])
def process_workflow():
    if request.method == 'GET':
        agents_yaml = parse_yaml("src/agents.yaml")
        workflow_yaml = parse_yaml("src/workflow.yaml")
        try:
            workflow_instance = Workflow(agents_yaml, workflow_yaml[0])
        except Exception as excep:
            raise RuntimeError("Unable to create agents") from excep

        output = io.StringIO()
        sys.stdout = output
        asyncio.run(workflow_instance.run())
        sys.stdout = sys.__stdout__

        response = {
            'output': output.getvalue()
        }
        if os.getenv("DEBUG"):
            return response
        else:
            return output.getvalue()
if __name__ == '__main__':
    app.run(host='0.0.0.0')
