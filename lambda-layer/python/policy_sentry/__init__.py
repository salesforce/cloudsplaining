# pylint: disable=missing-module-docstring
from __future__ import annotations

import logging
from logging import NullHandler

# Set default handler when policy_sentry is used as library to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(NullHandler())


def set_stream_logger(
    name: str = "policy_sentry",
    level: int = logging.DEBUG,
    format_string: str | None = None,
) -> None:
    """
    Add a stream handler for the given name and level to the logging module.
    By default, this logs all policy_sentry messages to ``stdout``.
        >>> import policy_sentry
        >>> policy_sentry.set_stream_logger('policy_sentry.querying', logging.INFO)
    :type name: string
    :param name: Log name
    :type level: int
    :param level: Logging level, e.g. ``logging.INFO``
    :type format_string: str
    :param format_string: Log message format
    """
    # remove existing handlers. since NullHandler is added by default
    handlers = logging.getLogger(name).handlers
    for handler in handlers:
        logging.getLogger(name).removeHandler(handler)
    if format_string is None:
        format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
