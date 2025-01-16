#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import yaml
import dotenv

dotenv.load_dotenv()

class Workflow:
    agents = []
    def __init__(self, agent_defs)
        """Execute sequential workflow.
        input:
            agents: array of agent definitions
        """
        for agent_def in agent_defs:
            agents.append(new Agent(agent_def))


    def sequential_workflow(workflow):
        """Execute sequential workflow.
        input: workflow
            workflow["spec"]["template"]["prompt"]: prompt for the agent
            workflow["spec"]["template"]["agents"]: array of agent instance
        """
    
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



