# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Union


RoleType = Union[str, None]  # Equivalent to TypeScript's string type for roles


# Basic Role class
class Role(str, Enum):
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"
    USER: str = "user"

    @classmethod
    def values(cls) -> set[str]:
        return {
            value
            for key, value in vars(cls).items()
            if not key.startswith("_") and isinstance(value, str)
        }
