# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import List, Optional, Iterable, Any, TYPE_CHECKING

from .message import BaseMessage

if TYPE_CHECKING:
    from .readonly_memory import ReadOnlyMemory


class BaseMemory(ABC):
    """Abstract base class for all memory implementations."""

    @property
    @abstractmethod
    def messages(self) -> List[BaseMessage]:
        """Return list of stored messages."""
        pass

    @abstractmethod
    async def add(self, message: BaseMessage, index: Optional[int] = None) -> None:
        """Add a message to memory."""
        pass

    @abstractmethod
    async def delete(self, message: BaseMessage) -> bool:
        """Delete a message from memory."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Clear all messages from memory."""
        pass

    async def add_many(
        self, messages: Iterable[BaseMessage], start: Optional[int] = None
    ) -> None:
        """Add multiple messages to memory."""
        counter = 0
        for msg in messages:
            index = None if start is None else start + counter
            await self.add(msg, index)
            counter += 1

    async def delete_many(self, messages: Iterable[BaseMessage]) -> None:
        """Delete multiple messages from memory."""
        for msg in messages:
            await self.delete(msg)

    async def splice(
        self, start: int, delete_count: int, *items: BaseMessage
    ) -> List[BaseMessage]:
        """Remove and insert messages at a specific position."""
        total = len(self.messages)
        start = max(total + start, 0) if start < 0 else start
        delete_count = min(delete_count, total - start)

        deleted_items = self.messages[start : start + delete_count]
        await self.delete_many(deleted_items)
        await self.add_many(items, start)

        return deleted_items

    def is_empty(self) -> bool:
        """Check if memory is empty."""
        return len(self.messages) == 0

    def __iter__(self):
        return iter(self.messages)

    @abstractmethod
    def create_snapshot(self) -> Any:
        """Create a serializable snapshot of current state."""
        pass

    @abstractmethod
    def load_snapshot(self, state: Any) -> None:
        """Restore state from a snapshot."""
        pass

    def as_read_only(self) -> "ReadOnlyMemory":
        """Return a read-only view of this memory."""
        from .readonly_memory import (
            ReadOnlyMemory,
        )  # Import here to avoid circular import

        return ReadOnlyMemory(self)
