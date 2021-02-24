# pylint: disable=missing-module-docstring
import logging
import sys

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler

# logging.getLogger(__name__).addHandler(NullHandler())
# Uncomment to get the full debug logs.
# 2020-10-06 10:04:17,200 - root - DEBUG - Leveraging the bundled IAM Definition.
# Need to figure out how to get click_log to do this for me.
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# logging.getLogger().addHandler(NullHandler())

name = "cloudsplaining"  # pylint: disable=invalid-name


def change_log_level(log_level):
    """"Change log level of module logger"""
    logger.setLevel(log_level)
