# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar


T = TypeVar("T")


class Tool(Generic[T], ABC):
    options: Dict[str, Any] = {}

    def __init__(self, options={}):
        self.options = options

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def input_schema(self):
        pass

    @abstractmethod
    def _run(self, input, options=None):
        pass

    def prompt_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.input_schema(),
        }

    def run(self, input: T, options=None):
        return self._run(input, options)
