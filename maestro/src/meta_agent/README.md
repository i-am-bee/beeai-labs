# META AGENT

Our goal is to create an agent that can create the relevant agents/workflow.yaml files necessary for you to delegate your tasks.

## Validating/Creating Agents/Workflow files

We can use the maestro commands to validate that our workflows are following the correct schema, and we can actually run them.

Assuming you are in maestro top level:

Validating the YAML file adheres to the schema:
`maestro validate ./schemas/agent_schema.json ./src/meta_agent/agents.yaml`

Creating the agents(with the ability to manually add tools): `maestro create ./src/meta_agent/agents.yaml`

To run the workflow:

If you already created the agents and enabled the tool: `maestro run None ./src/meta_agent/agents.yaml`

OR

Directly run the workflow: `./src/meta_agent/agents.yaml ./src/meta_agent/workflow.yaml`

## Prompt

Prompt Used in Create-Agent-YAML tool:

```Markdown
Build an agents.yaml file using the agent_schema() tool as a reference.

I want two agents, both using the llama3.1 model:

weather_fetcher – Retrieves weather data for a given location using the OpenMeteo tool.
temperature_comparator – Compares the retrieved temperature with historical averages using OpenMeteo.
Ensure both agents are correctly formatted using the schema.
```

### Tools Needed to be Created

agent_schema tool: create by copying the code portion in the agents.yaml file into the tool.