#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
""" Agent """
from typing import Any
import dotenv
from pydantic import BaseModel

from beeai_framework.adapters.ollama import OllamaChatModel
from beeai_framework.agents import AgentExecutionConfig
from beeai_framework.agents.react import ReActAgent
from beeai_framework.emitter import Emitter, EmitterOptions, EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.template import PromptTemplateInput
from beeai_framework.tools import AnyTool
from beeai_framework.tools.search import DuckDuckGoSearchTool
from beeai_framework.tools.weather import OpenMeteoTool
from beeai_framework.utils import AbortSignal

from src.agents.agent import Agent

dotenv.load_dotenv()

def user_customizer(config: PromptTemplateInput[Any]) -> PromptTemplateInput[Any]:
    """ user_customizer """

    class UserSchema(BaseModel):
        """ user schema"""
        input: str

    new_config = config.model_copy()
    new_config.input_schema = UserSchema
    new_config.template = """User: {{input}}"""
    return new_config

def no_result_customizer(config: PromptTemplateInput[Any]) -> PromptTemplateInput[Any]:
    """ no_result_customizer """
    new_config = config.model_copy()
    config.template += """\nPlease reformat your input."""
    return new_config

def not_found_customizer(config: PromptTemplateInput[Any]) -> PromptTemplateInput[Any]:
    """ not_found_customizer """
    class ToolSchema(BaseModel):
        """ Tool Schema """
        name: str

    class NotFoundSchema(BaseModel):
        """ Not found schema """
        tools: list[ToolSchema]

    new_config = config.model_copy()
    new_config.input_schema = NotFoundSchema
    new_config.template = """Tool does not exist!
{{#tools.length}}
Use one of the following tools: {{#trim}}{{#tools}}{{name}},{{/tools}}{{/trim}}
{{/tools.length}}"""
    return new_config

def user_template_func(template: PromptTemplateInput[Any]) -> PromptTemplateInput[Any]:
    return template.fork(customizer=user_customizer)

def system_template_func(template: PromptTemplateInput[Any], instructions: str) -> PromptTemplateInput[Any]:
    return template.update(defaults={"instructions": instructions.strip()})

def tool_no_result_error_template_func(template: PromptTemplateInput[Any]) -> PromptTemplateInput[Any]:
    return template.fork(customizer=no_result_customizer)

def tool_not_found_error_template_func(template: PromptTemplateInput[Any]) -> PromptTemplateInput[Any]:
    return template.fork(customizer=not_found_customizer)

def write(role: str, data: str) -> None:
    """ write message """
    print(f"{role} {data}")

def process_agent_events(data: Any, event: EventMeta) -> None:
    """Process agent events and log appropriately"""

    if event.name == "error":
        write("Agent 🤖 : ", FrameworkError.ensure(data.error).explain())
    elif event.name == "success":
        write("Agent 🤖 : ", "success")


def observer(emitter: Emitter) -> None:
    """Observer"""
    emitter.on("*", process_agent_events, EmitterOptions(match_nested=False))

class BeeAILocalAgent(Agent):
    """
    BeeAILocalAgent extends the Agent class to load and run a specific agent.
    """

    def __init__(self, agent: dict) -> None:
        """
        Initializes the workflow for the specified BeeAI agent.
         
        Args:
            agent_name (str): The name of the agent. 
        """
        super().__init__(agent)

        llm = OllamaChatModel(self.agent_model)

        templates: dict[str, Any] = {
            "user": user_template_func,
            "system": system_template_func,
            "tool_no_result_error": tool_no_result_error_template_func,
            "tool_not_found_error": tool_not_found_error_template_func,
        }

        tools: list[AnyTool] = [
            # WikipediaTool(),
            OpenMeteoTool(),
            DuckDuckGoSearchTool(),
        ]

        self.agent = ReActAgent(
            llm=llm, templates=templates, tools=tools, memory=UnconstrainedMemory()
        )

    async def run(self, prompt: str) -> str:
        """
        Runs the BeeAI agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """

        print(f"🐝 Running {self.agent_name}...\n")
        response = await self.agent.run(
            prompt=prompt,
            execution=AgentExecutionConfig(
                max_retries_per_step=3, total_max_retries=10,
                max_iterations=20
            ),
            signal=AbortSignal.timeout(2 * 60 * 1000),
        ).observe(observer)
        answer = response.result.text
        print(f"🐝 Response from {self.agent_name}: {answer}\n")
        return answer

    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        print(f"🐝 Running {self.agent_name}...\n")
        response = await self.agent.run(
            prompt=prompt,
            execution=AgentExecutionConfig(
                max_retries_per_step=3,
                total_max_retries=10,
                max_iterations=20
            ),
            signal=AbortSignal.timeout(2 * 60 * 1000),
        ).observe(observer)
        answer = response.result.text
        print(f"🐝 Response from {self.agent_name}: {answer}\n")
        return answer
