# OpenAI MCP Demo

This demo shows how to use Maestro to create OpenAI based agents
that make use of MCP tools

A small model is used to facilitate automated testing. This may not be the best for high quality results and derivations of this demo. See the `spec.model` setting in [agents.yaml](agents.yaml)

## Dependencies

This demo requires some MCP tools to be configured (it only lists tools, so it doesn't matter
what the tools do).

The automated test makes use of [GitHub mcp server](https://github.com/github/github-mcp-server).

Download the latest release, and use the path to the `github-mcp-server` in the environment settings below.

The `GITHUB_PERSONAL_ACCESS_TOKEN` is needed for derivations of this demo which may do real github work. For the purpose of automated testing this is set to a dummy value.

All commands below are relative to the `maestro` subdirectory of the repository.

## Standalone execution

```shell
export GITHUB_PERSONAL_ACCESS_TOKEN=<github-token>
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL="http://localhost:11434/v1" 
export MAESTRO_MCP_ENDPOINTS="/Users/jonesn/bin/github-mcp-server stdio"
maestro run demos/workflows/openai-mcp.ai/agents.yaml demos/workflows/openai-mcp.ai/workflow.yaml
```

## Automated execution

This demo is run from the overall test framework:

* ../.github/workflows/maestro_demo-tests.yaml : This defines the overall trigger and sets up a basic environment including the latest Ollama release
* [run-demos.sh](../../../tests/run-demos.sh) : Overall framework. By default only runs a *dry-run*, but if a `.run` file is found in the test directory (ie here for this demo) it will execute a normal run.
* The [test.sh](test.sh) will
  * download the required ollama model (taken from [agents.yaml](agents.yaml))
  * Download the [GitHub mcp server](https://github.com/github/github-mcp-server)
  * Set appropriate environment
  * Run the standard [test.sh](../common/test.sh)
  * Parse the overall output from the script looking for specific strings that indicate success

On a default github runner this test takes around 2 minutes.
