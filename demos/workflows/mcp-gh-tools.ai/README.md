# MCP Walkthrough

This demo shows how to use Maestro agents and connect to/use MCP tools, an extension of listing the avaiable tools as seen in the original [openai-mcp demo](../openai-mcp.ai/README.md).

## Required Exports

```bash
MAESTRO_MCP_ENDPOINTS="/Users/gliu/Desktop/work/github-mcp-server/cmd/github-mcp-server/github-mcp-server"
OPENAI_API_KEY=ollama
OPENAI_BASE_URL="http://localhost:11434/v1" 
GITHUB_PERSONAL_ACCESS_TOKEN=token
```

To download the github-mcp-server locally, follow the process listed in the `README.md` under ["Example Process using go to binaries"](../openai-mcp.ai/README.md)
Currently, we are running `qwen3:8b` model by default, to change simply adjust in [`agents.yaml`](./agents.yaml).

### Streaming

`export MAESTRO_OPENAI_STREAMING=true`

### Running the Workflow

Make sure to enable MCP tools and have exported the github personal access token:
`/file_location/github-mcp-server stdio --toolsets all`

To enable logging:

```bash
github-mcp-server stdio --enable-command-logging --log-file /var/log/github-mcp-server.log
```

To run:
`maestro run demos/workflows/mcp-gh-tools.ai/agents.yaml demos/workflows/mcp-gh-tools.ai/workflow.yaml`
