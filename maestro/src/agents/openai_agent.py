# SPDX-License-Identifier: Apache-2.0

import os
import traceback
from contextlib import AsyncExitStack # Keep this import
from typing import Final, List, Optional, Union, Tuple, Any

from agents import (
    Agent as UnderlyingAgent,
    Runner as UnderlyingRunner,
    AsyncOpenAI as UnderlyingClient,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    Tool,
    WebSearchTool,
    trace,
)

from src.agents.agent import Agent as MaestroAgent
from src.agents.openai_observability import setup_langfuse_tracing
from src.agents.openai_mcp import setup_mcp_servers, MCPServerInstance

SUPPORTED_TOOL_NAME: Final[str] = "web_search"
TOOL_REQUIRES_RESPONSES_API: Final[bool] = True
OPENAI_DEFAULT_URL: Final[str] = "https://api.openai.com/v1"

class OpenAIAgent(MaestroAgent):
    """
    Maestro Agent implementation for OpenAI and compatible APIs.
    """

    def __init__(self, agent_definition: dict) -> None:
        """
        Initializes the OpenAI agent, configures tracing, client, and tools.

        Args:
            agent_definition (dict): The agent definition dictionary from YAML.
        """
        super().__init__(agent_definition)
        self.agent_id = self.agent_name

        spec_dict = agent_definition.get('spec', {})
        self.model_name: str = spec_dict.get('model', "gpt-4o-mini")
        self.base_url: str = os.getenv("OPENAI_BASE_URL", OPENAI_DEFAULT_URL)
        self.api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.uses_chat_completions: bool = self.base_url != OPENAI_DEFAULT_URL

        self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Base URL: {self.base_url}")
        self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Model: {self.model_name}")

        self.langfuse_enabled: bool = setup_langfuse_tracing(self.print)
        self.client: UnderlyingClient = self._initialize_openai_client()
        self._configure_agents_library()
        self.static_tools: List[Tool] = self._initialize_static_tools(spec_dict)


    def _initialize_openai_client(self) -> UnderlyingClient:
        return UnderlyingClient(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def _configure_agents_library(self) -> None:
        set_default_openai_client(client=self.client, use_for_tracing=False)
        if not self.langfuse_enabled:
            if set_tracing_disabled:
                set_tracing_disabled(disabled=True)
                self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Langfuse off, disabling agents lib tracing.")
            else:
                self.print(f"WARN [OpenAIAgent {self.agent_name}]: Langfuse off, cannot disable agents lib tracing.")
        if self.uses_chat_completions:
            set_default_openai_api("chat_completions")
            self.print(f"INFO [OpenAIAgent {self.agent_name}]: Using 'chat_completions' API.")
        else:
            self.print(f"INFO [OpenAIAgent {self.agent_name}]: Assuming 'Responses' API.")


    def _initialize_static_tools(self, agent_spec: dict) -> List[Tool]:
        # ... (implementation remains the same) ...
        agent_tool_names: Optional[List[str]] = agent_spec.get("tools")
        openai_tools: List[Tool] = []
        tool_requested = agent_tool_names and SUPPORTED_TOOL_NAME in agent_tool_names

        if not tool_requested:
            if agent_tool_names:
                self.print(f"WARN [OpenAIAgent {self.agent_name}]: Tools {agent_tool_names} ignore unsupported tool: '{SUPPORTED_TOOL_NAME}'.")
            else:
                self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: No static tools requested.")
            return openai_tools

        self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Tool '{SUPPORTED_TOOL_NAME}' requested.")

        if TOOL_REQUIRES_RESPONSES_API and self.uses_chat_completions:
            self.print(f"WARN [OpenAIAgent {self.agent_name}]: Skipping tool '{SUPPORTED_TOOL_NAME}' due to API incompatibility.")
            return openai_tools

        try:
            tool_instance = WebSearchTool()
            openai_tools.append(tool_instance)
            self.print(f"INFO [OpenAIAgent {self.agent_name}]: Added static tool: {SUPPORTED_TOOL_NAME}")
        except Exception as e:
            self.print(f"ERROR [OpenAIAgent {self.agent_name}]: Failed to instantiate tool '{SUPPORTED_TOOL_NAME}': {e}")
            return []

        return openai_tools

    def _process_agent_result(self, result: Optional[Any]) -> str:
        """Processes the result object from the agent run."""
        # ... (implementation remains the same) ...
        if result is None:
            self.print(f"ERROR [OpenAIAgent {self.agent_name}]: Agent run did not produce a result object.")
            return "Error: Agent run failed to produce a result."

        final_output = getattr(result, 'final_output', None)
        if final_output is not None:
            final_output_str = str(final_output)
            self.print(f"Response from {self.agent_name}: {final_output_str}")
            return final_output_str
        else:
            self.print(f"WARN [OpenAIAgent {self.agent_name}]: Agent run completed but no 'final_output' found.")
            messages = getattr(result, 'messages', [])
            last_message_content = messages[-1].content if messages and hasattr(messages[-1], 'content') else "No message content available."
            fallback_str = f"Agent run finished without explicit final output. Last message: {last_message_content}"
            self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: {fallback_str}")
            return fallback_str


    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt, managing MCP connections and tracing.

        Args:
            prompt (str): The prompt to run the agent with.
        """
        trace_name = f"Maestro OpenAI Agent Run: {self.agent_name}"
        result: Optional[Any] = None

        with trace(trace_name):
            try:
                active_mcp_servers: List[MCPServerInstance]
                active_mcp_servers, mcp_stack = await setup_mcp_servers(
                    print_func=self.print,
                    agent_name=self.agent_name
                )

                # async stack needed to handle the mcp tool connections
                async with mcp_stack:
                    # Create the underlying agent instance
                    underlying_agent = UnderlyingAgent(
                        name=self.agent_name,
                        instructions=self.instructions,
                        model=self.model_name,
                        tools=self.static_tools,
                        mcp_servers=active_mcp_servers,
                    )

                    # Run the agent
                    self.print(f"Running {self.agent_name} with prompt...")
                    result = await UnderlyingRunner.run(underlying_agent, prompt)
                    self.print(f"DEBUG [OpenAIAgent {self.agent_name}]: Agent run completed.")

            except Exception as e:
                error_msg = f"ERROR [OpenAIAgent {self.agent_name}]: Agent run failed: {e}"
                self.print(error_msg)
                self.print(traceback.format_exc())
                return f"Error during agent execution: {e}"

        return self._process_agent_result(result)


    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode. (Not fully implemented)
        Args:
            prompt (str): The prompt to run the agent with.
        """
        self.print(f"WARN [OpenAIAgent {self.agent_name}]: Streaming not implemented, using non-streaming run.")
        return await self.run(prompt)