> [!WARNING]
> [PRE-Alpha] Please reach out if you want to get involved in the discussions. All feedback is welcomed

# Bee Hive

A multi-agent platform with the vision to facilitate deploy and run Bee agents.

In this initial version you are going to find some examples how run a group of agents, that you can build using current and more mature TypeScript [Bee Agent framework](https://github.com/i-am-bee/bee-agent-framework), or experiment with the new [Python version](../framework/bee-py).

## Usage

There are two steps to running a workflow: defining some agents and creating a workflow to run those agents.

> Note: to run Bee Hive, you will need to [configure your local environment](#local-environment)

### Agent Definition

* You can define your Agent in a declarative way using a YAML file, where you can use the current Bee Agent implementation. With that, you can configure your agent or agents. For example, create an `agents.yaml` file containing the following:

```yaml
apiVersion: beehive/v1alpha1
kind: Agent
metadata:
  name: current-affairs
  labels:
    app: mas-example
spec:
  model: meta-llama/llama-3-1-70b-instruct
  description: Get the current weather
  tools:
    - code_interpreter
    - weather
  instructions: Get the current temperature for the location provided by the user. Return results in Fahrenheit.

---
apiVersion: beehive/v1alpha1
kind: Agent
metadata:
  name: hot-or-not
  labels:
    app: mas-example
spec:
  model: meta-llama/llama-3-1-70b-instruct
  description: Is the current temperature hotter than usual?
  tools:
    - code_interpreter
    - weather
  instructions: The user will give you a temperature in Fahrenheit and a location. Use the OpenMateo weather tool to find the average monthly temperature for the location. Answer if the temperature provided by the user is hotter or colder than the average found by the tool.
```

* Create the agents by running the following command:

```bash
python create_agents.py agents.yaml
```

### Running a Workflow

#### Sequential

* Define a workflow in YAML listing the agents you wish to run. For example, create a `workflow.yaml` file containing the following:

```yaml
apiVersion: beehive/v1alpha1
kind: Workflow
metadata:
  name: beehive-deployment
  labels:
    app: mas-example
spec:
  strategy:
    type: sequence
    output: verbose
  template:
    metadata:
      labels:
        app: mas-example
    agents:
      - name: current-affairs
      - name: hot-or-not
    prompt: New York
```

* Execute the workflow:

```bash
python run_workflow workflow.yaml
```

## Local environment

* Run a local instance of the [Bee Stack](https://github.com/i-am-bee/bee-stack)

* Install dependencies: `poetry shell && poetry install`

* Configure environmental variables: `cp example.env .env`
