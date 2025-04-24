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
from typing import Final, Optional, List, Any
import asyncio
import traceback
from contextlib import AsyncExitStack

# TODO Only agent *needs* aliasing
from agents import (
    Agent as OAIAgent,
    Runner as OAIRunner,
    AsyncOpenAI as OAIAsyncOpenAI,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    Tool,
    WebSearchTool,
)
# MCPServer might be unused now if only SSE is used, but keep for context
from agents.mcp import MCPServer, MCPServerSse

from src.agents.agent import Agent


# --- Handle integrated openAI API tools - currently only web_search (requires responses API)

SUPPORTED_TOOL_NAME = "web_search"
TOOL_REQUIRES_RESPONSES_API = True

def _openai_tools_from_agent_definition(
    agent_tool_names: Optional[List[str]],
    agent_name: str,
    uses_chat_completions_api: bool,
    print_func: callable
) -> List[Tool]:

    openai_tools: List[Tool] = []
    tool_requested = agent_tool_names and SUPPORTED_TOOL_NAME in agent_tool_names

    if not tool_requested:
        if agent_tool_names:
            print_func(f"WARN [OpenAIAgent {agent_name}]: Specified tools {agent_tool_names} do not include the only supported tool: '{SUPPORTED_TOOL_NAME}'. No tools will be added.")
        else:
            print_func(f"DEBUG [OpenAIAgent {agent_name}]: No tools specified or '{SUPPORTED_TOOL_NAME}' not requested.")
        return openai_tools

    # --- 'web_search' was requested, now check compatibility ---
    print_func(f"DEBUG [OpenAIAgent {agent_name}]: Tool '{SUPPORTED_TOOL_NAME}' requested.")

    # Check API compatibility: WebSearchTool needs Responses API
    if TOOL_REQUIRES_RESPONSES_API and uses_chat_completions_api:
        print_func(
            f"WARN [OpenAIAgent {agent_name}]: Skipping tool '{SUPPORTED_TOOL_NAME}'. OpenAI Responses API not available (using chat_completions API)."
            )
        return openai_tools

    # --- Compatible: Add the tool ---
    try:
        tool_instance = WebSearchTool()
        openai_tools.append(tool_instance)
        print_func(f"INFO [OpenAIAgent {agent_name}]: Added supported tool: {SUPPORTED_TOOL_NAME}")
    except Exception as e:
        print_func(f"ERROR [OpenAIAgent {agent_name}]: Failed to instantiate tool '{SUPPORTED_TOOL_NAME}': {e}")
        return []

    return openai_tools
# --- End of tool processing function ---


