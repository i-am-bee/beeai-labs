#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import dotenv
from openai import OpenAI
import yaml

dotenv.load_dotenv()


def parse_yaml(file_path):
    with open(file_path, "r") as file:
        yaml_data = list(yaml.safe_load_all(file))
    return yaml_data


def create_agent(agent):
    client = OpenAI(
        base_url=f'{os.getenv("BEE_API")}/v1', api_key=os.getenv("BEE_API_KEY")
    )

    agent_name = agent["metadata"]["name"]
    agent_model = agent["spec"]["model"]
    agent_desc = agent["spec"]["description"]
    agent_instr = agent["spec"]["instructions"]
    agent_tools = []

    # weather_tool = {"type":"object", "properties":{"location":{"anyOf":[{"type":"object","properties":{"name":{"type":"string", "minLength":1 },"country":{"type":"string" },"language":{"type":"string","default":"English" }},"required":["name"],},{"type":"object","properties":{"latitude":{"type":"number"},"longitude":{"type":"number"}},"required":["latitude","longitude"]}]},"start_date":{"type":"string","format":"date","description":"Start date for the weather forecast in the format YYYY-MM-DD (UTC)"},"end_date":{"type":"string","format":"date","description": "End date for the weather forecast in the format YYYY-MM-DD (UTC)" },"temperature_unit":{"type":"string","enum":["celsius","fahrenheit"],"default":"celsius"}},"required":["location","start_date"]}

    for tool in agent["spec"]["tools"]:
        if tool == "code_interpreter":
            agent_tools.append({"type": tool})
        else:
            print(f"Enable the {tool} tool in the Bee UI")

    assistant = client.beta.assistants.create(
        name=agent_name,
        model=agent_model,
        description=agent_desc,
        tools=agent_tools,
        instructions=agent_instr,
    )

    return assistant.id


def create_agents(agents_yaml):
    agent_store = {}
    for agent in agents_yaml:
        agentid = create_agent(agent)
        print(f"🐝 Created agent {agent['metadata']['name']}: {agentid}")
        agent_store[agent["metadata"]["name"]] = agentid

    with open("agent_store.json", "w") as f:
        json.dump(agent_store, f)


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
