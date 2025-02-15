import logging
import sys
from collections.abc import Iterable
from typing import Any, List


def init_logging(debug: bool = False) -> logging.Logger:
    logging_level: int = logging.DEBUG if debug else logging.INFO

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)

    # Create handlers for stdout and stderr
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)

    # Set levels for handlers
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    format_str = "%(asctime)s - %(name)s\n%(levelname)s - %(message)s"
    stdout_formatter = logging.Formatter(format_str)
    stderr_formatter = logging.Formatter(format_str)

    stdout_handler.setFormatter(stdout_formatter)
    stderr_handler.setFormatter(stderr_formatter)

    # Add handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    # Filter out ERROR messages from stdout
    stdout_handler.addFilter(lambda record: record.levelno <= logging.WARNING)

    return logger


def flat_list(items: Any) -> List[Any]:
    result: List[Any] = []
    if not isinstance(items, (str, dict)) and isinstance(items, Iterable):
        for item in items:
            if isinstance(item, (list, set)):
                result.extend(flat_list(item))
            else:
                result.append(item)
    elif isinstance(items, dict):
        for k, v in items.items():  # pyright: ignore
            result.append(f"{k}={v}")
    else:
        result.append(items)
    return result
