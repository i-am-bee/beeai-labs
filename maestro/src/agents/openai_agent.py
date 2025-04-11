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
# Import standard AsyncOpenAI and streaming types
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import ChoiceDelta, ChoiceDeltaToolCall
# Keep existing agents imports for now, though their direct use might change
# TODO Only agent *needs* aliasing - Review if OAIAgent/OAIRunner are still needed
from agents import (
    Agent as OAIAgent,
    Runner as OAIRunner,
    # AsyncOpenAI as OAIAsyncOpenAI, # Use standard AsyncOpenAI
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from src.agents.agent import Agent
from typing import List, Dict, Any, AsyncIterator

class OpenAIAgent(Agent):
    """
    OpenAI extends the Agent class to load and run a agent using OpenAI,
    supporting both standard and streaming responses via the Chat Completions API.
    """
    client: AsyncOpenAI
    model_name: str
    openai_agent: OAIAgent
    agent_id: str

    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified OpenAI agent.

        Args:
            agent (dict): The agent configuration dictionary.
        """
        super().__init__(agent)

        # TODO: Add tools (std and MCP) - Note: Tool handling might differ between
        # the 'agents' library and direct OpenAI client usage.

        # TODO : for now we use environment variables - set to http://localhost:11434/v1 for Ollama
        base_url: str = os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1")
        api_key: str | None = os.getenv("OPENAI_API_KEY")
        spec_dict: Dict[str, Any] = agent.get('spec', {})
        self.model_name = spec_dict.get('model', "gpt-4o-mini") # Store model name

        # TODO: Proper debug
        print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Base URL: {base_url}")
        print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Model: {self.model_name}")

        # Use standard AsyncOpenAI client
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        # Update the parms for the endpoint. Tracing uses OpenAI backend, so disable tracing too
        set_default_openai_client(client=self.client, use_for_tracing=False)
        # For now, use the chat completions api, even for OpenAI
        # This confirms we should use client.chat.completions, not the Assistants API
        set_default_openai_api("chat_completions")
        set_tracing_disabled(disabled=True)

        self.openai_agent = OAIAgent(
            name=self.agent_name,
            instructions=self.instructions,
            model=self.model_name
            )

        self.agent_id=self.agent_name # Keep consistent if used elsewhere

    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt using Chat Completions (non-streaming).
        Args:
            prompt (str): The prompt to run the agent with.
        Returns:
            str: The content of the response message or an error string.
        """
        print(f"Running {self.agent_name}...")
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            final_output: str = response.choices[0].message.content or ""
            print(f"Response from {self.agent_name}: {final_output}")
            return final_output
        except Exception as e:
            print(f"Error running agent {self.agent_name}: {e}")
            return f"Error: {e}"


    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt using Chat Completions.
        Prints intermediate outputs (text deltas, tool calls) as they arrive.

        Args:
            prompt (str): The prompt to run the agent with.

        Returns:
            str: The complete final response accumulated from the stream, potentially including error messages.
        """
        print(f"Running {self.agent_name} in streaming mode...")
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]
        # list for response
        full_response_parts: List[str] = []
        # tools use
        tool_calls_details: List[Dict[str, Any]] = []

        def _handle_content_delta(delta: ChoiceDelta) -> None:
            if delta.content:
                content: str = delta.content
                print(content, end="", flush=True)
                full_response_parts.append(content)

        def _handle_tool_call_delta(delta: ChoiceDelta) -> None:
            if not delta.tool_calls:
                return

            print()
            for tool_call_delta in delta.tool_calls:
                index: int = tool_call_delta.index

                # save info about tool calls
                while len(tool_calls_details) <= index:
                    tool_calls_details.append({"id": None, "type": "function", "function": {"name": "", "arguments": ""}})

                current_tool_call: Dict[str, Any] = tool_calls_details[index]

                if tool_call_delta.id:
                    current_tool_call["id"] = tool_call_delta.id
                    print(f"[Tool Call Start] ID: {tool_call_delta.id}", flush=True)
                if tool_call_delta.function:
                    if tool_call_delta.function.name:
                        # Only print name if it's newly provided in this delta
                        if not current_tool_call["function"]["name"]:
                            print(f"  - Function: {tool_call_delta.function.name}", flush=True)
                        current_tool_call["function"]["name"] += tool_call_delta.function.name # Accumulate name parts if chunked
                    if tool_call_delta.function.arguments:
                        args_chunk: str = tool_call_delta.function.arguments
                        current_tool_call["function"]["arguments"] += args_chunk
                        print(f"    Args chunk: {args_chunk}", flush=True)

        def _print_tool_call_summary() -> None:

            if tool_calls_details:
                print("\n[Tool Calls Invoked Summary]:") # Add newline for better formatting
                for tc in tool_calls_details:
                    tc_id = tc.get('id', 'N/A')
                    tc_func = tc.get('function', {})
                    tc_name = tc_func.get('name', 'N/A')
                    tc_args = tc_func.get('arguments', '{}') # Default to empty JSON object string
                    print(f"  - ID: {tc_id}, Function: {tc_name}, Args: {tc_args}")

        try:
            stream: AsyncIterator[ChatCompletionChunk] = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                # TODO: Add info for tools support
                # tools=[...],
                # tool_choice="auto",
            )
            print(f"Assistant ({self.agent_name}): ", end="", flush=True)

            async for chunk in stream:
                if not chunk.choices: # check if empry
                    continue
                delta: ChoiceDelta = chunk.choices[0].delta
                _handle_content_delta(delta)
                _handle_tool_call_delta(delta=delta)

            _print_tool_call_summary()
            print(f"\nStreaming finished for {self.agent_name}.") # Add newline

        except Exception as e:
            print(f"\nError during streaming for {self.agent_name}: {e}")
            # returns response so far
            full_response: str = "".join(full_response_parts)
            return full_response + f"\nError during streaming: {e}"

        # Join all response parts into the final response
        full_response: str = "".join(full_response_parts)
        return full_response