"""Pytest configuration for asyncio testing."""

import pytest


def pytest_addoption(parser):
    """Add pytest command line options."""
    parser.addini("asyncio_mode", "default mode for async fixtures", default="strict")
