from enum import Enum
import logging
import sys

from pyventus import EventHandler, EventLinker

from .config import CONFIG
from .events import MessageEvent
from .roles import Role


_handler: EventHandler = None


class BeeLoggerFormatter:
    def format(self, record: logging.LogRecord):
        if hasattr(record, "is_event_message") and record.is_event_message:
            return logging.Formatter(
                "{asctime} {levelname:<8s} - {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            ).format(record)
        else:
            return logging.Formatter(
                "{asctime} {levelname:<8s} {name} - {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            ).format(record)


class BeeLogger(logging.Logger):

    def __init__(self, name, level=CONFIG.log_level):
        super().__init__(name, level)

        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(BeeLoggerFormatter())

        self.addHandler(console_handler)

        global _handler
        if _handler is None:
            _handler = EventLinker.subscribe(MessageEvent, event_callback=self.log_message_events)

    def log_message_events(self, event: MessageEvent):
        source = str.lower(event.source)
        state = f" ({event.state})" if event.state else ""
        icon = " 👤" if source == str.lower(Role.USER) else " 🤖"
        self.info(f" {str.capitalize(source)}{state}{icon}: {event.message}", extra={"is_event_message": True})
