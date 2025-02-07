# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar, Optional, ClassVar
from copy import deepcopy

T = TypeVar("T")


class Serializable(ABC):
    """Base class for all serializable objects."""

    _registered_classes: ClassVar[Dict[str, Type["Serializable"]]] = {}

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses when they're created."""
        super().__init_subclass__(**kwargs)
        cls._registered_classes[cls.__name__] = cls

    @classmethod
    def register(cls, aliases: Optional[list[str]] = None) -> None:
        """Register the class and any aliases for serialization."""
        cls._registered_classes[cls.__name__] = cls
        if aliases:
            for alias in aliases:
                if (
                    alias in cls._registered_classes
                    and cls._registered_classes[alias] != cls
                ):
                    raise ValueError(
                        f"Alias '{alias}' already registered to a different class"
                    )
                cls._registered_classes[alias] = cls

    @classmethod
    def from_serialized(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from serialized data."""
        instance = cls.__new__(cls)
        Serializable.__init__(instance)
        instance.load_snapshot(data)
        return instance

    @classmethod
    def from_snapshot(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from a snapshot."""
        instance = cls.__new__(cls)
        Serializable.__init__(instance)
        instance.load_snapshot(data)
        return instance

    def serialize(self) -> Dict[str, Any]:
        """Serialize the object to a dictionary."""
        return {"__class": self.__class__.__name__, "__value": self.create_snapshot()}

    @abstractmethod
    def create_snapshot(self) -> Dict[str, Any]:
        """Create a serializable snapshot of the object's state."""
        raise NotImplementedError

    @abstractmethod
    def load_snapshot(self, state: Dict[str, Any]) -> None:
        """Load object state from a snapshot."""
        raise NotImplementedError

    def clone(self: T) -> T:
        """Create a deep copy of the object."""
        snapshot = self.create_snapshot()
        return self.__class__.from_snapshot(deepcopy(snapshot))


# Example of how to use the base class:
class ExampleSerializable(Serializable):
    def __init__(self, data: str):
        super().__init__()
        self.data = data

    @classmethod
    def register(cls, aliases: Optional[list[str]] = None) -> None:
        """Register with custom aliases."""
        super().register(aliases)

    def create_snapshot(self) -> Dict[str, Any]:
        return {"data": self.data}

    def load_snapshot(self, state: Dict[str, Any]) -> None:
        self.data = state["data"]


# Usage example:
if __name__ == "__main__":
    # Register the class with an alias
    ExampleSerializable.register(aliases=["Example", "ExampleClass"])

    # Create and serialize an instance
    obj = ExampleSerializable("test data")
    serialized = obj.serialize()

    # Create new instance from serialized data
    new_obj = ExampleSerializable.from_serialized(serialized["__value"])

    # Create a clone
    cloned = obj.clone()
