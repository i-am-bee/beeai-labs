# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List, Optional, TypeVar, Any, Sequence
from dataclasses import dataclass

from bee_agent.tools import Tool
from bee_agent.utils import BeeEventEmitter
from mcp.client.session import ClientSession
from mcp.types import (
    Tool as MCPToolInfo,
    CallToolResult,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

T = TypeVar("T")


@dataclass
class MCPToolInput:
    """Input configuration for MCP Tool initialization."""

    client: ClientSession
    tool: MCPToolInfo


class MCPToolOutput:
    """Output class for MCP Tool results."""

    def __init__(self, result: CallToolResult):
        self.result = result


class MCPTool(Tool[MCPToolOutput]):
    """Tool implementation for Model Context Protocol."""

    def __init__(self, client: ClientSession, tool: MCPToolInfo, **options):
        """Initialize MCPTool with client and tool configuration."""
        super().__init__(options)
        self.client = client
        self._tool = tool
        self._name = tool.name
        self._description = (
            tool.description
            or "No available description, use the tool based on its name and schema."
        )
        self.emitter = BeeEventEmitter()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def input_schema(self) -> str:
        return self._tool.inputSchema

    async def _run(
        self, input_data: Any, options: Optional[Dict] = None
    ) -> MCPToolOutput:
        """Execute the tool with given input."""
        print(f"Executing tool {self.name} with input: {input_data}")  # Debug
        result = await self.client.call_tool(name=self.name, arguments=input_data)
        print(f"Tool result: {result}")  # Debug
        return MCPToolOutput(result)

    @classmethod
    async def from_client(cls, client: ClientSession) -> List["MCPTool"]:
        tools_result = await client.list_tools()
        return [cls(client=client, tool=tool) for tool in tools_result.tools]
