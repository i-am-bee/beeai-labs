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


if __name__ == "__main__":
    import asyncio
    from mcp.server import Server
    from mcp.shared.memory import create_connected_server_and_client_session

    ab_input_schema = {
        "type": "object",
        "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        "required": ["a", "b"],
    }

    async def add_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        print(f"Add tool called with arguments: {arguments}")  # Debug
        a, b = float(arguments["a"]), float(arguments["b"])
        result = str(
            int(a + b)
        )  # Convert to int since we're testing with whole numbers
        print(f"Add tool result: {result}")  # Debug
        return [TextContent(type="text", text=result)]

    async def multiply_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        print(f"Multiply tool called with arguments: {arguments}")  # Debug
        a, b = float(arguments["a"]), float(arguments["b"])
        result = str(
            int(a * b)
        )  # Convert to int since we're testing with whole numbers
        print(f"Multiply tool result: {result}")  # Debug
        return [TextContent(type="text", text=result)]

    async def run_tests():
        print("Starting MCP Tool tests...")

        # Set up server
        server = Server("test-server")

        @server.list_tools()
        async def handle_list_tools():
            return [
                MCPToolInfo(
                    name="add",
                    description="Adds two numbers",
                    inputSchema=ab_input_schema,
                ),
                MCPToolInfo(
                    name="multiply",
                    description="Multiplies two numbers",
                    inputSchema=ab_input_schema,
                ),
            ]

        @server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict
        ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            print(
                f"Server handling tool call: {name} with arguments: {arguments}"
            )  # Debug
            if name == "add":
                return await add_tool(name, arguments)
            elif name == "multiply":
                return await multiply_tool(name, arguments)
            raise ValueError(f"Unknown tool: {name}")

        try:
            async with create_connected_server_and_client_session(server) as client:
                print("\nTest 1: Listing tools...")
                tools = await MCPTool.from_client(client)
                assert len(tools) == 2
                print("✓ Tools listed successfully")

                print("\nTest 2: Calling add tool...")
                add_tool_instance = next(t for t in tools if t.name == "add")
                test_input = {"a": 2, "b": 3}
                print(f"Calling add tool with input: {test_input}")
                result = await add_tool_instance.run(test_input)
                print(f"Add tool result content: {result.result.content[0].text}")
                assert (
                    result.result.content[0].text == "5"
                ), f"Expected '5' but got '{result.result.content[0].text}'"
                print("✓ Add tool called successfully")

                print("\nTest 3: Calling multiply tool...")
                multiply_tool_instance = next(t for t in tools if t.name == "multiply")
                test_input = {"a": 2, "b": 3}
                print(f"Calling multiply tool with input: {test_input}")
                result = await multiply_tool_instance.run(test_input)
                print(f"Multiply tool result content: {result.result.content[0].text}")
                assert (
                    result.result.content[0].text == "6"
                ), f"Expected '6' but got '{result.result.content[0].text}'"
                print("✓ Multiply tool called successfully")

        except Exception as e:
            print(f"Error during tests: {e}")
            import traceback

            traceback.print_exc()
            raise

        print("\nAll tests completed successfully!")

    asyncio.run(run_tests())
