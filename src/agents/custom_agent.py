#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import sys
from typing import Any

from src.agents.agent import Agent
from src.agents.slack_agent import SlackAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.prompt_agent import PromptAgent

# adding a custom agent
# 1. add necessary import for the agent
# 2. add the custom agent name and class in the custom_agent map

# using a custom agent
# 1. set "custom" to "framework"
# 2  set the custom agent name to "metadata.labels.custom_agent"

custom_agent = { "slack_agent": SlackAgent, "scoring_agent": ScoringAgent, "prompt_agent": PromptAgent}

class CustomAgent(Agent):
    """
    Proxy that dispatches to the configured custom agent.
    """

    def __init__(self, agent_def: dict) -> None:
        super().__init__(agent_def)
        name = agent_def["metadata"]["labels"].get("custom_agent")
        if not name or name not in custom_agent:
            raise ValueError(f"Unknown custom_agent '{name}'")
        # instantiate the real agent
        self.agent = custom_agent[name](agent_def)

    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Forward any positional or keyword args to the underlying custom agent.
        """
        return await self.agent.run(*args, **kwargs)

    async def run_streaming(self, *args: Any, **kwargs: Any) -> Any:
        """
        Forward any positional or keyword args to the underlying agent’s streaming run.
        """
        return await self.agent.run_streaming(*args, **kwargs)
