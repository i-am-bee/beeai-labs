#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys
import dotenv
import yaml
from openai import OpenAI

dotenv.load_dotenv()


def parse_yaml(file_path):
    """Loads agent definitions from a YAML file."""
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))  # Supports multi-document YAML
    return yaml_data


def create_agent(agent):
    """Registers an agent with Bee API and returns its ID."""
    client = OpenAI(
        base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
    )

    agent_name = agent["metadata"]["name"]
    agent_model = agent["spec"]["model"]
    agent_desc = agent["spec"]["description"]
    agent_instr = agent["spec"].get("instruction", "")  # FIX: Schema uses 'instruction'
    agent_tools = []

    # Process tools
    for tool in agent["spec"].get("tools", []): 
        if tool == "code_interpreter":
            agent_tools.append({"type": tool})
        else:
            print(f"Enable the {tool} tool in the Bee UI")

    # Create assistant with Bee API
    assistant = client.beta.assistants.create(
        name=agent_name,
        model=agent_model,
        description=agent_desc,
        tools=agent_tools,
        instructions=agent_instr,  # FIX: Uses 'instruction' from schema
    )

    return assistant.id


def create_agents(agents_yaml):
    """Iterates through all agents and registers them."""
    agent_store = {}
    for agent in agents_yaml:
        try:
            agent_id = create_agent(agent)
            print(f"🐝 Created agent {agent['metadata']['name']}: {agent_id}")
            agent_store[agent["metadata"]["name"]] = agent_id
        except Exception as e:
            print(f"⚠️ Failed to create agent {agent['metadata']['name']}: {e}")

    # Save agent IDs for later use
    with open("agent_store.json", "w") as f:
        json.dump(agent_store, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_agents.py <yaml_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    agents_yaml = parse_yaml(file_path)

    try:
        create_agents(agents_yaml)
    except Exception as excep:
        raise RuntimeError("Unable to create agents") from excep






