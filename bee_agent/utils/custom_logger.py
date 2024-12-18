import logging
import sys

from .config import CONFIG


class BeeLogger:
    logger = None

    def __new__(
        self,
        name,
        log_level=None,
    ):
        if log_level is None:
            log_level = CONFIG.log_level

        self.log_level = log_level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_format = logging.Formatter(
            "{asctime} {levelname:<8s} {name} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_format)

        self.logger.addHandler(console_handler)

        return self.logger
