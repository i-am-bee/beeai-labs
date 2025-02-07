# SPDX-License-Identifier: Apache-2.0

import os
import aiofiles
from typing import TypeVar, Generic, Dict, Any
from dataclasses import dataclass
from functools import wraps

from .base_cache import BaseCache
from .sliding_cache import SlidingCache
from .serializer import Serializer

T = TypeVar("T")


def cache():
    """Decorator to cache method results."""

    def decorator(func):
        cache_key = f"_cache_{func.__name__}"

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, cache_key):
                setattr(self, cache_key, await func(self, *args, **kwargs))
            return getattr(self, cache_key)

        wrapper.clear_cache = lambda self: (
            delattr(self, cache_key) if hasattr(self, cache_key) else None
        )
        return wrapper

    return decorator


@dataclass
class Input:
    """Input configuration for FileCache."""

    full_path: str


class FileCache(BaseCache[T], Generic[T]):
    """File-based cache implementation."""

    def __init__(self, input_config: Input):
        """Initialize the FileCache with the given input configuration."""
        super().__init__()
        self._input = input_config
        self._register()

    @classmethod
    def _register(cls) -> None:
        """Register the cache class."""
        Serializer.register(
            cls,
            {
                "to_plain": lambda x: x.create_snapshot(),
                "from_plain": lambda x: cls.from_snapshot(x),
            },
        )

    @property
    def source(self) -> str:
        """Get the source file path."""
        return self._input.full_path

    @classmethod
    async def from_provider(
        cls, provider: BaseCache[T], input_config: Input
    ) -> "FileCache[T]":
        """Create a new FileCache instance from a provider."""
        async with aiofiles.open(input_config.full_path, "w") as f:
            serialized = await provider.serialize()  # Await the serialization
            await f.write(serialized)
        return cls(input_config)

    @cache()
    async def _get_provider(self) -> BaseCache[T]:
        """Get the cache provider instance."""
        try:
            exists = os.path.isfile(self._input.full_path)
        except Exception:
            exists = False

        if exists:
            async with aiofiles.open(self._input.full_path, "r") as f:
                serialized = await f.read()

            deserialized = await Serializer.deserialize(serialized)
            target = deserialized["target"]
            snapshot = deserialized["snapshot"]

            Target = Serializer.get_factory(target).ref
            instance = Target.from_snapshot(snapshot)

            if not isinstance(instance, BaseCache):
                raise TypeError(
                    "Provided file does not serialize any instance of BaseCache class."
                )

            return instance
        else:
            return SlidingCache(size=float("inf"), ttl=float("inf"))

    async def reload(self) -> None:
        """Reload the cache from the file."""
        self._get_provider.clear_cache(self)
        await self._get_provider()

    async def _save(self) -> None:
        """Save the cache to the file."""
        provider = await self._get_provider()
        async with aiofiles.open(self._input.full_path, "w") as f:
            serialized = await provider.serialize()  # Await the serialization
            await f.write(serialized)

    async def size(self) -> int:
        """Get the number of items in the cache."""
        provider = await self._get_provider()
        return await provider.size()

    async def set(self, key: str, value: T) -> None:
        """Set a value in the cache."""
        provider = await self._get_provider()
        await provider.set(key, value)
        try:
            await provider.get(key)
        finally:
            await self._save()

    async def get(self, key: str) -> T:
        """Get a value from the cache."""
        provider = await self._get_provider()
        return await provider.get(key)

    async def has(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        provider = await self._get_provider()
        return await provider.has(key)

    async def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        provider = await self._get_provider()
        result = await provider.delete(key)
        await self._save()
        return result

    async def clear(self) -> None:
        """Clear all items from the cache."""
        provider = await self._get_provider()
        await provider.clear()
        await self._save()

    async def create_snapshot(self) -> Dict[str, Any]:
        """Create a serializable snapshot of the current state."""
        return {
            "input": {"full_path": self._input.full_path},
            "provider": await self._get_provider(),
        }

    def load_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from a snapshot."""
        for key, value in snapshot.items():
            setattr(self, key, value)

    @classmethod
    def from_snapshot(cls, snapshot: Dict[str, Any]) -> "FileCache[T]":
        """Create an instance from a snapshot."""
        instance = cls(Input(full_path=snapshot["input"]["full_path"]))
        instance.load_snapshot(snapshot)
        return instance


if __name__ == "__main__":
    import asyncio
    import tempfile
    import os
    from pathlib import Path

    async def test_file_cache():
        try:
            # Create a temporary directory for our test cache files
            with tempfile.TemporaryDirectory() as temp_dir:
                cache_file = Path(temp_dir) / "test_cache.json"

                print("\n1. Creating and Testing Basic Cache Operations:")
                # Initialize the cache
                cache = FileCache[str](Input(str(cache_file)))

                # Test basic operations
                print("Setting values in cache...")
                await cache.set("key1", "value1")
                await cache.set("key2", "value2")

                # Verify values
                value1 = await cache.get("key1")
                value2 = await cache.get("key2")
                print(f"Retrieved values: key1={value1}, key2={value2}")

                # Check existence
                has_key = await cache.has("key1")
                print(f"Has key1: {has_key}")

                # Get cache size
                size = await cache.size()
                print(f"Cache size: {size}")

                print("\n2. Testing File Persistence:")
                # Verify file was created
                print(f"Cache file exists: {cache_file.exists()}")
                print(f"Cache file size: {cache_file.stat().st_size} bytes")

                print("\n3. Testing Delete Operation:")
                # Delete a key
                deleted = await cache.delete("key2")
                print(f"Deleted key2: {deleted}")
                has_key2 = await cache.has("key2")
                print(f"Has key2 after delete: {has_key2}")

                print("\n4. Testing Clear Operation:")
                # Clear the cache
                await cache.clear()
                size = await cache.size()
                print(f"Cache size after clear: {size}")

                print("\n5. Testing Provider Creation:")
                # Test with non-existent file
                new_file = Path(temp_dir) / "new_cache.json"
                new_cache = FileCache[str](Input(str(new_file)))
                await new_cache.set("test_key", "test_value")
                print(f"Created new cache file: {new_file.exists()}")

        except Exception as e:
            print(f"Error during test: {str(e)}")

    # Run the test
    asyncio.run(test_file_cache())
