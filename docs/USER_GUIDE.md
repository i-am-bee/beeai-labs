# Maestro Project User Guide

## Table of Contents
1. [Maestro Language](#maestro-language)
2. [Maestro CLI](#maestro-cli)
3. [Maestro UIs](#maestro-uis)
4. [Simple Examples](#simple-examples)
5. [Demos](#demos)
6. [FAQs](#faqs)

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

- **apiVersion**: Version of agent definition format.  This must be `maestro/v1alpha1` now.
- **kind**: Type of object. `Agent` for agent definition
- **metadata**:
  - **name**: Name of agent
  - **labels**: list of key, value pairs. This is optional and can be used to associate any information to this agent 
- **spec**:
  - **model**: LLM model name used by the agent  eg. "llama3.1:latest"
  - **framework**: Agent framework type.  Current supported agent frameworks are : "beeai", "crewai", "openai", "remotem", "custom" and "code"
  - **mode**: Remote or Local.  Some agents support agent remotely.  Remote is supported by "beeai" and "remote" 
  - **description**: Description of this agent
  - **tools**: list of tool names. This is not implemeted yet.

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
### Agent
The syntax of the agent definition is defined in the [json schema](https://github.com/AI4quantum/maestro/blob/main/schemas/agent_schema.json).

**apiVersion**: version of the format. This must be `maestro/v1alpha1` now.

**kind**: Agent

**metadata**:

  name: current-temperature
  labels:
    app: mas-example
    
**spec**:

  model: "llama3.1:latest"
  framework: beeai
  mode: remote
  description: Get the current weather
  tools:
    - code_interpreter
    - weather
  instructions: An input is given of a location. Use the OpenMeteo tool to get today's current forecast for the location. Return results in the format - location, temperature in Fahrenheit, and date.
    Example output - New York City, 44.9°F, March 26, 2025
### Workflow
The syntax of the workflow definition is defined in the [json schema](https://github.com/AI4quantum/maestro/blob/main/schemas/workflow_schema.json).
language designed for creating and managing complex workflows. It consists of two main components:

- **Agents**: Agents are the building blocks of Maestro workflows. They represent entities that perform tasks, such as processing data, sending notifications, or invoking external services.

- **Workflow**: A workflow is a directed acyclic graph (DAG) of agents, defining the sequence and dependencies of tasks.


## Maestro CLI

The Maestro Command Line Interface (CLI) allows users to define, execute, and manage workflows.

### Basic Commands

- `maestro init`: Initialize a new Maestro project.
- `maestro build`: Compile the Maestro workflow into an executable format.
- `maestro run`: Execute the compiled workflow.
- `maestro help`: Display help information for Maestro CLI commands.

## Maestro UIs

Maestro provides two user interfaces for visualizing and managing workflows:

- **Maestro Web UI**: A web-based interface for designing, executing, and monitoring workflows.
- **Maestro Visual Studio Code Extension**: An extension for Visual Studio Code, enabling Maestro workflow development within the code editor.

## Simple Examples

### Example 1: Simple Sequential Workflow

```maestro
 
agent A {
  task t1 {
    // Task 1 logic
  }
}

agent B {
  task t2 {
    // Task 2 logic
  }
}

workflow w1 {
  A -> B
}
