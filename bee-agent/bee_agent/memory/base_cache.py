from abc import ABC, abstractmethod
from typing import Dict, Generic, Any, TypeVar


T = TypeVar("T")


class BaseCache(ABC, Generic[T]):
    """Abstract base class for all Cache implementations."""

    def __init__(self):
        """Initialize the cache with an empty elements dictionary."""
        self._elements: Dict[str, Any] = {}
        self._enabled: bool = True

    @property
    def enabled(self) -> bool:
        """
        Property that indicates if the cache is enabled.

        Returns:
            bool: True if cache is enabled, False otherwise
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Set the enabled status of the cache.

        Args:
            value (bool): The new enabled status
        """
        self._enabled = value

    @property
    def elements(self) -> Dict[str, Any]:
        """
        Property that provides access to the internal elements dictionary.

        Returns:
            Dict[str, Any]: The cache elements
        """
        return self._elements

    async def serialize(self) -> str:
        """Serialize the cache state."""
        snapshot = await self.create_snapshot()
        from .serializer import Serializer  # Import here to avoid circular imports

        return await Serializer.serialize(
            {
                "target": {
                    "module": self.__class__.__module__,
                    "name": self.__class__.__name__,
                },
                "snapshot": snapshot,
            }
        )

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """Add a element in the cache."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get a element in the cache."""
        pass

    @abstractmethod
    async def has(self, key: str) -> bool:
        """Get a element in the cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a element in the Cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all the Cache content."""
        pass

    def size(self) -> int:
        """Clear all the Cache content."""
        return len(self.elements)

    def is_empty(self) -> bool:
        """Check if memory is empty."""
        return len(self.elements) == 0

    def __iter__(self):
        return iter(self.elements)

    @abstractmethod
    def create_snapshot(self) -> Any:
        """Create a serializable snapshot of current state."""
        pass

    @abstractmethod
    def load_snapshot(self, state: Any) -> None:
        """Restore state from a snapshot."""
        pass