class OpenAIAgent(Agent):
    """
    OpenAI extends the Agent class to load and run a agent using OpenAI.
    Simplified version supporting only the 'web_search' tool.
    Can connect to multiple MCP servers defined via environment variable
    MAESTRO_MCP_ENDPOINTS.
    """
    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified OpenAI agent.

        Args:
            agent (dict): The agent definition dictionary.
        """
        super().__init__(agent)

        OPENAI_DEFAULT_URL: Final[str] = "https://api.openai.com/v1"
        self.base_url = os.getenv("OPENAI_BASE_URL", OPENAI_DEFAULT_URL)
        self.api_key = os.getenv("OPENAI_API_KEY")
        spec_dict = agent.get('spec', {})
        self.model_name: str = spec_dict.get('model', "gpt-4o-mini") # Keep internal ref

        self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Base URL: {self.base_url}")
        self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Model: {self.model_name}")

        self.client = OAIAsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        # Update the parms for the endpoint. Tracing uses OpenAI backend, so disable tracing too
        set_default_openai_client(client=self.client, use_for_tracing=False)
        set_tracing_disabled(disabled=True)

        # Use chat completions if we're not using the default endpoint
        # This affects tool compatibility (WebSearch needs Responses API)
        self.uses_chat_completions = self.base_url != OPENAI_DEFAULT_URL
        if self.uses_chat_completions:
            set_default_openai_api("chat_completions")
            # Changed log level to INFO as it's an important configuration detail
            self.print(f"INFO [OpenAIAgent {self.agent_name}]: Non-default base URL detected. Forcing 'chat_completions' API. The '{SUPPORTED_TOOL_NAME}' tool may be unavailable.")
        else:
            # Assuming default URL uses Responses API implicitly if available via the library
            self.print(f"INFO [OpenAIAgent {self.agent_name}]: Using default base URL. Assuming Responses API is available for tools if supported by the model/library.")


        # Add requested static tools to the client (only web_search supported)
        agent_spec = agent.get("spec", {})
        self.tools: List[Tool] = _openai_tools_from_agent_definition(
            agent_tool_names=agent_spec.get("tools"),
            agent_name=self.agent_name,
            uses_chat_completions_api=self.uses_chat_completions,
            print_func=self.print
        )

        self.agent_id=self.agent_name   


    # For MCP set environment to point to list of MCP servers (running SSE) ie
    # export MAESTRO_MCP_ENDPOINTS="http://localhost:8000/sse,http://mcp-server-2:8001/sse"
    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt, potentially using multiple MCP servers.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        mcp_endpoints_str = os.getenv("MAESTRO_MCP_ENDPOINTS", "")
        mcp_endpoint_urls = [url.strip() for url in mcp_endpoints_str.split(',') if url.strip()]

        active_mcp_servers: List[MCPServerSse] = []
        result = None

        try:
            # Use AsyncExitStack a
            async with AsyncExitStack() as stack:
                if not mcp_endpoint_urls:
                    self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: No MCP endpoints configured in MAESTRO_MCP_ENDPOINTS.")
                else:
                    self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Attempting to connect to MCP Servers: {mcp_endpoint_urls}...")

                    for i, url in enumerate(mcp_endpoint_urls):
                        server_name = f"{self.agent_name}_MCP_Server_{i+1}"
                        try:
                            server = MCPServerSse(
                                name=server_name,
                                params={"url": url},
                            )

                            await stack.enter_async_context(server)
                            self.print(f"INFO [OpenAIAgent {self.agent_name}]: MCP Server connected: {server.name} ({url})")
                            active_mcp_servers.append(server) # Add the active server to the list
                        except ConnectionRefusedError:
                            self.print(f"WARN [OpenAIAgent {self.agent_name}]: MCP Server connection refused: {server_name} ({url})")
                        except Exception as conn_err:
                            self.print(f"WARN [OpenAIAgent {self.agent_name}]: Failed to connect MCP Server {server_name} ({url}): {conn_err}")

                if not active_mcp_servers and mcp_endpoint_urls:
                    self.print(f"WARN [OpenAIAgent {self.agent_name}]: Failed to connect to any configured MCP servers. Running without MCP.")
                elif active_mcp_servers:
                    self.print(f"INFO [OpenAIAgent {self.agent_name}]: Running agent with {len(active_mcp_servers)} active MCP server(s).")

                openai_agent = OAIAgent(
                    name=self.agent_name,
                    instructions=self.instructions,
                    model=self.model_name,
                    tools=self.tools,
                    mcp_servers=active_mcp_servers,
                    # TODO: Needs more investigation - auto, required, could be model specific
                    # model_settings=ModelSettings(tool_choice="required")
                )

                self.print(f"Running {self.agent_name} with prompt...")
                result = await OAIRunner.run(openai_agent, prompt)
                self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Agent run completed.")

        except Exception as e:
            error_msg = f"ERROR [OpenAIAgent {self.agent_name}]: Agent run failed: {e}"
            self.print(error_msg)
            self.print(traceback.format_exc())
            return f"Error during agent execution: {e}"

        if result is None:
            self.print(f"ERROR [OpenAIAgent {self.agent_name}]: Agent run did not produce a result object.")
            return "Error: Agent run failed to produce a result."

        final_output = getattr(result, 'final_output', None)
        if final_output is None:
            self.print(f"WARN [OpenAIAgent {self.agent_name}]: Agent run completed but no 'final_output' found in the result object.")
            messages = getattr(result, 'messages', [])
            last_message_content = messages[-1].content if messages and hasattr(messages[-1], 'content') else "No message content available."
            final_output_str = f"Agent run finished without explicit final output. Last message: {last_message_content}"
            self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: {final_output_str}")
            return final_output_str
        else:
            final_output_str = str(final_output)
            self.print(f"Response from {self.agent_name}: {final_output_str}")
            return final_output_str


    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        # TODO: Implement actual streaming logic if the underlying library supports it easily.
        # For now, it just calls the non-streaming run method.
        self.print(f"WARN [OpenAIAgent {self.agent_name}]: Streaming not fully implemented, falling back to non-streaming run.")
        return await self.run(prompt)