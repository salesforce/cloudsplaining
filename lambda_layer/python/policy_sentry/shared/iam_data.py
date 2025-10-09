"""Used for loading the IAM data"""

from __future__ import annotations

import functools
import gc
import logging
from typing import Any, cast

import orjson

from policy_sentry.shared.constants import (
    DATASTORE_FILE_PATH,
    POLICY_SENTRY_SCHEMA_VERSION_NAME,
)

logger = logging.getLogger()
# On initialization, load the IAM data
iam_definition_path = DATASTORE_FILE_PATH
logger.debug(f"Leveraging the IAM definition at {iam_definition_path}")


def load_iam_definition() -> dict[str, Any]:
    gc_enabled = gc.isenabled()
    if gc_enabled:
        # https://github.com/msgpack/msgpack-python?tab=readme-ov-file#performance-tips
        gc.disable()

    data: dict[str, Any] = orjson.loads(iam_definition_path.read_bytes())

    if gc_enabled:
        gc.enable()

    return data


iam_definition = load_iam_definition()


@functools.lru_cache(maxsize=1)
def get_iam_definition_schema_version() -> str:
    """
    Returns the schema version of the IAM datastore
    """

    return cast(
        "str",
        iam_definition[POLICY_SENTRY_SCHEMA_VERSION_NAME],
    )


@functools.lru_cache(maxsize=1024)
def get_service_prefix_data(service_prefix: str) -> dict[str, Any]:
    """
    Given an AWS service prefix, return a large dictionary of IAM privilege data for processing and analysis.

    Arguments:
        service_prefix: An AWS service prefix, like s3 or ssm
    Returns:
        List: A list of metadata about that service
    """
    try:
        return cast("dict[str, Any]", iam_definition[service_prefix])
    except:  # noqa: E722
        if service_prefix == "catalog":
            # the resource types "Portfolio" and "Product" have the service name "catalog" in their ARN
            # https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsservicecatalog.html#awsservicecatalog-resources-for-iam-policies
            return cast("dict[str, Any]", iam_definition["servicecatalog"])

        logger.info(f"Service prefix not {service_prefix} found.")
        return {}
