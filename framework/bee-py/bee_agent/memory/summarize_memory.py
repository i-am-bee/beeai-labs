# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Dict, Iterable, TYPE_CHECKING

from .base_memory import BaseMemory
from .message import BaseMessage
from bee_agent.utils import Role


if TYPE_CHECKING:
    from bee_agent.llms import BaseLLM


class SummarizeMemory(BaseMemory):
    """Memory implementation that summarizes conversations."""

    def __init__(self, llm: "BaseLLM"):
        self._messages: List[BaseMessage] = []
        self.llm = llm

    @property
    def messages(self) -> List[BaseMessage]:
        return self._messages

    async def add(self, message: BaseMessage, index: Optional[int] = None) -> None:
        """Add a message and trigger summarization if needed."""
        messages_to_summarize = self._messages + [message]
        summary = self._summarize_messages(messages_to_summarize)

        self._messages = [BaseMessage(role=Role.SYSTEM, text=summary)]

    async def add_many(
        self, messages: Iterable[BaseMessage], start: Optional[int] = None
    ) -> None:
        """Add multiple messages and summarize."""
        messages_to_summarize = self._messages + list(messages)
        summary = self._summarize_messages(messages_to_summarize)

        self._messages = [BaseMessage(role=Role.SYSTEM, text=summary)]

    def _summarize_messages(self, messages: List[BaseMessage]) -> str:
        """Summarize a list of messages using the LLM."""
        if not messages:
            return ""

        prompt = {
            "prompt": """Summarize the following conversation. Be concise but include all key information.

Previous messages:
{}

Summary:""".format(
                "\n".join([f"{msg.role}: {msg.text}" for msg in messages])
            )
        }

        # Generate is synchronous, not async
        response = self.llm.generate(prompt)
        return response.output.response

    async def delete(self, message: BaseMessage) -> bool:
        """Delete a message from memory."""
        try:
            self._messages.remove(message)
            return True
        except ValueError:
            return False

    def reset(self) -> None:
        """Clear all messages from memory."""
        self._messages.clear()

    def create_snapshot(self) -> Dict:
        """Create a serializable snapshot of current state."""
        return {"messages": self._messages.copy()}

    def load_snapshot(self, state: Dict) -> None:
        """Restore state from a snapshot."""
        self._messages = state["messages"].copy()
