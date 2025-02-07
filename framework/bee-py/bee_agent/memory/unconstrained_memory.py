# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Dict
from copy import copy
from .base_memory import BaseMemory
from .message import BaseMessage


class UnconstrainedMemory(BaseMemory):
    """Simple memory implementation with no constraints."""

    def __init__(self):
        self._messages: List[BaseMessage] = []

    @property
    def messages(self) -> List[BaseMessage]:
        return self._messages

    async def add(self, message: BaseMessage, index: Optional[int] = None) -> None:
        index = (
            len(self._messages)
            if index is None
            else max(0, min(index, len(self._messages)))
        )
        self._messages.insert(index, message)

    async def delete(self, message: BaseMessage) -> bool:
        try:
            self._messages.remove(message)
            return True
        except ValueError:
            return False

    def reset(self) -> None:
        self._messages.clear()

    def create_snapshot(self) -> Dict:
        return {"messages": copy(self._messages)}

    def load_snapshot(self, state: Dict) -> None:
        self._messages = copy(state["messages"])
