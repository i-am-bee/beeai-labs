# tests/agents/test_metrics_agent.py

import asyncio
import os
import pytest

from src.agents.metrics_agent import MetricsAgent
from opik.evaluation.metrics import AnswerRelevance, Hallucination

# TODO: OPENAIKEY = BEE_API_KEY?
# os.environ["OPENAI_API_KEY"] = os.getenv("BEE_API_KEY")


def test_metrics_agent_run_sync(monkeypatch):
    # 1) stub out the actual calls so they never reach OpenAI
    monkeypatch.setattr(AnswerRelevance, 'score', lambda self, input, output, context: 0.75)
    monkeypatch.setattr(Hallucination, 'score',   lambda self, input, output, context: 0.10)

    # 2) minimal Agent definition your base class needs
    agent_def = {
        "metadata": {"name": "metrics_agent", "labels": {}},
        "spec": {
            "framework": "custom",
            "model": "dummy",
            "description": "desc",
            "instructions": "instr"
        }
    }

    agent = MetricsAgent(agent=agent_def)
    result = asyncio.run(agent.run("Ping?", "Pong!"))

    # 3) verify that our stubs were used
    assert result["response"]       == "Pong!"
    assert result["relevance"]      == pytest.approx(0.75)
    assert result["hallucination"]  == pytest.approx(0.10)
