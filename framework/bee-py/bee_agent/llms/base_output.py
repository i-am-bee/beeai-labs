# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence
from bee_agent.memory.message import BaseMessage


@dataclass
class BaseLLMOutput:
    """Base class for LLM outputs."""

    pass


class BaseChatLLMOutput(BaseLLMOutput, ABC):
    """Abstract base class for chat LLM outputs."""

    @property
    @abstractmethod
    def messages(self) -> Sequence[BaseMessage]:
        """Get the messages from the LLM output.
        Returns:
            Sequence[BaseMessage]: A read-only sequence of messages
        """
        raise NotImplementedError
