#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import sys
import traceback
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from beeai_framework.agents import AgentExecutionConfig
from beeai_framework.agents.react import ReActAgent
from beeai_framework.backend import ChatModel, ChatModelParameters
from beeai_framework.emitter import EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import TokenMemory
from beeai_framework.tools.mcp import MCPTool
from beeai_framework.tools.weather import OpenMeteoTool
from beeai_framework.adapters.ollama import OllamaChatModel
from beeai_framework.emitter import Emitter, EmitterOptions, EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.template import PromptTemplateInput
from beeai_framework.tools import AnyTool
from beeai_framework.utils import AbortSignal

from src.agents.agent import Agent

# Load environment variables
load_dotenv()

def print_events(data: Any, event: EventMeta) -> None:
    """Print agent events"""
    if event.name in ["start", "retry", "update", "success", "error"]:
        print(f"\n** Event ({event.name}): {event.path} **\n{data}")

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-slack"],
    env={
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", default=""),
        "SLACK_TEAM_ID": os.getenv("SLACK_TEAM_ID", default=""),
        "PATH": os.getenv("PATH", default=""),
    },
)

async def slack_tool() -> MCPTool:
    async with stdio_client(server_params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        # Discover Slack tools via MCP client
        slacktools = await MCPTool.from_client(session)
        filter_tool = filter(lambda tool: tool.name == "slack_post_message", slacktools)
        slack = list(filter_tool)
        return slack[0]


class SlackAgent(Agent):
    """
    SlackAgent extends the Agent class to post messages to a slack channel.
    """

    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified BeeAI agent.

        Args:
            agent_name (str): The name of the agent.
        """
        super().__init__(agent)

    async def create_agent(self):
        llm = ChatModel.from_name(
            "ollama:granite3.1-dense:8b",
            ChatModelParameters(temperature=0),
        )

        # Configure tools
        slack = await slack_tool()

        # Create agent with memory and tools and custom system prompt template
        self.agent = ReActAgent(
            llm=llm,
            tools=[slack],
            memory=TokenMemory(llm),
            templates={
                "system": lambda template: template.update(
                    defaults={
                        "instructions": """
                        You are a helpful assistant. When prompted to post to Slack, send messages to the channel "C08PC6Z99CN"."""
                    }
                )
            },
        )

    async def run(self, prompt: str) -> str:
        """
        Runs the BeeAI agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """

        self.print(f"Running {self.agent_name}...\n")
        await self.create_agent()

        response = await self.agent.run(
            prompt=prompt,
            execution=AgentExecutionConfig(
                max_retries_per_step=3, total_max_retries=10,
                max_iterations=20
            ),
            signal=AbortSignal.timeout(2 * 60 * 1000),
        )
        answer = response.result.text
        self.print(f"Response from {self.agent_name}: {answer}\n")
        return answer

    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        self.print(f"Running {self.agent_name}...\n")
        await self.create_agent()

        answer = response.result.text
        self.print(f"Response from {self.agent_name}: {answer}\n")
        return answer

        response = await self.agent.run(
            prompt=prompt,
            execution=AgentExecutionConfig(
                max_retries_per_step=3, total_max_retries=10,
                max_iterations=20
            ),
            signal=AbortSignal.timeout(2 * 60 * 1000),
        )
        answer = response.result.text
        self.print(f"Response from {self.agent_name}: {answer}\n")
        return answer
