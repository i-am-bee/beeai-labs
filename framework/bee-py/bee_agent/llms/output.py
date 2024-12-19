# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Sequence, List

from .base_output import BaseChatLLMOutput
from bee_agent.memory.message import BaseMessage
from bee_agent.utils import Role


@dataclass
class ChatOutput:
    """Represents a chat output from Ollama LLM."""

    response: str

    def to_messages(self) -> List[BaseMessage]:
        """Convert the response to a list of messages."""
        return [BaseMessage(role=Role.ASSISTANT, text=self.response)]


@dataclass
class ChatLLMOutput(BaseChatLLMOutput):
    """Concrete implementation of ChatLLMOutput for Ollama."""

    output: ChatOutput

    @property
    def messages(self) -> Sequence[BaseMessage]:
        return self.output.to_messages()
