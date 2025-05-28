#!/usr/bin/env python3

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
import time
import dotenv
import pycron

from src.mermaid import Mermaid
from src.step import Step, eval_expression
from src.agents.agent import save_agent, restore_agent
from src.agents.agent_factory import AgentFramework, AgentFactory

dotenv.load_dotenv()


def get_agent_class(framework: str, mode="local") -> type:
    """
    Returns the agent class based on the provided framework.

    Args:
        framework (str): The framework to get the agent class for.

    Returns:
        type: The agent class based on the provided framework.
    """
    if os.getenv("DRY_RUN"):
        from src.agents.mock_agent import MockAgent
        return MockAgent
    return AgentFactory.create_agent(framework, mode)


def create_agents(agent_defs):
    """
    Creates agents based on the provided definitions.

    Args:
        agent_defs (list): A list of agent definitions. Each definition is a dictionary with the following keys:
            "spec": A dictionary containing the specification of the agent.
                "framework": The framework of the agent (e.g., "bee").

    Returns:
        None
    """
    for agent_def in agent_defs:
        agent_def["spec"]["framework"] = agent_def["spec"].get(
            "framework", AgentFramework.BEEAI
        )
        cls = get_agent_class(
            agent_def["spec"]["framework"],
            agent_def["spec"].get("mode")
        )
        save_agent(cls(agent_def))


class Workflow:
    """Execute a sequential Maestro workflow."""
    """Execute sequential workflow.

    Args:
        agent_defs (dict): Dictionary of agent definitions.
        workflow (dict): Workflow definition.

    Attributes:
        agents (dict): Dictionary of agents.
        steps (dict): Dictionary of steps.
    """
    def __init__(self, agent_defs=None, workflow=None):
        """Execute sequential workflow.
        input:
            agents: array of agent definitions, saved agent names, or None (agents in workflow must be pre-created)
            workflow: workflow definition
        """
        self.agents = {}
        self.steps = {}
        self.agent_defs = agent_defs or []
        self.workflow = workflow or {}

    def to_mermaid(self, kind="sequenceDiagram", orientation="TD") -> str:
        wf = self.workflow[0] if isinstance(self.workflow, list) else self.workflow
        return Mermaid(wf, kind, orientation).to_markdown()

    async def run(self, prompt=''):
        if prompt:
            self.workflow['spec']['template']['prompt'] = prompt

        self.create_or_restore_agents(self.agent_defs, self.workflow)

        tpl = self.workflow['spec']['template']
        if tpl.get('event'):
            output = await self._condition()
            return await self.process_event(output)
        else:
            return await self._condition()

    def create_or_restore_agents(self, agent_defs, workflow):
        if agent_defs:
            for agent_def in agent_defs:
                agent_def["spec"]["framework"] = agent_def["spec"].get(
                    "framework", AgentFramework.BEEAI
                )
                cls = get_agent_class(
                    agent_def["spec"]["framework"],
                    agent_def["spec"].get("mode")
                )
                self.agents[agent_def["metadata"]["name"]] = cls(agent_def)
        else:
            for name in workflow["spec"]["template"]["agents"]:
                self.agents[name] = restore_agent(name)

    def find_index(self, steps, name):
        for idx, step in enumerate(steps):
            if step.get("name") == name:
                return idx
        raise ValueError(f"Step {name} not found")

    async def _condition(self):
        prompt = self.workflow["spec"]["template"]["prompt"]
        steps = self.workflow["spec"]["template"]["steps"]
        return await self._process_steps(steps, steps[0]["name"], prompt)

    async def _process_steps(self, steps, start_step, initial_prompt):
        """
        Core sequential executor with support for:
          - multi-arg inputs via `step["inputs"]`
          - optional per-step context via `step["context"]`
        """
        self._context = {"prompt": initial_prompt}

        for step_def in steps:
            if isinstance(step_def.get("agent"), str):
                agent_obj = self.agents.get(step_def["agent"])
                if not agent_obj:
                    raise RuntimeError(
                        f"Agent '{step_def['agent']}' not found for step '{step_def['name']}'"
                    )
                step_def["agent"] = agent_obj
            self.steps[step_def["name"]] = Step(step_def)

        current_step = start_step
        step_results = {}

        while True:
            step_def = next(s for s in steps if s["name"] == current_step)
            if "inputs" in step_def:
                args = []
                for inp in step_def["inputs"]:
                    var = inp["from"]
                    if var not in self._context:
                        raise RuntimeError(
                            f"Step '{current_step}' asked for input '{var}', but it does not exist"
                        )
                    args.append(self._context[var])
            else:
                args = [ self._context["prompt"] ]

            if "context" in step_def:
                ctx = []
                for item in step_def["context"]:
                    if isinstance(item, str):
                        ctx.append(item)
                    else:
                        name = item["from"]
                        if name not in self._context:
                            raise RuntimeError(
                                f"Step '{current_step}' asked for context '{name}', but it does not exist"
                            )
                        ctx.append(self._context[name])
            else:
                ctx = None
            if ctx is None:
                result = await self.steps[current_step].run(*args)
            else:
                result = await self.steps[current_step].run(*args, context=ctx)

            if "prompt" not in result:
                raise RuntimeError(
                    f"Step '{current_step}' did not return a 'prompt' key"
                )
            new_prompt = result["prompt"]
            self._context[current_step] = new_prompt
            self._context["prompt"] = new_prompt

            if result.get("next"):
                current_step = result["next"]
            else:
                idx = self.find_index(steps, current_step)
                if idx == len(steps) - 1:
                    break
                current_step = steps[idx + 1]["name"]

        step_results["final_prompt"] = self._context["prompt"]
        return step_results

    async def process_event(self, prompt):
        tpl = self.workflow['spec']['template']
        cron = tpl['event']['cron']
        agent_name = tpl['event'].get('agent')
        step_names = tpl['event'].get('steps')
        exit_expr = tpl['event'].get('exit')

        first_run = True
        while True:
            if pycron.is_now(cron):
                if first_run and agent_name:
                    prompt = await self.agents[agent_name].run(prompt)
                if step_names:
                    event_steps = [self.get_step(n) for n in step_names]
                    out = await self._process_steps(event_steps, step_names[0], prompt)
                    prompt = out.get("final_prompt", prompt)
                first_run = False

            if eval_expression(exit_expr, prompt):
                break
            time.sleep(30)

        return prompt

    def get_step(self, step_name):
        for s in self.workflow['spec']['template']['steps']:
            if s.get("name") == step_name:
                return s
        raise ValueError(f"Step {step_name} not found")
