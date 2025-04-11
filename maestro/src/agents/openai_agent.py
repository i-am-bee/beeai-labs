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

import agents

from .agent import Agent

class OpenAIAgent(Agent):
    def __init__(self, agent: dict) -> None:
        super.__init__(agent)
        self.openai_agent = agents.Agent(
            name=self.agent_name,
            instructions=self.instructions,
            tools=self.tools)
    
    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        self.print(f"Running {self.agent_name}...")
        result = await agents.Runner.run(self.openai_agent, prompt)        
        self.print(f"Response from {self.agent_name}: {result.final_output}")
        return result.final_output

    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """        
        return self.run(prompt)