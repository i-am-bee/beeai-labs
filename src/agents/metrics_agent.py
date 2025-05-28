#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from dotenv import load_dotenv
load_dotenv()

from src.agents.agent import Agent
from opik.evaluation.metrics import AnswerRelevance, Hallucination

class MetricsAgent(Agent):
    """
    Agent that takes two inputs: 
      1) the original prompt
      2) the response string

    It prints an evaluation string containing relevance & hallucination metrics,
    but returns only the original response downstream.
    """

    def __init__(self, agent: dict) -> None:
        super().__init__(agent)
        spec_model = agent["spec"]["model"]
        # Auto-prefix for OpenAI-compatible routing
        if "/" not in spec_model:
            spec_model = f"openai/{spec_model}"
        self._spec_model = spec_model

    async def run(self, prompt: str, response: str) -> str:
        """
        Args:
          prompt:   the original workflow input
          response: the output string from the previous workflow step

        Returns:
          The original response string (metrics printed, not returned)
        """
        # Compute metrics using the prompt as 'input' and response as 'output'
        rel_result = AnswerRelevance(model=self._spec_model).score(
            input=prompt,
            output=response,
            context=[prompt]
        )
        hall_result = Hallucination(model=self._spec_model).score(
            input=prompt,
            output=response,
            context=[prompt]
        )

        rel = getattr(rel_result, "value", rel_result)
        hall = getattr(hall_result, "value", hall_result)
        metrics_line = f"relevance: {rel:.2f}, hallucination: {hall:.2f}"
        evaluation_str = f"{response}\n[{metrics_line}]"
        self.print(evaluation_str)

        return response
