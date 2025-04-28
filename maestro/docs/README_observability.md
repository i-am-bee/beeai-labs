# Maestro Agent Observability with Langfuse

This document describes the optional observability integration using [Langfuse](https://langfuse.com/) for Maestro agents.

**Important Note:** Currently, this Langfuse integration is only implemented and functional for agents using the `openai` framework (`framework: openai` in the agent YAML) via the implementation in `src/agents/openai_agent.py`. Other agent frameworks within Maestro are not yet instrumented for Langfuse tracing.

## Overview

This integration leverages the Logfire library to automatically capture and send detailed execution traces to your Langfuse instance. If enabled, traces including LLM calls, tool usage (both built-in and MCP), and overall agent execution flow will be available for analysis and debugging in Langfuse.

The integration is designed to be **optional**. If the required configuration is not provided, the agent will run normally without attempting to send any data to Langfuse.

## Configuration

To enable Langfuse tracing, set the following environment variables **before** running the `maestro` command:

1.  **`LANGFUSE_PUBLIC_KEY`**: Your Langfuse project's Public Key. This typically starts with `pk-lf...`.
2.  **`LANGFUSE_SECRET_KEY`**: Your Langfuse project's Secret Key. This typically starts with `sk-lf...`.
3.  **`LANGFUSE_HOST`**: The base URL of your Langfuse instance.
    *   For Langfuse Cloud (US): `https://cloud.langfuse.com`
    *   For Langfuse Cloud (EU): `https://eu.cloud.langfuse.com`
    *   For self-hosted instances: Your instance's URL (e.g., `http://localhost:3000`).

**Example:**

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"

# Now run your maestro command
maestro run agents.yaml workflow.yaml
```
