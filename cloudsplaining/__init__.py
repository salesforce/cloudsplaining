# pylint: disable=missing-module-docstring
import logging

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
name = "cloudsplaining"  # pylint: disable=invalid-name
