# Maestro Project User Guide

## Table of Contents
1. [Maestro Language](#maestro-language)
2. [Maestro CLI](#maestro-cli)
3. [Maestro UIs](#maestro-uis)
4. [Examples](#examples)
5. [Demos](#demos)

## Maestro Language

Maestro defines agents and workflows in yaml format. 
### Agent
Agent example defined in yaml format is: 
```yaml
apiVersion: maestro/v1alpha1
kind: Agent
metadata:
  name: current-temperature
  labels:
    app: mas-example
spec:
  model: "llama3.1:latest"
  framework: beeai
  mode: remote
  description: Get the current weather
  tools:
    - code_interpreter
    - weather
  instructions: An input is given of a location. Use the OpenMeteo tool to get today's current forecast for the location. Return results in the format - location, temperature in Fahrenheit, and date.
    Example output - New York City, 44.9°F, March 26, 2025
```
The syntax of the agent definition is defined in the [json schema](https://github.com/AI4quantum/maestro/blob/main/schemas/agent_schema.json).

- **apiVersion**: version of agent definition format.  This must be `maestro/v1alpha1` now.
- **kind**: type of object. `Agent` for agent definition
- **metadata**:
  - **name**: name of agent
  - **labels**: array of key, value pairs. This is optional and can be used to associate any information to this agent 
- **spec**:
  - **model**: LLM model name used by the agent  eg. "llama3.1:latest"
  - **framework**: agent framework type.  Current supported agent frameworks are : "beeai", "crewai", "openai", "remotem", "custom" and "code"
  - **mode**: Remote or Local.  Some agents support agent remotely.  Remote is supported by "beeai" and "remote" 
  - **description**: Description of this agent
  - **tools**: array of tool names. This is not implemeted yet.

### Workflow
Workflow example defined in yaml format is:
```yaml
piVersion: maestro/v1alpha1
kind: Workflow
metadata:
  name: maestro-deployment
  labels:
    app: mas-example
spec:
  template:
    metadata:
      labels:
        app: mas-example
    agents:
      - current-temperature
      - hot-or-not
      - cold-activities
      - hot-activities
    prompt: New York City
    steps:
      - name: get-temperature
        agent: current-temperature
      - name: hot-or-not
        agent: hot-or-not
        condition:
        - if: (input.find('hotter') != -1)
          then: hot-activities
          else: cold-activities
      - name: cold-activities
        agent: cold-activities
        condition:
        - default: exit
      - name: hot-activities
        agent: hot-activities
      - name: exit
```
The syntax of the workflow definition is defined in the [json schema](https://github.com/AI4quantum/maestro/blob/main/schemas/workflow_schema.json).

- **apiVersion**: version of agent definition format.  This must be `maestro/v1alpha1` now.
- **kind**: type of object. `Workflow` for workflow definition
- **metadata**:
  - **name**: name of workflow
  - **labels**: array of key, value pairs. This is optional and can be used to associate any information to this workflow 
- **spec**:
  - **template**:
    - **metadata**:
      - **labels**: array of key, value pairs. This is optional and can be used to associate any information to this template
    - **agents**: array of agent names used in this workflow
    - **prompt**: initial prompt for this workflow
    - **event**: definition of event.  Event trigers workflow execution
    - **exception**: definition of exception handling.
    - **steps**: array of steps.  Steps are executed from top to bottom in this list unless the step has `condition` in it. 
      - **name**: name of step
      - **agent**: name of agent for this step

#### Step

The step is an unit of work in the workflow.  It includes execution of agent, execution of agents in parallel or sequential, taking user input, preprocess input of step, post process execution output, deciding the next step to be executed.

The step has properties that define the work of the setp.  Everything is optional except `name` property.

- **name**: name of step definition
- **agent**: name of agent executed in this step
- **inputs**: array source passed to agent as argument
- **context**: array of string or object passed to agent as context
- **input**: definition of user promot and user input processing
- **loop**: definition iterative agent execution
- **condition**: step execution flow control.  The next step is changed according to the agent execution output
- **parallel**: array of agents that are executed in parallel

### event

The event is one way to triger worlflow execution.  Only cron event is suppoorted now.

- **name**: name of event definition
- **cron**: cron job in standard cron format
- **agent**: agent name executed in event processing
- **steps**: step name executed in event processing
- **exit**: cron job exit condition.  Python statement that evaluates the execution output.  True for exit

### exception

The exception is executed when an exception happens during the execution of the workflow.

- **name**: name of exception definition
- **agent**: name of agent executed in exception handling

## Maestro CLI

The Maestro Command Line Interface (CLI) allows users to manage workflows that inlcudes validate, run, deploy and some other commands.

### Basic Commands

- `maestro create` AGENTS_FILE [options]: create agent
- `maestro deploy` AGENTS_FILE WORKFLOW_FILE [options] [ENV...] deploy and run the workflow in docker, kubernetes or Streamit
- `maestro mermaid` WORKFLOW_FILE [options]: generate the mermaid output for the workflow
- `maestro run` WORKFLOW_FILE [options]: run the workflow with existing agents in command window
- `maestro run` AGENTS_FILE WORKFLOW_FILE [options]: create agents and run the workflow in command window
- `maestro validate` YAML_FILE [options]: validate agent or workflow definition yaml file
- `maestro validate` SCHEMA_FILE YAML_FILE [options]: validate agent or workflow definition yaml file using the specified schema file 
- `maestro meta-agents` TEXT_FILE [options]: run ....
- `maestro clean` [options]: clean up Streamit servers of maestro
- `maestro create-cr` YAML_FILE [options]: create maestro custom resource in kubernetes cluster


## Maestro UIs

### Streamlit deploy UI

Maestro initial UI

![Screenshot 2025-06-05 at 11 09 36 AM](https://github.com/user-attachments/assets/7a7cd362-6995-471f-a1b5-ec9c6729c8b4)

Show diagram button shows the worklflow diagram 

![Screenshot 2025-06-05 at 11 13 50 AM](https://github.com/user-attachments/assets/afabaa19-0a9d-4893-b6c6-da958caf6492)

aragnts.yaml and workflow.yaml buttoms show agent and workflow yaml files contents

![Screenshot 2025-06-05 at 11 14 49 AM](https://github.com/user-attachments/assets/82a51bde-3032-4a46-a794-8368e8cfd0ea)

Submit button strarts the workflow with the inputted prompt string

![Screenshot 2025-06-05 at 11 26 06 AM](https://github.com/user-attachments/assets/1acebecf-0add-4ae7-b873-13d4e8992cfd)

### Docker, Kubernates deploy UI

Maestro initial UI

![Screenshot 2025-06-05 at 12 39 01 PM](https://github.com/user-attachments/assets/0053422d-f1be-4cd5-af10-323630e3aa7d)

The workflow name and "Agent definitions" links show or download the workflow and agent yaml files.
The workflow diagram is shown.
The input field for the prompt and the Re-run button starting the workflow at the bottom.

![Screenshot 2025-06-05 at 12 40 30 PM](https://github.com/user-attachments/assets/b87f4a78-6218-4a85-a1b8-de01a9f0da1e)

The workflow output come out after the inpiut of the prompt string and pressing of the Re-run button

### maestro run output

The `maestro run` command outout comes out in the command window.
![Screenshot 2025-06-05 at 1 07 28 PM](https://github.com/user-attachments/assets/f9b9f90c-6e9a-4c8d-b9fc-6b178355644d)

## Examples

### [Weather Checker AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/weather-checker.ai/README.md): Simple Sequential Workflow
The weather checker ai is a simple sequential workflow.  I have 2 agents Temperatire agent that retrieve the current temperature of the given location and hot-or-not Agent that retrive the historical temperature of the given location and returns whether the current temperature is hotter or colder.

#### agent.yaml
```yaml
apiVersion: maestro/v1alpha1
kind: Agent
metadata:
  name: Temperature Agent
  labels:
    app: mas-example
spec:
  model: "llama3.1:latest"
  framework: beeai
  mode: remote
  description: Get the current weather
  tools:
    - code_interpreter
    - weather
  instructions: An input is given of a location.  Use the OpenMeteo tool to get today's current forecast for the location. Return results in the format -location, temperature in Fahrenheit, and date.
---
apiVersion: maestro/v1alpha1
kind: Agent
metadata:
  name: hot-or-not Agent
  labels:
    app: mas-example
spec:
  model: "llama3.1:latest"
  framework: beeai
  mode: remote
  description: Is the current temperature hotter than usual?
  tools:
    - code_interpreter
    - weather
  instructions: |
    Use the OpenMeteo weather tool to find the historical temperature of the given location.  Return whether the current temperature is hotter or colder.

    Example Process:
    Input: New York, 50 degrees F

    Compare input against historical temperature (lets say 55) in input location.

    Output: The current temperature is colder than the historical temperature.
```

#### workflow.yaml
```yaml
apiVersion: maestro/v1alpha1
kind: Workflow
metadata:
  name: Weather Checker AI
  labels:
    app: mas-example
spec:
  template:
    metadata:
      labels:
        app: mas-example
    agents:
      - Temperature Agent
      - hot-or-not Agent
    prompt: New York City
    steps:
      - name: get_temperature
        agent: Temperature Agent
      - name: compare_temperature
        agent: hot-or-not Agent
```

## Demos

Some demo workflows are available. For setting up the demo environment refer to [README.md](https://github.com/AI4quantum/maestro/blob/main/demos/README.md)
### Demos with workflow

- [Activity Planner AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/activity-planner.ai/README.md)
- [CBOM AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/cbom.ai/README.md)
- [IBM Summary AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/ibm-summary.ai/README.md)
- [Summary AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/summary.ai/README.md)
- [Weather Checker AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/weather-checker.ai/README.md)

## Demos with agent / tool integration

- [Activity Planner CrewAI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/activity-planner-crewai.ai/README.md)
- [MCP GH Tools AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/mcp-gh-tools.ai/README.md)
- [OpenAI MCP AI](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/mcp-gh-tools.ai/README.md)

## Demo Meta Agent
- [Meta Agents](https://github.com/AI4quantum/maestro/blob/main/demos/workflows/meta-agents/README.md)
