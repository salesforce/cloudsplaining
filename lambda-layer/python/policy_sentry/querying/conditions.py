"""
Methods that execute specific queries against the SQLite database for the CONDITIONS table.
This supports the policy_sentry query functionality
"""

from __future__ import annotations

import functools
import logging
from typing import cast

from policy_sentry.querying.actions import get_action_data
from policy_sentry.shared.iam_data import get_service_prefix_data
from policy_sentry.util.conditions import is_condition_key_match

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1024)
def get_condition_keys_for_service(service_prefix: str) -> list[str]:
    """
    Get a list of available conditions per AWS service

    Arguments:
        service_prefix: An AWS service prefix, like `s3` or `kms`
    Returns:
        List: A list of condition keys
    """
    service_prefix_data = get_service_prefix_data(service_prefix)
    results = list(service_prefix_data["conditions"])
    return results


# Per condition key name
# pylint: disable=inconsistent-return-statements
def get_condition_key_details(service_prefix: str, condition_key_name: str) -> dict[str, str]:
    """
    Get details about a specific condition key in JSON format

    Arguments:
        service_prefix: An AWS service prefix, like `ec2` or `kms`
        condition_key_name: The name of a condition key, like `ec2:Vpc`
    Returns:
        Dictionary: Metadata about the condition key
    """
    service_prefix_data = get_service_prefix_data(service_prefix)
    for condition_name, condition_data in service_prefix_data["conditions"].items():
        if is_condition_key_match(condition_name, condition_key_name):
            output = {
                "name": condition_name,
                "description": condition_data["description"],
                "condition_value_type": condition_data["type"].lower(),
            }
            return output

    return {}


def get_conditions_for_action_and_raw_arn(action: str, raw_arn: str) -> list[str]:
    """
    Get a list of conditions available to an action.

    Arguments:
        action: The IAM action, like s3:GetObject
        raw_arn: The raw ARN format specific to the action
    Returns:
        List: A list of condition keys
    """
    service_prefix, action_name = action.split(":")
    action_data = get_action_data(service_prefix, action_name)
    conditions = []
    for action_info in action_data[service_prefix]:
        if action_info["resource_arn_format"].lower() == raw_arn.lower():
            conditions.extend(action_info["condition_keys"])
    return conditions


def get_condition_keys_available_to_raw_arn(raw_arn: str) -> list[str]:
    """
    Get a list of condition keys available to a RAW ARN

    Arguments:
        raw_arn: The value in the database, like arn:${Partition}:s3:::${BucketName}/${ObjectName}
    Returns:
        List: A list of condition keys
    """
    results = set()
    elements = raw_arn.split(":", 5)
    service_prefix = elements[2]
    service_prefix_data = get_service_prefix_data(service_prefix)
    for resource_data in service_prefix_data["resources"].values():
        if resource_data["arn"] == raw_arn:
            results.update(resource_data["condition_keys"])

    return list(results)


# pylint: disable=inconsistent-return-statements
def get_condition_value_type(condition_key: str) -> str | None:
    """
    Get the data type of the condition key - like Date, String, etc.

    Arguments:
        condition_key: A condition key, like a4b:filters_deviceType
    Returns:
        String: type of the condition key, like Bool, Date, String, etc.
    """
    service_prefix, _ = condition_key.split(":")
    service_prefix_data = get_service_prefix_data(service_prefix)

    for condition_key_entry, condition_key_data in service_prefix_data["conditions"].items():
        if is_condition_key_match(condition_key_entry, condition_key):
            return cast("str", condition_key_data["type"]).lower()

    return None
