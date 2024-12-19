# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional


class MemoryError(Exception):
    """Base class for memory-related exceptions."""

    pass


class MemoryFatalError(MemoryError):
    """Fatal memory errors that cannot be recovered from."""

    def __init__(
        self, message: str, errors: Optional[List[Exception]] = None, **kwargs
    ):
        super().__init__(message)
        self.errors = errors or []
        self.is_fatal = kwargs.get("is_fatal", True)
        self.is_retryable = kwargs.get("is_retryable", False)
