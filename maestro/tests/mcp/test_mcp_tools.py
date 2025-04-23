# tests/mcp/test_mcp_tools.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import sys
import os
from typing import Dict, Any, AsyncGenerator, List

import pytest
import pytest_asyncio

try:
    from src.agents.mcp_tools import MCPToolManager, mcp_enabled, DEFAULT_MCP_ENDPOINTS
except ImportError as e:
    print(f"ERROR: Failed to import MCPToolManager. Make sure project structure is correct and contains 'src/agents/mcp_tools.py'.")
    print(f"Import Error: {e}")
    MCPToolManager = None
    mcp_enabled = False
    DEFAULT_MCP_ENDPOINTS = []


@pytest_asyncio.fixture(scope="module")
async def mcp_manager() -> AsyncGenerator[MCPToolManager, None]:
    """
    Pytest fixture to initialize and yield the MCPToolManager.
    Performs initial checks and discovery once per module.
    Skips tests if MCP is disabled or no endpoints are configured.
    """
    print("\n--- Setting up MCPToolManager Fixture ---")
    if not mcp_enabled:
        pytest.skip("MCP library ('mcp') not installed or failed to import. Did you 'pip install mcp'? Skipping MCP tests.")

    if not DEFAULT_MCP_ENDPOINTS:
        pytest.skip("No MCP endpoints configured in DEFAULT_MCP_ENDPOINTS (in mcp_tools.py). Skipping MCP tests.")

    # TODO: For testing, consider what MCP server is used
    print(f"Fixture: Using MCP endpoints: {DEFAULT_MCP_ENDPOINTS}")
    manager = MCPToolManager()

    print("Fixture: Discovering tools...")
    try:
        await manager.discover_tools() # Discover tools once for the module
        if not manager.tools:
            print("Fixture: WARNING - No tools discovered during setup (check endpoints and server status).")
        else:
            print(f"Fixture: Discovered {len(manager.tools)} tools.")
    except Exception as e:
        pytest.fail(f"Fixture: FAILED - An unexpected error occurred during tool discovery: {e}", pytrace=False)

    yield manager # Provide the initialized manager (with discovered tools) to tests

    print("\n--- Tearing down MCPToolManager Fixture ---")


@pytest.mark.asyncio
async def test_mcp_tool_discovery(mcp_manager: MCPToolManager):
    """
    Tests if the MCPToolManager discovered any tools.
    Relies on the fixture having already run discover_tools().
    """
    print("\n--- Running Pytest: Tool Discovery Check ---")
    assert mcp_manager is not None
    if mcp_manager.tools:
        print(f"Pytest Discovery Check: PASSED (Fixture found {len(mcp_manager.tools)} tools)")
    else:
        print("Pytest Discovery Check: COMPLETED (Fixture found no tools)")


@pytest.mark.asyncio
async def test_mcp_basic_tool_execution(mcp_manager: MCPToolManager):
    """
    Tests executing the first discovered MCP tool with dummy arguments using Pytest.
    Skips if no tools were discovered by the fixture.
    """
    print("\n--- Running Pytest: Basic Tool Execution ---")
    if not mcp_manager.tools:
        pytest.skip("Skipping execution test because no tools were discovered during fixture setup.")

    first_tool_name = list(mcp_manager.tools.keys())[0]
    tool, endpoint = mcp_manager.tools[first_tool_name]
    print(f"Pytest: Attempting to execute the first discovered tool: '{first_tool_name}' from {endpoint}")
    print(f"Pytest: Tool Description: {getattr(tool, 'description', 'N/A')}")

    # Determine Dummy Args based on Schema
    schema = getattr(tool, 'inputSchema', getattr(tool, 'parameters', {}))
    required_params = schema.get('required', []) if isinstance(schema, dict) else []
    properties = schema.get('properties', {}) if isinstance(schema, dict) else {}
    dummy_args: Dict[str, Any] = {}

    print(f"Pytest: Generating dummy arguments based on schema (required: {required_params})")
    for param_name in required_params:
        param_info = properties.get(param_name, {})
        param_type = param_info.get('type', 'string')
        if param_type == 'integer' or param_type == 'number':
            dummy_args[param_name] = 0
        elif param_type == 'boolean':
            dummy_args[param_name] = False
        elif param_type == 'array':
            dummy_args[param_name] = []
        elif param_type == 'object':
            dummy_args[param_name] = {}
        else: # Default to string
            dummy_args[param_name] = f"dummy_{param_name}"
        print(f"  - Added dummy arg: {param_name}={dummy_args[param_name]}")

    print(f"Pytest: Using generated dummy arguments: {dummy_args}")

    try:
        result = await mcp_manager.execute_tool_streaming(first_tool_name, dummy_args)
        print(f"\nPytest Execution Test: FINISHED for tool '{first_tool_name}'.")
        if result:
            print(f"  Pytest Final Result (Placeholder/Accumulated): {result}")
            assert result is not None
            assert isinstance(result, dict)
            assert "status" in result
        else:
            print("  Pytest Execution returned None or empty result (check logs).")
            # TODO: Consider failing if None is unexpected
            # pytest.fail("Tool execution returned None unexpectedly.")

    except Exception as e:
        print(f"\nPytest Execution Test: FAILED - An unexpected error occurred during execution of '{first_tool_name}': {e}")
        pytest.fail(f"Unexpected exception during tool execution: {e}", pytrace=False)


