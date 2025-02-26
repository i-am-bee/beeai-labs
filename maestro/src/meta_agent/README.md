# META AGENT

Our goal is to create an agent that can create the relevant agents/workflow.yaml files necessary for you to delegate your tasks.

## Validating/Creating Agents/Workflow files

We can use the maestro commands to validate that our workflows are following the correct schema, and we can actually run them.

Assuming you are in maestro top level:

Validating the YAML file adheres to the schema:
`maestro validate ./schemas/agent_schema.json ./src/meta_agent/agents.yaml`

Creating the agents(with the ability to manually add tools): `maestro create ./src/meta_agent/agents.yaml`

To run the workflow:

If you already created the agents and enabled the tool: `maestro run None ./src/meta_agent/workflow.yaml`

OR

Directly run the workflow: `./src/meta_agent/agents.yaml ./src/meta_agent/workflow.yaml`

## Prompts

Prompt Used in Create-Agent-YAML agent:

```Markdown
Build an agents.yaml file using the agent_schema tool as a reference.

I want two agents, both using the llama3.1 model:

weather_fetcher – Retrieves weather data for a given location using the OpenMeteo tool.
temperature_comparator – Compares the retrieved temperature with historical averages using OpenMeteo.
Ensure both agents are correctly formatted using the schema.
```

Prompt Used in Create-Workflow-YAML agent:

```Markdown
Build a structured workflow using the workflow_schema tool as a reference.

I have two agents in agents.yaml:
weather_fetcher – Retrieves weather data for a given location using the OpenMeteo tool.
temperature_comparator – Compares the retrieved temperature with historical averages using OpenMeteo.

Requirements:

Ensure the workflow follows the workflow.schema.json format.
Each step must:
Reference a valid agent from agents.yaml.
Have a name that describes its function.
The final output should be a valid structured workflow in YAML format, please make it easily readble in a code block
```

### Tools Needed to be Created

agent_schema tool: create by copying the code portion in the agents.yaml file into the tool.
workflow_schema tool: create by copying the code portion in the agents.yaml file into the tool.