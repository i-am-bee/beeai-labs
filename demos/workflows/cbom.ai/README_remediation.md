# CBOM-AI

## remediation

1. Conversion of  cbom.ai demo (in this repo) from beeai-remote to openai
2. First pass to port original cbom.ai demo to new environment
    * This currently does not work, and is commented out
    * Specifically step7 in the workflow needs a good CBOM to work with - as such step 6a is added to
      hardcode a working CBOM, as created during the 2024 demo 

### Required setup

Ensure the java tools in this directory are available to the agent

For example:

1. Clone https://github.com/planetf1/mcp-server (assume in ~/src)
2. Configure:
    ```shell
    export MAESTRO_MCP_ENDPOINTS="python3 ~/src/mcp-server/mcp_server.py --log /tmp/mcp.log demos/workflows/cbom.ai/java_fetcher.py demos/workflows/cbom.ai/fetch_code.py demos/workflows/cbom.ai/tool_fixer.py demos/workflows/cbom.ai/tool_patcher.py"
    ```

3. Environment:
    ```
    export OPENAI_BASE_URL=http://localhost:11434/v1
    export OPENAI_API_KEY="ollama"
    export MAESTRO_MCP_ENDPOINTS="python3 ~/src/mcp-server/mcp_server.py --log /tmp/mcp.log demos/workflows/cbom.ai/java_fetcher.py demos/workflows/cbom.ai/fetch_code.py demos/workflows/cbom.ai/tool_fixer.py demos/workflows/cbom.ai/tool_patcher.py"
    ```
# Optional to see intermediate results
#export MAESTRO_OPENAI_STREAMING=true
export MAESTRO_OPENAI_STREAMING=false


### Running

```
maestro run /Users/jonesn/AI/maestro/demos/workflows/cbom.ai/agents_remediation.yaml /Users/jonesn/AI/maestro/demos/workflows/cbom.ai/workflow_remediation.yaml 2>&1 | tee /tmp/agent.log
```

Logs from the mcp tail can be reviewed from `/tmp/mcp.log` given the example configuration above. This will show tool usage