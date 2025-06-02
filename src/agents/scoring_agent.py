#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from dotenv import load_dotenv
load_dotenv()

from src.agents.agent import Agent
from opik.evaluation.metrics import AnswerRelevance, Hallucination

class ScoringAgent(Agent):
    """
    Agent that takes two inputs (prompt & response) plus an optional
    `context` list, prints the scores, and returns only the response.

    Defaults to using Ollama (via Litellm) if no provider prefix is given.
    If you explicitly write "openai/…" or "ollama/…", those will be honored.
    """

    def __init__(self, agent: dict) -> None:
        super().__init__(agent)
        raw_model = agent["spec"]["model"]
        if "/" in raw_model:
            self._litellm_model = raw_model
        else:
            self._litellm_model = f"ollama/{raw_model}"

    async def run(
        self,
        prompt: str,
        response: str,
        context: list[str] | None = None
    ) -> str:
        """
        Args:
          prompt:   the original prompt
          response: the LLM’s output
          context:  optional list of strings to use as gold/context

        Returns:
          the original response (metrics are printed, not returned)
        """

        ctx = context or [prompt]
        rel_res = AnswerRelevance(model=self._litellm_model).score(
            input=prompt,
            output=response,
            context=ctx
        )
        hall_res = Hallucination(model=self._litellm_model).score(
            input=prompt,
            output=response,
            context=ctx
        )

        rel  = getattr(rel_res,  "value", rel_res)
        hall = getattr(hall_res, "value", hall_res)

        metrics_line = f"relevance: {rel:.2f}, hallucination: {hall:.2f}"
        self.print(f"{response}\n[{metrics_line}]")

        return response
