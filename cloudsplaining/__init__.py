# pylint: disable=missing-module-docstring
import logging
# import sys
# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
# Uncomment to get the full debug logs.
# 2020-10-06 10:04:17,200 - root - DEBUG - Leveraging the bundled IAM Definition.
# Need to figure out how to get click_log to do this for me.
# root = logging.getLogger()
# root.setLevel(logging.DEBUG)
# handler = logging.StreamHandler(sys.stdout)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# root.addHandler(handler)

name = "cloudsplaining"  # pylint: disable=invalid-name
