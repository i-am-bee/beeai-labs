#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0

# Exit immediately on any error
set -euo pipefail

# Script is designed to be called instead of common test.sh, so will take these args and pass on
if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <path_to_test_script> <demo_name>" >&2
    exit 1
fi
TARGET_TEST_SCRIPT="$1"
DEMO_NAME="$2"

# sets source directory (where this script is)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
AGENT_YAML_PATH="${SCRIPT_DIR}/agents.yaml"

# Version of https://github.com/github/github-mcp-server
GITHUB_MCP_VERSION="v0.2.1"

# Pick model from agent definition to avoid duplication. Must be available on Ollama
if [[ ! -f "${AGENT_YAML_PATH}" ]]; then
    echo "Error: Agent definition file not found at ${AGENT_YAML_PATH}" >&2; exit 1;
fi

# Required, or gh mcp server fails to initialize & hangs -- but we won't need it.
export GITHUB_PERSONAL_ACCESS_TOKEN="dummy"

# Determine the file to download for the gh mcp server
OS_NAME="$(uname -s)"
ARCH_NAME="$(uname -m)"
MCP_ARCH_STR="${OS_NAME}_${ARCH_NAME}"
MCP_FILENAME="github-mcp-server_${MCP_ARCH_STR}.tar.gz"
MCP_URL="https://github.com/github/github-mcp-server/releases/download/${GITHUB_MCP_VERSION}/${MCP_FILENAME}"
MCP_INSTALL_DIR_NAME="github-mcp-server"

# LLM backend
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama"

MCPTMP=$(mktemp -d -t github-mcp-XXXXXX) # Assigned after trap is set
echo "Created temporary directory for MCP server: ${MCPTMP}"

# Get model from yaml and retrieve
echo "Extracting model name from ${AGENT_YAML_PATH}..."
OLLAMA_MODEL=$(grep '^\s*model:' "${AGENT_YAML_PATH}" | sed -E 's/^\s*model:\s*"?([^"]+)"?\s*$/\1/')
if [[ -z "${OLLAMA_MODEL}" ]]; then echo "Error: Could not extract model name from ${AGENT_YAML_PATH}" >&2; exit 1; fi
echo "Pulling Ollama model: ${OLLAMA_MODEL}..."
if ! ollama pull "${OLLAMA_MODEL}"; then
    echo "Error: Failed to pull Ollama model '${OLLAMA_MODEL}'" >&2
    exit 1
fi
echo "Ollama model pulled successfully."

# Install the MCP server (avoid updating github repo tree)
( 
    echo "Entering temporary directory: ${MCPTMP}"
    cd "${MCPTMP}" || exit 1

    echo "Downloading MCP server from ${MCP_URL}..."
    if ! curl -fsSL -o "${MCP_FILENAME}" "${MCP_URL}"; then
        echo "Error: Failed to download MCP server from ${MCP_URL}" >&2
        exit 1
    fi
    echo "Download complete."

    echo "Extracting MCP server..."
    if ! tar -xzf "${MCP_FILENAME}"; then
        echo "Error: Failed to extract ${MCP_FILENAME}" >&2
        exit 1 # Exit handled by set -e
    fi
    echo "Extraction complete."
)
MCPSERVER_PATH="${MCPTMP}/${MCP_INSTALL_DIR_NAME}"

# Set the environment variable for Maestro (or the test runner) to find the MCP server
export MAESTRO_MCP_ENDPOINTS="${MCPSERVER_PATH} stdio"
echo "MAESTRO_MCP_ENDPOINTS set to: ${MAESTRO_MCP_ENDPOINTS}"

# Verify the server binary exists and is executable after extraction then run
if [[ ! -x "${MCPSERVER_PATH}" ]]; then
    echo "Error: MCP server binary not found or not executable at ${MCPSERVER_PATH}" >&2
    exit 1
fi
echo "MCP server ready at ${MCPSERVER_PATH}"

# TODO: Setup langfuse for observability (if applicable)

echo "Pre-test setup complete."
echo "----------------------------------------"

echo "Running standard test script: ${TARGET_TEST_SCRIPT} with demo name: ${DEMO_NAME}"

if [[ ! -x "${TARGET_TEST_SCRIPT}" ]]; then
    echo "Error: Target test script at ${TARGET_TEST_SCRIPT} is not available." >&2
    exit 1
fi

echo "Executing: ${TARGET_TEST_SCRIPT} ${DEMO_NAME}"
TEST_OUTPUT=$("${TARGET_TEST_SCRIPT}" "${DEMO_NAME}" 2>&1) || true
TEST_EXIT_CODE=$?

echo "--- Test Script Output ---"
echo "${TEST_OUTPUT}"
echo "--- End Test Script Output ---"
echo "Test script finished with exit code: ${TEST_EXIT_CODE}"

# TODO: Validation could be improved - simple grep check initially
if ! echo "${TEST_OUTPUT}" | grep -q 'Tools found'; then
    echo "Error: Validation failed. Output did not contain 'Tools found'." >&2
    exit 1
fi
if ! echo "${TEST_OUTPUT}" | grep -q 'Successfully connected to 1 MCP server(s)'; then
    echo "Error: Validation failed. Output did not contain 'Successfully connected to 1 MCP server(s)'." >&2
    exit 1
fi

echo "Basic validation passed."

# Exit with the exit code of the test script if validation passed
exit ${TEST_EXIT_CODE}

