# tests/agents/test_metrics_agent.py

import asyncio
import os
import pytest

from src.agents.metrics_agent import MetricsAgent
from opik.evaluation.metrics import AnswerRelevance, Hallucination

# TODO: OPENAIKEY = BEE_API_KEY?
# os.environ["OPENAI_API_KEY"] = os.getenv("BEE_API_KEY")


def test_metrics_agent_run_sync(monkeypatch):
    # never reach OpenAI
    monkeypatch.setattr(AnswerRelevance, 'score', lambda self, input, output, context: 0.75)
    monkeypatch.setattr(Hallucination, 'score',   lambda self, input, output, context: 0.10)

    # minimal Agent 
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
    print(result)
   
    # assert result["response"]       == "Pong!"
    # assert result["relevance"]      == pytest.approx(0.75)
    # assert result["hallucination"]  == pytest.approx(0.10)
