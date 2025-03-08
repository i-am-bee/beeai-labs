# META AGENT

This is the meta-agent demo for creating an `agent.yaml` file given a natural language prompt/scenario.

## Validating/Creating Agents/Workflow files

We can use the maestro commands to validate that our workflows are following the correct schema, and we can actually run them.

Assuming you are in maestro top level:

Validating the YAML file adheres to the schema:
`maestro validate ./schemas/agent_schema.json ./demos/workflows/meta-agents-weather.ai/agents.yaml`

Creating the agents(with the ability to manually add tools): `maestro create ./demos/workflows/meta-agents-weather.ai/agents.yaml`

If you already created the agents and enabled the tool: `maestro run None ./demos/workflows/meta-agents-weather.ai/workflow.yaml`

OR

Directly run the workflow: `./demos/workflows/meta-agents-weather.ai/agents.yaml ./demos/workflows/meta-agents-weather.ai/workflow.yaml`

### Tools Needed to be Created

agent_schema tool: create by copying the code portion in the agents.yaml file into the tool.