# SPDX-License-Identifier: Apache-2.0

from typing import List, Dict, Optional
from .base_memory import BaseMemory
from .message import BaseMessage


class ReadOnlyMemory(BaseMemory):
    """Read-only wrapper for a memory instance."""

    def __init__(self, source: BaseMemory):
        self.source = source

    @property
    def messages(self) -> List[BaseMessage]:
        return self.source.messages

    async def add(self, message: BaseMessage, index: Optional[int] = None) -> None:
        pass  # No-op for read-only memory

    async def delete(self, message: BaseMessage) -> bool:
        return False  # No-op for read-only memory

    def reset(self) -> None:
        pass  # No-op for read-only memory

    def create_snapshot(self) -> Dict:
        return {"source": self.source}

    def load_snapshot(self, state: Dict) -> None:
        self.source = state["source"]

    def as_read_only(self) -> "ReadOnlyMemory":
        """Return self since already read-only."""
        return self
