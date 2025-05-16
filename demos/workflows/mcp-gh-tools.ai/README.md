# MCP Walkthrough

This demo shows how to use Maestro agents and connect to/use MCP tools, an extension of listing the avaiable tools as seen in the original [openai-mcp demo](../openai-mcp.ai/README.md).

## Required Exports

```bash
MAESTRO_MCP_ENDPOINTS="/Users/gliu/Desktop/work/github-mcp-server/cmd/github-mcp-server/github-mcp-server"
OPENAI_API_KEY=ollama
OPENAI_BASE_URL="http://localhost:11434/v1" 
GITHUB_PERSONAL_ACCESS_TOKEN=token
```

Currently, we are running `qwen3` model by default, to change simply adjust in [`agents.yaml`](./agents.yaml). The `llama3.1` model also supports tools.

### Streaming

`export MAESTRO_OPENAI_STREAMING=true`

### Running the Workflow

Make sure to enable MCP tools and have exported the github personal access token:
`/file_location/github-mcp-server stdio --toolsets all`

To run:
`maestro run demos/workflows/mcp-gh-tools.ai/agents.yaml demos/workflows/mcp-gh-tools.ai/workflow.yaml`
