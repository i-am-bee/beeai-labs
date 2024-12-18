from abc import ABC, abstractmethod
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Union

import json
import chevron

from bee_agent.llms import (
    BaseLLM,
    Prompt,
    AssistantPromptTemplate,
    SystemPromptTemplate,
    UserPromptTemplate,
)
from bee_agent.memory import BaseMessage, BaseMemory, UnconstrainedMemory
from bee_agent.tools import Tool
from bee_agent.utils import BeeLogger, Role


logger = BeeLogger(__name__)
T = TypeVar("T")


class BaseAgent(ABC):
    llm: Optional[BaseLLM] = None
    tools: List[Tool]
    memory: BaseMemory

    max_iterations = 20

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        tools: Optional[List[Tool]] = [],
        memory: Optional[BaseMemory] = None,
    ):
        self.llm = llm
        self.tools = tools
        self.memory = memory if memory else UnconstrainedMemory()

        logger.debug(f"Using model {self.llm.model}")

    @abstractmethod
    def _run(self, prompt: Optional[Prompt] = None, options: Optional[T] = None):
        pass

    async def init_memory(self):
        logger.debug(f"Initializing {type(self.memory).__name__}")

        self.memory.reset()
        system_prompt = dict(SystemPromptTemplate)

        if len(self.tools):
            tool_box = [tool.prompt_data() for tool in self.tools]
            system_prompt["data"] = {
                "tools": tool_box,
                "tools_length": len(tool_box),
                "instructions": "You are a helpful assistant",
            }
        await self.memory.add(
            BaseMessage.of(
                {
                    "role": Role.SYSTEM.value,
                    "text": chevron.render(**system_prompt),
                    "meta": {"createdAt": datetime.now().isoformat()},
                }
            )
        )

    async def plan_step(self, prompt, step_state={}, options=None):
        iteration_count = step_state.get("count", 0)

        logger.debug(f"Preparing for iteration: {iteration_count + 1}")

        if iteration_count >= self.max_iterations:
            logger.warning("Maximum iterations reached. Stopping.")
            return

        if iteration_count == 0:
            user_prompt = dict(UserPromptTemplate)
            user_prompt["data"] = {"input": prompt.get("prompt", "")}
            logger.info(f"User: {prompt.get('prompt', '')}")
            await self.memory.add(
                BaseMessage.of(
                    {
                        "role": Role.USER.value,
                        "text": chevron.render(**user_prompt),
                        "meta": {"createdAt": datetime.now().isoformat()},
                    }
                )
            )

        step_state["count"] = iteration_count + 1

        output_parts = step_state.pop("output_parts", {})
        if output_parts.get("Function Name") and output_parts.get("Function Input"):
            tool_input = json.loads(output_parts.get("Function Input"))
            tool_name = output_parts.get("Function Name")

            tool = list(filter(lambda t: t.name == tool_name, self.tools))[0]

            tool_response = tool.run(tool_input)
            logger.debug(f"Response from {tool_name}: {tool_response}")

            assistant_prompt = dict(AssistantPromptTemplate)
            assistant_prompt["data"] = {
                "thought": output_parts.get("Thought"),
                "tool_name": output_parts.get("Function Name"),
                "tool_input": tool_input,
                "tool_output": tool_response,
            }

            logger.info(f"Agent (thought) 🤖: {output_parts.get('Thought')}")
            logger.info(f"Agent (tool_name) 🤖: {output_parts.get('Function Name')}")
            logger.info(f"Agent (tool_input) 🤖: {output_parts.get('Function Input')}")
            await self.memory.add(
                BaseMessage.of(
                    {
                        "role": Role.ASSISTANT.value,
                        "text": chevron.render(**assistant_prompt),
                        "meta": {"createdAt": datetime.now().isoformat()},
                    }
                )
            )

        await self.execute_step(prompt, step_state, options)

    async def execute_step(self, prompt, step_state={}, options=None):
        logger.debug(f"Running iteration: {step_state.get('count')}")

        response = self._run(prompt, options)
        await self.observe_step(response, prompt, step_state, options)

    async def observe_step(self, output, prompt, step_state, options):
        logger.debug(f"Reviewing result of iteration: {step_state.get('count')}")

        content = (
            output if type(output) is str else output.messages[0]
        )  # output.get("message", {}).get("content")
        result = self.llm.parse_output(content, self.tools) if self.llm else content

        if result:
            output_parts = {}
            for line in result.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    output_parts[k.strip()] = v.strip()

            final_answer = output_parts.get("Final Answer")
            if final_answer:
                logger.info(f"Agent (final_answer) 🤖: {final_answer}")
                await self.memory.add(
                    BaseMessage.of(
                        {
                            "role": Role.ASSISTANT.value,
                            "text": final_answer,
                            "meta": {"createdAt": datetime.now().isoformat()},
                        }
                    )
                )
            else:
                step_state["output_parts"] = output_parts
                await self.plan_step(prompt, step_state, options)
        else:
            await self.plan_step(prompt, step_state, options)

    def run(
        self, prompt: Optional[Union[Prompt, str]] = None, options: Optional[T] = None
    ):
        _prompt = {"prompt": prompt} if type(prompt) is str else prompt

        async def runner(agent, _prompt):
            await agent.init_memory()
            await agent.plan_step(_prompt, {"count": 0}, options)

        try:
            # Already running event loop, e.g., Jupyter
            asyncio.get_running_loop()
            # Create a separate thread so we can block before returning
            with ThreadPoolExecutor(1) as pool:
                pool.submit(lambda: asyncio.run(runner(self, _prompt))).result()
        except RuntimeError:
            # No event loop
            asyncio.run(runner(self, _prompt))


class BeeAgent(BaseAgent):
    def _run(self, prompt: Prompt, options: Optional[Dict[str, Any]] = None):
        if self.llm:
            return self.llm.generate(self.memory.messages, options)
