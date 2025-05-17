#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os
from src.agents.agent import Agent
from opik.evaluation.metrics import Hallucination, AnswerRelevance

class MetricsAgent(Agent):
    """
    Generic agent that takes any two inputs (prompt & response)
    and returns the original response plus Opik judge metrics.
    """

    def __init__(self, agent: dict) -> None:
        super().__init__(agent)
        spec_model = agent["spec"]["model"]
        # need to set the model name to the one used by OpenAI to bypass LiteLLM error
        if "/" not in spec_model:
            spec_model = f"openai/{spec_model}"
        self._metrics = {
            "relevance": AnswerRelevance(model=spec_model),
            "hallucination": Hallucination(model=spec_model)
        }

    async def run(self, prompt: str, response: str):
        """
        Args:
          prompt:   the original input (e.g. location, user question)
          response: the LLM’s output

        Returns:
          dict with:
            - response: the original response
            - relevance: ScoreResult
            - hallucination: ScoreResult
        """
        scores = {}
        for name, metric in self._metrics.items():
            scores[name] = metric.score(
                input=prompt,
                output=response,
                context=[f"Context: {prompt}"]
            )

        return {
            "response": response,
            **scores
        }