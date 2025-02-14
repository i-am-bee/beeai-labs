#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

# import dotenv
from openai import OpenAI
import yaml
import dotenv
from src.workflow import Workflow

dotenv.load_dotenv()

def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: docker run maestro -e <env1=valuse1> -e <env2=value2> <agent yaml file mane> <workflow yaml file name>")
        sys.exit()
    agents_yaml = parse_yaml(sys.argv[1])
    workflow_yaml = parse_yaml(sys.argv[2])
    try:
        workflow = Workflow(agents_yaml, workflow_yaml[0])
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep
    workflow.run()
