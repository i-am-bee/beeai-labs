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

class OpenAIAgent(Agent):
    """
    OpenAI extends the Agent class to load and run a agent using OpenAI.
    """
    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified OpenAI agent.

        Args:
            agent_name (str): The name of the agent.
        """
        super().__init__(agent)
        
        # TODO: Add tools (std and MCP)

        # TODO : for now we use environment variables - set to http://localhost:11434/v1 for Ollama
        base_url = os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")
        spec_dict = agent.get('spec', {})
        model_name: str = spec_dict.get('model', "gpt-4o-mini")

        # TODO: Proper debug
        print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Base URL: {base_url}")
        print(f"DEBUG [OpenAIAgent {self.agent_name}]: Using Model: {model_name}")
        
        client = OAIAsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        # Update the parms for the endpoint. Tracing uses OpenAI backend, so disable tracing too
        set_default_openai_client(client=client, use_for_tracing=False)
        # For now, use the chat completions api, even for OpenAI
        set_default_openai_api("chat_completions")
        set_tracing_disabled(disabled=True)
        
        self.openai_agent = OAIAgent(
            name=self.agent_name,
            instructions=self.instructions,
            model=model_name
            )

        self.agent_id=self.agent_name
    
    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        print(f"Running {self.agent_name}...")
        result = await OAIRunner.run(self.openai_agent, prompt)        
        print(f"Response from {self.agent_name}: {result.final_output}")
        return result.final_output

    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """        
        return await self.run(prompt)