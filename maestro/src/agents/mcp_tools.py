# SPDX-License-Identifier: Apache-2.0

import asyncio
import httpx
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
import traceback
from contextlib import asynccontextmanager 

# TODO: Resilient model loading - import errors during dev (wrong lib)- keep or remove?
try:
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession
    mcp_enabled = True
    MCP_IMPORT_ERROR = None
except ImportError as e:
    print(f"WARNING: Could not import MCP components (sse_client, ClientSession). MCP tool support will be disabled. Run `poetry sync` or `pip install mcp`? Error: {e}")
    mcp_enabled = False
    MCP_IMPORT_ERROR = e
    # Dummies for import failure (to avoid warnings from type safety checks)
    def sse_client(*args, **kwargs): pass
    class ClientSession: pass

# TODO: Needs to be retrieved from config. For now this is default fastmcp on localhost
DEFAULT_MCP_ENDPOINTS: List[str] = [
    "http://localhost:8000/sse",
]

# TODO: Utility function - helped to locate issues during development. Keep, move, or remove?
def _log_exception_details(e: Exception, context_msg: str = ""):
    """Logs details of an exception, including nested ExceptionGroups."""
    print(f"MCPToolManager: {context_msg}: {type(e).__name__} - {e}")

    def print_group(exc_group, indent=0):
        prefix = "  " * indent
        if not isinstance(exc_group, ExceptionGroup):
            print(f"{prefix}Cause: {type(exc_group).__name__} - {exc_group}")
            print(f"{prefix}Traceback:")
            tb_lines = traceback.format_exception(type(exc_group), exc_group, exc_group.__traceback__)
            for line in tb_lines:
                print(f"{prefix}  {line.strip()}")
            return
        print(f"{prefix}ExceptionGroup Message: {exc_group.message}")
        for i, sub_exc in enumerate(exc_group.exceptions):
            print(f"{prefix}Sub-exception {i+1}/{len(exc_group.exceptions)}:")
            print_group(sub_exc, indent + 1)

    if isinstance(e, ExceptionGroup):
        print_group(e)
    else:
        print("Traceback:")
        traceback.print_exc()


