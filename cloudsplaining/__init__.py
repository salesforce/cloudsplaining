# pylint: disable=missing-module-docstring
import logging
import sys

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler

# logging.getLogger(__name__).addHandler(NullHandler())
# Uncomment to get the full debug logs.
# 2020-10-06 10:04:17,200 - root - DEBUG - Leveraging the bundled IAM Definition.
# Need to figure out how to get click_log to do this for me.
from typing import Union, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# logging.getLogger().addHandler(NullHandler())

name = "cloudsplaining"  # pylint: disable=invalid-name


def change_log_level(log_level: Union[int, str]) -> None:
    """"Change log level of module logger"""
    logger.setLevel(log_level)


# pylint: disable=redefined-outer-name
def set_stream_logger(
    name: str = "cloudsplaining",
    level: int = logging.DEBUG,
    format_string: Optional[str] = None,
) -> None:
    """
    Add a stream handler for the given name and level to the logging module.
    By default, this logs all cloudsplaining messages to ``stdout``.
        >>> import cloudsplaining
        >>> cloudsplaining.set_stream_logger('cloudsplaining.scan', logging.INFO)
    :type name: string
    :param name: Log name
    :type level: int
    :param level: Logging level, e.g. ``logging.INFO``
    :type format_string: str
    :param format_string: Log message format
    """
    # remove existing handlers. since NullHandler is added by default
    handlers = logging.getLogger(name).handlers
    for handler in handlers:  # pylint: disable=redefined-outer-name
        logging.getLogger(name).removeHandler(handler)
    if format_string is None:
        format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
    logger = logging.getLogger(name)  # pylint: disable=redefined-outer-name
    logger.setLevel(level)
    handler = logging.StreamHandler()  # pylint: disable=redefined-outer-name
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)  # pylint: disable=redefined-outer-name
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def set_log_level(verbose: int) -> None:
    """
    Set Log Level based on click's count argument.

    Default log level to critical; otherwise, set to: warning for -v, info for -vv, debug for -vvv

    :param verbose: integer for verbosity count.
    :return:
    """
    if verbose == 1:
        set_stream_logger(level=getattr(logging, "WARNING"))
    elif verbose == 2:
        set_stream_logger(level=getattr(logging, "INFO"))
    elif verbose >= 3:
        set_stream_logger(level=getattr(logging, "DEBUG"))
    else:
        set_stream_logger(level=getattr(logging, "CRITICAL"))
