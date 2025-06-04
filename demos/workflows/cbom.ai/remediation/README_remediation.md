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
2. Configure (and all tool files to endpoints):

    ```shell
    export MAESTRO_MCP_ENDPOINTS="python3 /absolute/path/to/mcp_server.py --log /tmp/mcp.log /absolute/path/to/java_fetcher.py ..."
    ```

3. Environment:

    ```shell
    export OPENAI_BASE_URL=http://localhost:11434/v1
    export OPENAI_API_KEY="ollama"
    export MAESTRO_MCP_ENDPOINTS="python3 ~/src/mcp-server/mcp_server.py --log /tmp/mcp.log demos/workflows/cbom.ai/java_fetcher.py demos/workflows/cbom.ai/remediation/fetch_code.py demos/workflows/cbom.ai/remediation/tool_fixer.py demos/workflows/cbom.ai/remediation/tool_patcher.py"
    ```

# Optional to see intermediate results

```shell
#export MAESTRO_OPENAI_STREAMING=true
export MAESTRO_OPENAI_STREAMING=false
```

### Running

```shell
maestro run /path/to/agents_remediation.yaml /path/to/workflow_remediation.yaml 2>&1 | tee /tmp/agent.log
```

Logs from the mcp tail can be reviewed from `/tmp/mcp.log` given the example configuration above. This will show tool usage