class MCPToolManager:
    """
    Manages discovery and interaction with tools via the Model Context Protocol (MCP).
    Uses sse_client context manager for remote access to MCP servers.
    Local access via STDIO is not supported.
    """
    endpoints: List[str]
    # Save tool info
    tools: Dict[str, Tuple[Any, str]]
    openai_tools_schemas: Dict[str, Dict[str, Any]]

    def __init__(self, endpoints: Optional[List[str]] = None):
        """Initializes the MCPToolManager."""
        self.endpoints = []
        self.tools = {}
        self.openai_tools_schemas = {}
        if not mcp_enabled:
            print(f"MCPToolManager disabled due to import error: {MCP_IMPORT_ERROR}")
            return
        self.endpoints = endpoints if endpoints is not None else DEFAULT_MCP_ENDPOINTS
        print(f"MCPToolManager initialized with endpoints: {self.endpoints}")

    @asynccontextmanager
    async def _get_mcp_session(self, endpoint_url: str) -> AsyncGenerator[ClientSession, None]:
        """Async context manager to connect and yield an initialized MCP session."""
        print(f"MCPToolManager: Connecting via SSE to {endpoint_url}...")
        async with sse_client(endpoint_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session

    async def discover_tools(self) -> None:
        """Connects to configured MCP endpoints and discovers available tools."""
        # TODO: This does a fair amount of printing - for library method this probably should be debug only
        if not mcp_enabled:
            print("MCPToolManager: MCP support disabled, skipping discovery.")
            return
        if not self.endpoints:
            print("MCPToolManager: No MCP endpoints configured, skipping discovery.")
            return

        print("MCPToolManager: Starting tool discovery...")
        self.tools = {}
        self.openai_tools_schemas = {}
        discovery_tasks = [self._discover_endpoint(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                pass # Already logged

        print("MCPToolManager: Tool discovery finished.")
        if not self.tools:
            print("MCPToolManager: No tools discovered.")
        else:
            print("MCPToolManager: Discovered tools:")
            for name, (tool, endpoint) in self.tools.items():
                print(f"  - Name: {name}")
                print(f"    Description: {getattr(tool, 'description', 'N/A')}")
                print(f"    Endpoint: {endpoint}")
                print(f"    OpenAI Schema: {self.openai_tools_schemas.get(name)}")

    async def _discover_endpoint(self, endpoint_url: str) -> None:
        """Helper to discover tools from a single endpoint."""
        if not mcp_enabled: return

        try:
            async with self._get_mcp_session(endpoint_url) as session:
                print(f"MCPToolManager: Discovering tools using session for {endpoint_url}...")
                response = await session.list_tools()
                # TODO: should be a .tools attribute (empirically determined) - is this correct way?
                discovered: List[Any] = getattr(response, 'tools', [])

                if not discovered:
                    print(f"MCPToolManager: No tools found at {endpoint_url}.")
                    return

                for tool in discovered:
                    tool_name = getattr(tool, 'name', None)
                    if not tool_name:
                        print(f"MCPToolManager: Warning - Discovered tool at {endpoint_url} is missing a 'name'. Skipping.")
                        continue
                    if tool_name in self.tools:
                        print(f"MCPToolManager: Warning - Duplicate tool name '{tool_name}' found at {endpoint_url}. Overwriting previous definition from {self.tools[tool_name][1]}.")

                    # Store the tool object itself for later use
                    self.tools[tool_name] = (tool, endpoint_url)
                    self.openai_tools_schemas[tool_name] = self._convert_to_openai_tool(tool)
                    print(f"MCPToolManager: Discovered tool '{tool_name}' at {endpoint_url}")

        except httpx.RequestError as e:
            print(f"MCPToolManager: Error connecting via SSE to {endpoint_url}: {e}")
            raise
        except Exception as e:
            _log_exception_details(e, f"Error during SSE discovery at {endpoint_url}")
            raise # Exception as we are initializing ?

    # TODO: Needed to call from OpenAI - keep here, or in openai module?
    def _convert_to_openai_tool(self, tool: Any) -> Dict[str, Any]:
        """Converts an MCP Tool object (duck-typed) to the OpenAI tool format."""
        tool_name = getattr(tool, 'name', 'unknown_tool')
        description = getattr(tool, 'description', None)
        # Should be 'inputSchema' based on docs, fallback to 'parameters'
        parameters = getattr(tool, 'inputSchema', getattr(tool, 'parameters', None))
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description or f"MCP tool: {tool_name}",
                "parameters": parameters or {"type": "object", "properties": {}},
            },
        }

    def get_openai_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns a list of discovered tools formatted for the OpenAI API."""
        return list(self.openai_tools_schemas.values())

    def is_mcp_tool(self, tool_name: str) -> bool:
        """Checks if a tool name corresponds to a discovered MCP tool."""
        return tool_name in self.tools

    async def execute_tool_streaming(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Executes a discovered MCP tool."""
        if not mcp_enabled:
            print("MCPToolManager: Cannot execute tool, MCP support disabled.")
            return None
        if tool_name not in self.tools:
            print(f"MCPToolManager: Error - Attempted to execute unknown tool '{tool_name}'.")
            return None

        tool, endpoint_url = self.tools[tool_name]
        print(f"MCPToolManager: Executing tool '{tool_name}' via SSE to {endpoint_url} with args: {arguments}")
        final_tool_result: Any = None

        try:
            async with self._get_mcp_session(endpoint_url) as session:
                print(f"MCPToolManager: Calling tool '{tool_name}' using session for {endpoint_url}...")
                final_tool_result = await session.call_tool(
                    name=tool_name,
                    arguments=arguments,
                )
                print(f"MCPToolManager: Received result object for '{tool_name}': {final_tool_result!r}")

            print(f"MCPToolManager: Finished execution for '{tool_name}'.")
            # TODO: Every tool will return something different - consider how to handle better
            return {
                "status": "success",
                "message": f"Tool '{tool_name}' executed.",
                "raw_result": final_tool_result
            }

        # TODO: If something goes wrong, do we reraise exception, or just return None - safer??
        except httpx.RequestError as e:
            print(f"MCPToolManager: Error connecting via SSE to {endpoint_url} for tool execution: {e}")
            return None
        except Exception as e:
            _log_exception_details(e, f"Error during SSE tool execution at {endpoint_url}")
            return None
