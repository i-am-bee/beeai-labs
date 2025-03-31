# Contributing to Maestro Demos

Thank you for your interest in contributing to **Maestro**! This document outlines the structure and workflow for setting up and testing demos using **Maestro**.

---

## Project Structure

```markdown
/maestro
│── /src                    # Source code for core functionalities
│   │── /schemas            # JSON schema definitions for agents and workflows
│       │── agent_schema.json
│       │── workflow_schema.json
│── /demos                  # Demo-specific workflows and agents
│   │── /workflows          
│       │── agents.yaml     # YAML file defining the agents used in the demo
│       │── workflow.yaml         
│── .env                    # Environment variables (use `example.env` as reference)
│── README.md               # Project documentation
│── CONTRIBUTING.md         # Contribution guidelines
```

---

## Setting Up Your Environment

### 1. Clone the Repository

```bash
git clone https://github.com/i-am-bee/bee-hive.git
cd bee-hive
```

### 2. Set Up the Virtual Environment

```bash
poetry env use python3
poetry install
poetry shell
```

### 3. Configure Environment Variables

- Copy `example.env` and rename it to `.env`:

  ```bash
  cp example.env .env
  ```

---

## Validating and Running Demos with Maestro

### Validate Workflow and Agent YAML Files

Note: All these commands assume you are running from maestro top-level directory.

Ensure that your YAML definitions adhere to the correct schema before running them.

```bash
maestro validate ./schemas/agent_schema.json ./src/agents/meta_agent/agents.yaml
```

### Create Agents

To create agents (with the ability to manually add tools):

```bash
maestro create ./src/agents/meta_agent/agents.yaml
```

### Run the Workflow

If you have already created the agents and enabled the tools:

```bash
maestro run None ./src/agents/meta_agent/workflow.yaml
```

OR create the agents and run workflow in the same step:

```bash
maestro run ./src/agents/meta_agent/agents.yaml ./src/agents/meta_agent/workflow.yaml
```

---

## Creating a New Demo

### 1. Define Agents

- Create a YAML file in `/demos/agents.yaml` to define agents.
- Follow the `agent_schema.json` structure.

#### Example `agents.yaml`

```yaml
apiVersion: maestro/v1alpha1
kind: Agent
metadata:
  name: search_arxiv
spec:
  model: llama3.1
  description: "Searches for relevant ArXiv papers."
  instructions: "Given a topic, fetch relevant papers."
```

### 2. Define the Workflow

- Create a YAML file in `/demos/workflow.yaml`.
- Ensure it follows `workflow_schema.json`.

#### Example `workflow.yaml`

```yaml
apiVersion: maestro/v1alpha1
kind: Workflow
metadata:
  name: arxiv_search_demo
spec:
  strategy:
    type: sequence
  steps:
    - name: search_arxiv
      agent: search_arxiv
    - name: filter_papers
      agent: selector_agent
    - name: summarize
      agent: summary_agent
```

### 3. Document the Demo

- Add a `README.md` inside the `/demos` folder.
- Include:
  - Overview of the demo
  - Installation/setup steps
  - Example command to run the demo

---

## Testing and Debugging

### Debugging Tips

- Ensure all dependencies are installed (`poetry install`).
- Check for missing agents (`agent_store.json` must contain registered agents).
- Validate YAML schemas using `maestro validate` before running workflows.

---

## Code Style and Best Practices

- Use **docstrings** for all functions and classes.
- Write **meaningful commit messages**:

  ```bash
  git commit -m "Add new ArXiv search agent"
  ```

- Ensure workflows are **modular and reusable**.

---

## Submitting a Pull Request

1. **Fork the repository** and create a new branch:

   ```bash
   git checkout -b feature-new-demo
   ```
  
2. **Make your changes and commit**.
3. **Push to your fork** and create a Pull Request.

---

By following these guidelines, we ensure that all demos are consistent, well-documented, and easy to run using **Maestro**.
