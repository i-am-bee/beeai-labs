# SPDX-License-Identifier: Apache-2.0

import asyncio
import json

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Union


from bee_agent.llms import (
    BaseLLM,
    Prompt,
    AssistantPromptTemplate,
    SystemPromptTemplate,
    UserPromptTemplate,
)
from bee_agent.memory import BaseMessage, BaseMemory, UnconstrainedMemory
from bee_agent.tools import Tool
from bee_agent.utils import BeeLogger, BeeEventEmitter, MessageEvent, Role


logger = BeeLogger(__name__)
event_emitter = BeeEventEmitter()
T = TypeVar("T")


class BaseAgent(ABC):
    llm: Optional[BaseLLM] = None
    tools: List[Tool]
    memory: BaseMemory

    max_iterations = 20

    @property
    def __is_loop_running(self) -> bool:
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

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
        system_prompt_data = {}

        if len(self.tools):
            tool_box = [tool.prompt_data() for tool in self.tools]
            system_prompt_data = {
                "tools": tool_box,
                "tools_length": len(tool_box),
                "instructions": "You are a helpful assistant",
            }

        await self.memory.add(
            BaseMessage.of(
                {
                    "role": Role.SYSTEM,
                    "text": SystemPromptTemplate.render(system_prompt_data),
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
            user_prompt_text = UserPromptTemplate.render(
                {"input": prompt.get("prompt", "")}
            )

            event_emitter.emit(
                MessageEvent(source=Role.USER, message=prompt.get("prompt", ""))
            )

            await self.memory.add(
                BaseMessage.of(
                    {
                        "role": Role.USER,
                        "text": user_prompt_text,
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

            assistant_prompt_text = AssistantPromptTemplate.render(
                {
                    "thought": output_parts.get("Thought"),
                    "tool_name": output_parts.get("Function Name"),
                    "tool_input": tool_input,
                    "tool_output": tool_response,
                }
            )

            event_emitter.emit_many(
                [
                    MessageEvent(
                        source="Agent",
                        state="thought",
                        message=output_parts.get("Thought"),
                    ),
                    MessageEvent(
                        source="Agent",
                        state="tool_name",
                        message=output_parts.get("Function Name"),
                    ),
                    MessageEvent(
                        source="Agent",
                        state="tool_input",
                        message=output_parts.get("Function Input"),
                    ),
                ]
            )

            await self.memory.add(
                BaseMessage.of(
                    {
                        "role": Role.ASSISTANT,
                        "text": assistant_prompt_text,
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
                event_emitter.emit(
                    MessageEvent(
                        source="Agent", message=final_answer, state="final_answer"
                    )
                )

                await self.memory.add(
                    BaseMessage.of(
                        {
                            "role": Role.ASSISTANT,
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

        if self.__is_loop_running:
            # Create a separate thread so we can block before returning
            with ThreadPoolExecutor(1) as pool:
                pool.submit(lambda: asyncio.run(runner(self, _prompt))).result()
        else:
            # No event loop
            asyncio.run(runner(self, _prompt))


class BeeAgent(BaseAgent):
    def _run(self, prompt: Prompt, options: Optional[Dict[str, Any]] = None):
        if self.llm:
            return self.llm.generate(self.memory.messages, options)
