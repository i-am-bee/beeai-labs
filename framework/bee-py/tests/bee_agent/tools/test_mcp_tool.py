# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp.types import (
    Tool as MCPToolInfo,
    CallToolResult,
    TextContent,
)
from mcp.client.session import ClientSession
from bee_agent.tools import MCPTool, MCPToolOutput


# Common Fixtures
@pytest.fixture
def mock_client_session():
    return AsyncMock(spec=ClientSession)


# Basic Tool Test Fixtures
@pytest.fixture
def mock_tool_info():
    return MCPToolInfo(
        name="test_tool",
        description="A test tool",
        inputSchema={},
    )


@pytest.fixture
def call_tool_result():
    return CallToolResult(
        output="test_output",
        content=[
            {
                "text": "test_content",
                "type": "text",
            }
        ],
    )


# Calculator Tool Test Fixtures
@pytest.fixture
def add_numbers_tool_info():
    return MCPToolInfo(
        name="add_numbers",
        description="Adds two numbers together",
        inputSchema={
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    )


@pytest.fixture
def add_result():
    return CallToolResult(
        output="8",
        content=[TextContent(text="8", type="text")],
    )


# Basic Tool Tests
class TestMCPTool:
    @pytest.mark.asyncio
    async def test_mcp_tool_initialization(self, mock_client_session, mock_tool_info):
        tool = MCPTool(client=mock_client_session, tool=mock_tool_info)

        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.input_schema() == {}

    @pytest.mark.asyncio
    async def test_mcp_tool_run(
        self, mock_client_session, mock_tool_info, call_tool_result
    ):
        mock_client_session.call_tool = AsyncMock(return_value=call_tool_result)
        tool = MCPTool(client=mock_client_session, tool=mock_tool_info)
        input_data = {"key": "value"}

        result = await tool._run(input_data)

        mock_client_session.call_tool.assert_awaited_once_with(
            name="test_tool", arguments=input_data
        )
        assert isinstance(result, MCPToolOutput)
        assert result.result == call_tool_result

    @pytest.mark.asyncio
    async def test_mcp_tool_from_client(self, mock_client_session, mock_tool_info):
        tools_result = MagicMock()
        tools_result.tools = [mock_tool_info]
        mock_client_session.list_tools = AsyncMock(return_value=tools_result)

        tools = await MCPTool.from_client(mock_client_session)

        mock_client_session.list_tools.assert_awaited_once()
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
        assert tools[0].description == "A test tool"


# Calculator Tool Tests
class TestAddNumbersTool:
    @pytest.mark.asyncio
    async def test_add_numbers_mcp(
        self, mock_client_session, add_numbers_tool_info, add_result
    ):
        mock_client_session.call_tool = AsyncMock(return_value=add_result)
        tool = MCPTool(client=mock_client_session, tool=add_numbers_tool_info)
        input_data = {"a": 5, "b": 3}

        result = await tool._run(input_data)

        mock_client_session.call_tool.assert_awaited_once_with(
            name="add_numbers", arguments=input_data
        )
        assert isinstance(result, MCPToolOutput)
        assert result.result.output == "8"
        assert result.result.content[0].text == "8"

    @pytest.mark.asyncio
    async def test_add_numbers_from_client(
        self, mock_client_session, add_numbers_tool_info
    ):
        tools_result = MagicMock()
        tools_result.tools = [add_numbers_tool_info]
        mock_client_session.list_tools = AsyncMock(return_value=tools_result)

        tools = await MCPTool.from_client(mock_client_session)

        mock_client_session.list_tools.assert_awaited_once()
        assert len(tools) == 1
        assert tools[0].name == "add_numbers"
        assert "adds two numbers" in tools[0].description.lower()
