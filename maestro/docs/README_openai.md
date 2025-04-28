# Maestro OpenAI Agent Integration

This document describes how to use Maestro's `openai` agent framework, which leverages the official OpenAI Python SDK (or compatible libraries for other endpoints, specifically the `agents-mcp` library) to integrate Large Language Models (LLMs) into your workflows.

This integration supports:

*   Connecting to the official OpenAI API.
*   Connecting to any OpenAI-compatible API endpoint (e.g., Ollama, local vLLM instances).
*   Utilizing built-in tools provided by the underlying `agents` library (currently `web_search`).
*   Connecting to external tools via Model Context Protocol(MCP) servers, supporting both:
    *   Remote servers using Server-Sent Events (SSE).
    *   Local servers launched as subprocesses using Standard I/O (Stdio).

## Prerequisites

1.  **Maestro:** Ensure you have Maestro installed and configured as per [README.md](../README.md).
2. Have access to an OpenAI API key, or access to a compatible API endpoint (including Ollama)


## Configuration

In addition to regular maestro yaml, the following environment variables are needed:

  *   For **OpenAI API:** Set the `OPENAI_API_KEY` environment variable.
  *   For **Custom Endpoints (like Ollama):** Ensure the endpoint is running and accessible. You will need to set `OPENAI_BASE_URL`.
  *   For **MCP Servers:** Ensure the servers are running (for remote SSE) or the binaries are accessible (for local Stdio). Set `MAESTRO_MCP_ENDPOINTS`.
  *   **Streaming Override (Optional):** Set `MAESTRO_OPENAI_STREAMING` to control streaming behavior.
      *   `true`: Forces streaming mode, even if `run()` is called.
      *   `false`: Forces non-streaming mode, even if `run_streaming()` is called.
      *   `auto` (or unset): Uses the called method (`run()` for non-streaming, `run_streaming()` for streaming). This is primarily for development/debugging.


Observability can be added using LangFuse. See [README_observability.md](../README_observability.md) for more details.

### Basic Agent Definition

Define an agent with `spec.framework: openai` and `spec.mode: local` in your agent YAML file. The `spec.model: gpt-4o-mini` specifies which LLM to use.

```yaml
# Example: tests/agents/openai_agent/agents.yaml
apiVersion: maestro/v1alpha1
kind: Agent
metadata:
  name: openai_test_mcp
  labels:
    app: testapp_mcp
spec:
  model: "gpt-4o-mini" # Specify the model to use
  description: test
  instructions: You are a helpful agent. Respond to the users question, making use of any required tools
  framework: openai
  mode: local # 'local' mode uses this Maestro agent implementation
```

It is important to set the `OPENAI_API_KEY` environment variable - see [OpenAI's website](https://platform.openai.com/account/api-keys).

This will connect to OpenUI using the [new Responses API](https://platform.openai.com/docs/guides/responses-vs-chat-completions) at `https://api.openai.com/v1`

The full example can be run with:
```bash
maestro run tests/agents/openai_agent/agents.yaml test/agents/openai_agent/workflow.yaml
```
### Using Built-in Tools (web_search)

The agents library provides some built-in tools. Currently, the Maestro openai agent only supports web_search.

Add the tool name in to `spec.tools` in the agent YAML:

```yaml
apiVersion: maestro/v1alpha1
kind: Agent
metadata:
  name: openai_test_search
  labels:
    app: testapp_search
spec:
  model: "gpt-4o-mini"
  description: test
  instructions: You are a helpful agent. Respond to the users question, making use of any required tools
  framework: openai
  mode: local
  tools:
    - web_search
```

The web_search tool requires the OpenAI "Responses API", which is  available when using the default OpenAI endpoint (https://api.openai.com/v1).

The full example can be run with:
```
maestro run tests/agents/openai_agent/agents_search.yaml test/agents/openai_agent/workflow_search.yaml
```

### Connecting to Custom OpenAI-Compatible Endpoints (e.g., Ollama)

In addition to the above, set the `OPENAI_BASE_URL` environment variable to point to your endpoint's V1 API compatibility layer for example `export OPENAI_BASE_URL="http://localhost:11434/v1"`. 

Setting this also forces the use of the older chat_completions API internally within the agents library. This will mean the built in tools cannot be used.

An example that assumes Ollama with the `granite3.3:8b model available` can be run with:
```
maestro run tests/agents/openai_agent/agents_search.yaml test/agents/openai_agent/workflow_search.yaml
```

### Using MCP Tools

Configure external tools provided by MCP servers using the `MAESTRO_MCP_ENDPOINTS` environment variable.

This variable takes a comma-separated list of server definitions.

Both remote (SSE) and local (Stdio) servers can be freely mixed.

Tools do not need to be listed in the yaml, and all provided by the servers will be available to the agent.

#### Remote (SSE) Servers:

* Defined by a URL starting with `http://` or `https://`.
* The URL should point to the server's Server-Sent Events endpoint.
* Example: `http://my-remote-mcp.example.com:8000/sse`

#### Local (Stdio) Servers:

* Defined by a command string that launches the MCP server process locally.
* The string is parsed using shell-like rules (shlex), so commands with spaces or arguments should work correctly.
* The first part is the command/binary path, subsequent parts are arguments passed to the command.
* The local server process inherits the environment variables of the Maestro process.
* Example: `/Users/jonesn/bin/github-mcp-server stdio --verbose`

#### Example environment

Servers of both types can be mixed:
```
export MAESTRO_MCP_ENDPOINTS="http://localhost:8000/sse,/Users/jonesn/bin/github-mcp-server stdio,https://another-mcp.com/events"
```

The agent will attempt to connect to all defined servers. The tools from all successfully connected servers will be made available to the LLM during its run.

#### Provided Example for MCP

The following MCP servers are used in the example variable setting above:

* The [official github MCP server](https://github.com/github/github-mcp-server)
  * Download the binary (in go) and ensure it is pointed to by the path to `github-mcp-server` in the example above. This has a number of tools to support github activities. Note that this tool also requires that `GITHUB_PERSONAL_ACCESS_TOKEN` is set.
* A [test remote MCP server](https://github.com/planetf1/mcp-server)
  * Clone the project, and follow the launch instructions in the README. If running on the same machine the URL in the variable should be correct. This has a variety of tools but is provided only to demonstrate mcp capability. Do not rely on the tool implementations.

For *OpenAI*
```
maestro run tests/agents/openai_agent/agents_mcp.yaml test/agents/openai_agent/workflow_mcp.yaml
```
or with *Ollama*
```
maestro run tests/agents/openai_agent/agents_ollama_mcp.yaml test/agents/openai_agent/workflow_ollama_mcp.yaml
```

