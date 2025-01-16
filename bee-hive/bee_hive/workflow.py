#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import yaml
import dotenv

dotenv.load_dotenv()

class Workflow:
def __init__(self, workflow)


def sequential_workflow(workflow):
    prompt = workflow["spec"]["template"]["prompt"]
    agents = workflow["spec"]["template"]["agents"]
    if (
        workflow_yaml["spec"]["strategy"]["output"]
        and workflow_yaml["spec"]["strategy"]["output"] == "verbose"
    ):
        run_workflow = run_streaming_agent
    else:
        run_workflow = run_agent
    for agent in agents:
        prompt = run_workflow(agent[agent, prompt)
    return prompt



