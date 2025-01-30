# Assisted by watsonx Code Assistant 
from flask import Flask, request, jsonify
import os
import json
import sys
import io

import yaml
from bee_hive.workflow import Workflow

app = Flask(__name__)

def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data

@app.route('/', methods=['POST'])
def process_workflow():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'agents' not in request.files:
            return 'No agent definition'

        agents = request.files['agents']

        # Check if the file has a filename
        if agents.filename == '':
            return 'No agents file name'

        # Save the file to the server
        agents.save("agents")

        if 'workflow' not in request.files:
            return 'No agent definition'

        workflow = request.files['workflow']

        # Check if the file has a filename
        if workflow.filename == '':
            return 'No workflow file name'

        # Save the file to the server
        workflow.save("workflow")

        agents_yaml = parse_yaml("agents")
        workflow_yaml = parse_yaml("workflow")
        try:
            workflow_instance = Workflow(agents_yaml, workflow_yaml[0])
        except Exception as excep:
            raise RuntimeError("Unable to create agents") from excep

        output = io.StringIO()
        sys.stdout = output
        workflow_instance.run()
        sys.stdout = sys.__stdout__
        
        response = {
            'workflow': workflow.filename,
            'agents': agents.filename,
            'output': output.getvalue()
        }

        return jsonify(response)

    return render_template('upload.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0')

