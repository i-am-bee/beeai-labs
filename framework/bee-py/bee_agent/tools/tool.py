# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Union, Optional
from functools import wraps

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


def bee_tool(
    name: str,
    description: str,
    input_schema: Optional[Dict[str, Any]] = None,
    output: Optional[Union[Dict[str, Any], str]] = None,
):
    def decorator(func):
        class FunctionTool(Tool):
            @property
            def name(self):
                return name

            @property
            def description(self):
                return description

            def input_schema(self):
                return input_schema or {}

            @property
            def output_schema(self):
                if isinstance(output, dict):
                    return output
                elif isinstance(output, str):
                    return {"type": "string", "description": output}
                return {}

            def _run(self, input, options=None):
                return func(input)

            def prompt_data(self):
                data = super().prompt_data()
                if output:
                    data["output"] = self.output_schema
                return data

        return FunctionTool()

    return decorator
