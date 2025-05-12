#! /usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from src.agents.agent import Agent
from opik.evaluation.metrics import Hallucination, AnswerRelevance

class MetricsAgent(Agent):
    """
    Generic agent that takes any two inputs (prompt & response)
    and returns the original response plus Opik judge metrics.
    """

    def __init__(self, agent: dict) -> None:
        super().__init__(agent)
        # you could also read self.agent_config.get("metrics") here 
        # to make it configurable via YAML
        self._metrics = {
            "relevance": AnswerRelevance(),
            "hallucination": Hallucination()
        }

    async def run(self, prompt: str, response: str):
        """
        Args:
          prompt:   the original input (e.g. location, user question)
          response: the LLM’s output

        Returns:
          dict with:
            - response: the original response
            - relevance: float score ∈ [0,1]
            - hallucination: float score ∈ [0,1]
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