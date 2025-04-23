# src/agents/openai_agent.py
# Copyright © 2025 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
# TODO Only agent *needs* aliasing
from agents import (
    Agent as OAIAgent,
    Runner as OAIRunner,
    AsyncOpenAI as OAIAsyncOpenAI,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from src.agents.agent import Agent
from typing import List, Dict, Any, AsyncIterator, Optional # Added Optional
import asyncio # Added for gather

# Import the MCP Tool Manager
from .mcp_tools import MCPToolManager, mcp_enabled # Import mcp_enabled flag too

class OpenAIAgent(Agent):
    """
    OpenAI extends the Agent class to load and run a agent using OpenAI,
    supporting both standard and streaming responses via the Chat Completions API,
    and potentially utilizing MCP tools.
    """
    client: OAIAsyncOpenAI
    model_name: str
    openai_agent: OAIAgent # Instance of the Agent class from the 'agents' library
    agent_id: str
    mcp_tool_manager: Optional[MCPToolManager] # Add MCP tool manager instance variable
    openai_mcp_tools: List[Dict[str, Any]] # Store formatted tools for OpenAI API

    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified OpenAI agent.
        Also initializes MCP tool discovery if enabled.

        Args:
            agent_name (str): The name of the agent.
        """
        super().__init__(agent)

        # --- OpenAI Client Setup (existing code) ---
        base_url: str = os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1")
        api_key: str | None = os.getenv("OPENAI_API_KEY")
        spec_dict: Dict[str, Any] = agent.get('spec', {})
        self.model_name = spec_dict.get('model', "gpt-4o-mini")

        print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Base URL: {base_url}")
        print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Model: {self.model_name}")

        self.client = OAIAsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        set_default_openai_client(client=self.client, use_for_tracing=False)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(disabled=True)

        # Get tools available from mcp
        self.mcp_tool_manager = None
        self.openai_mcp_tools = []
        if mcp_enabled:
            # TODO: Pass endpoints from config if needed, otherwise uses defaults
            self.mcp_tool_manager = MCPToolManager()
            # Note: Discovery is async, needs to be run in an event loop.
            # We'll trigger it before the first run if not already done.
            # Or, ideally, initialize it asynchronously if the main app structure allows.
            # For now, let's plan to call it within the run methods.
            print(f"DEBUG [OpenAIAgent {self.agent_name}]: MCP Tool Manager initialized.")
            print(f"DEBUG [OpenAIAgent {self.agent_name}]: Triggering MCP tool discovery...")
            # TODO - Async function to sort
            self.mcp_tool_manager.discover_tools()
            self.openai_mcp_tools = self.mcp_tool_manager.get_openai_tool_schemas()
            print(f"DEBUG [OpenAIAgent {self.agent_name}]: MCP tools ready for OpenAI API: {len(self.openai_mcp_tools)}")
        else:
            print(f"DEBUG [OpenAIAgent {self.agent_name}]: MCP Tool Manager disabled.")
        
        self.openai_agent = OAIAgent(
            name=self.agent_name,
            instructions=self.instructions,
            model=self.model_name,
            # TODO: Agent SDK does not support MCP Tools ! (FATAL)
            tools=self.openai_mcp_tools,
        )
        
        self.agent_id=self.agent_name


    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt using Chat Completions (non-streaming).
        Includes discovered MCP tools in the API call if available.

        Args:
            prompt (str): The prompt to run the agent with.
        Returns:
            str: The content of the response message or an error string.
        """

        """
        Runs the agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        self.print(f"Running {self.agent_name}...")
        result = await OAIRunner.run(self.openai_agent, prompt)
        self.print(f"Response from {self.agent_name}: {result.final_output}")
        return result.final_output


    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        return await self.run(prompt)