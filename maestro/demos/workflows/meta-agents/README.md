# Meta agent test

This folder holds the generated `agents.yaml` and `workflow.yaml` files for the meta agent demos.

Validate the agent file: `maestro validate ./schemas/agent_schema.json ./demos/workflows/meta-agents/DEMO_NAME/FOLDER_NAME/agents.yaml`

Creating the agents(with the ability to manually add tools): `maestro create ./demos/workflows/meta-agents/DEMO_NAME/FOLDER_NAME/agents.yaml`

If you already created the agents and enabled the tool: `maestro run None ./demos/workflows/meta-agents/DEMO_NAME/FOLDER_NAME/workflow.yaml`

## Tools Needed to be Created

agent_schema tool: create by copying the code portion in the agents.yaml file into the tool. This is inside `./weather/agent` and `./weather/workflow`
