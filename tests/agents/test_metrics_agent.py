#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os
import asyncio
import pytest
import requests

from src.agents.metrics_agent import MetricsAgent
from opik.evaluation.metrics.score_result import ScoreResult

def is_ollama_up(api_base: str) -> bool:
    try:
        return requests.get(f"{api_base}/models", timeout=2).ok
    except:
        return False

@pytest.mark.integration
def test_metrics_agent_with_ollama():
    api_base = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
    api_key  = os.getenv("OPENAI_API_KEY", "ollama")

    if not is_ollama_up(api_base):
        pytest.skip(f"Ollama server not reachable at {api_base}")

    agent_def = {
        "metadata": {"name": "metrics_agent", "labels": {}},
        "spec": {
            "framework":    "custom",
            "model":        "qwen3:latest",
            "description":  "desc",
            "instructions": "instr"
        }
    }

    agent = MetricsAgent(agent=agent_def)
    result = asyncio.run(agent.run("What is the capital of France?", "Paris."))

    assert result["response"] == "Paris."
    rel = result.get("relevance")
    assert isinstance(rel, ScoreResult)
    assert 0.0 <= rel.value <= 1.0

    hall = result.get("hallucination")
    assert isinstance(hall, ScoreResult)
    assert 0.0 <= hall.value <= 1.0
