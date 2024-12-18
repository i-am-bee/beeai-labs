from dataclasses import dataclass
from typing import Sequence, List
from bee_agent.memory.message import BaseMessage, Role
from .base_output import BaseChatLLMOutput


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
