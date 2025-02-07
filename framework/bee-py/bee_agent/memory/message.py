# SPDX-License-Identifier: Apache-2.0

from abc import ABC
from typing import Dict, Any, Optional, Type
from datetime import datetime
from copy import deepcopy
from dataclasses import dataclass

from bee_agent.utils import Role, RoleType


# Basic Serialization implementation
class Serializable(ABC):
    """Base class for serializable objects."""

    @classmethod
    def register(cls):
        # Registration logic would go here
        pass

    def serialize(self) -> Dict[str, Any]:
        """Serialize the object to a dictionary."""
        return self.create_snapshot()

    @classmethod
    def from_serialized(
        cls: Type["Serializable"], data: Dict[str, Any]
    ) -> "Serializable":
        """Create an instance from serialized data."""
        instance = cls.__new__(cls)
        instance.load_snapshot(data)
        return instance


# TypedDict equivalent for BaseMessageMeta
class BaseMessageMeta(Dict[str, Any]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at: Optional[datetime] = kwargs.get("created_at")


# Equivalent to TypeScript's BaseMessageInput interface
@dataclass
class BaseMessageInput:
    role: RoleType
    text: str
    meta: Optional[BaseMessageMeta] = None


@dataclass
class BaseMessage(Serializable):
    role: Role
    text: str
    meta: Optional[BaseMessageMeta] = None

    @classmethod
    def of(cls, data: Dict[str, str]) -> "BaseMessage":
        return cls(role=data["role"], text=data["text"])

    def __hash__(self):
        """Make BaseMessage hashable by using role and text."""
        return hash((self.role, self.text))

    def __eq__(self, other):
        """Define equality for BaseMessage."""
        if not isinstance(other, BaseMessage):
            return False
        return (
            self.role == other.role
            and self.text == other.text
            and self.meta == other.meta
        )

    def create_snapshot(self) -> Dict[str, Any]:
        """Create a serializable snapshot of the message."""
        return {"role": self.role, "text": self.text, "meta": deepcopy(self.meta)}

    def load_snapshot(self, state: Dict[str, Any]) -> None:
        """Load message state from a snapshot."""
        for key, value in state.items():
            setattr(self, key, value)
        return self

    @classmethod
    def register(cls):
        """Register the class for serialization."""
        super().register()


# Example usage:
if __name__ == "__main__":
    # Create a message using the of() factory method
    message = BaseMessage.of(
        {
            "role": Role.USER,
            "text": "Hello, how are you?",
            "meta": {"created_at": datetime.now()},
        }
    )
    message = BaseMessage.of(
        {
            "role": Role.USER,
            "text": "Hello, how are you?",
            "meta": {"created_at": datetime.now()},
        }
    )
    print(message)
    # Serialize the message
    serialized = message.serialize()
    print(serialized)
    # Create a new message from serialized data
    deserialized = BaseMessage.from_serialized(serialized)