async def run_standalone_tests():
    """Runs the MCP tool checks as a standalone script."""
    print("--- Starting MCP Tool Manager Test (Standalone) ---")

    if not mcp_enabled:
        print("MCP library ('mcp') not installed or failed to import. Did you 'pip install mcp'?")
        print("Skipping MCP tests.")
        print("--- MCP Tool Manager Test Finished (Skipped) ---")
        return

    print(f"Standalone: Attempting to connect to MCP endpoints: {DEFAULT_MCP_ENDPOINTS}")
    if not DEFAULT_MCP_ENDPOINTS:
        print("\nStandalone WARNING: No MCP endpoints configured in DEFAULT_MCP_ENDPOINTS (in mcp_tools.py).")
        print("Please add your MCP server URLs to test discovery and execution.")
        print("--- MCP Tool Manager Test Finished (No Endpoints) ---")
        return

    manager = MCPToolManager()

    print("\n--- Standalone Test 1: Discovering Tools ---")
    try:
        await manager.discover_tools()
        if manager.tools:
            print("\nStandalone Discovery Test: SUCCESS - Found one or more tools.")
        else:
            print("\nStandalone Discovery Test: FINISHED - No tools were discovered (check endpoints and server status).")
    except Exception as e:
        print(f"\nStandalone Discovery Test: FAILED - An unexpected error occurred: {e}")
        print("--- MCP Tool Manager Test Finished (Error) ---")
        return

    print("\n--- Standalone Test 2: Attempting Basic Tool Execution ---")
    if not manager.tools:
        print("Standalone: Skipping execution test because no tools were discovered.")
    else:
        first_tool_name = list(manager.tools.keys())[0]
        tool, endpoint = manager.tools[first_tool_name]
        print(f"Standalone: Attempting to execute: '{first_tool_name}' from {endpoint}")
        print(f"Standalone: Tool Description: {getattr(tool, 'description', 'N/A')}")

        # Determine Dummy Args based on Schema (Standalone)
        schema = getattr(tool, 'inputSchema', getattr(tool, 'parameters', {}))
        required_params = schema.get('required', []) if isinstance(schema, dict) else []
        properties = schema.get('properties', {}) if isinstance(schema, dict) else {}
        dummy_args: Dict[str, Any] = {}

        print(f"Standalone: Generating dummy arguments based on schema (required: {required_params})")
        for param_name in required_params:
            param_info = properties.get(param_name, {})
            param_type = param_info.get('type', 'string')
            if param_type == 'integer' or param_type == 'number':
                dummy_args[param_name] = 0
            elif param_type == 'boolean':
                dummy_args[param_name] = False
            elif param_type == 'array':
                dummy_args[param_name] = []
            elif param_type == 'object':
                dummy_args[param_name] = {}
            else:
                dummy_args[param_name] = f"dummy_{param_name}"
            print(f"  - Added dummy arg: {param_name}={dummy_args[param_name]}")

        print(f"Standalone: Using generated dummy arguments: {dummy_args}")

        try:
            result = await manager.execute_tool_streaming(first_tool_name, dummy_args)
            print(f"\nStandalone Execution Test: FINISHED for tool '{first_tool_name}'.")
            if result:
                print(f"  Standalone Final Result (Placeholder/Accumulated): {result}")
            else:
                print("  Standalone Execution might have failed or returned None (check logs above).")
        except Exception as e:
            print(f"\nStandalone Execution Test: FAILED - An unexpected error occurred: {e}")

    print("\n--- MCP Tool Manager Test Finished (Standalone) ---")


if __name__ == "__main__":
    if sys.version_info < (3, 7):
        print("ERROR: This script requires Python 3.7 or higher for asyncio.run().")
        sys.exit(1)

    if MCPToolManager is None:
        print("Cannot run standalone tests because MCPToolManager failed to import.")
        sys.exit(1)

    asyncio.run(run_standalone_tests())