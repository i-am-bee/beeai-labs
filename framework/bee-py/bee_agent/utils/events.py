import asyncio

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, List, Literal, Optional

from pyventus import AsyncIOEventEmitter, EmittableEventType, EventEmitter


@dataclass
class MessageEvent:
    source: Literal["User", "Agent"]
    message: str
    state: Optional[str] = None


class BeeEventEmitter(AsyncIOEventEmitter):
    @property
    def __is_loop_running(self) -> bool:
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Check if there is an active event loop
        is_loop_running: bool = self.__is_loop_running

        # Log the execution context, if debug mode is enabled
        if self._logger.debug_enabled:  # pragma: no cover
            self._logger.debug(
                action="Context:", msg=f"{'Async' if is_loop_running else 'Sync'}"
            )

        if is_loop_running:
            # Create a separate thread
            with ThreadPoolExecutor(1) as pool:
                pool.submit(lambda: asyncio.run(event_emission())).result()

        else:
            # Run the event emission in a blocking manner
            asyncio.run(event_emission())

    def emit_many(self, /, events: List[EmittableEventType], *args: Any, **kwargs: Any):
        for event in events:
            self.emit(event, *args, **kwargs)
