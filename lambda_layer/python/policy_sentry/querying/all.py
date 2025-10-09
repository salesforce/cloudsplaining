"""IAM Database queries that are not specific to either the Actions, ARNs, or Condition Keys tables."""

from __future__ import annotations

import functools
import logging

from policy_sentry.shared.constants import (
    POLICY_SENTRY_SCHEMA_VERSION_NAME,
)
from policy_sentry.shared.iam_data import (
    get_service_prefix_data,
    iam_definition,
)

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1024)
def get_all_service_prefixes() -> set[str]:
    """
    Gets all the AWS service prefixes from the actions table.

    If the action table does NOT have specific IAM actions (and therefore only supports * actions),
    then it will not be included in the response.

    Returns:
        List: A list of all AWS service prefixes present in the table.
    """
    results = set(iam_definition.keys())
    results.discard(POLICY_SENTRY_SCHEMA_VERSION_NAME)

    return results


@functools.lru_cache(maxsize=1024)
def get_all_actions(lowercase: bool = False) -> set[str]:
    """
    Gets a huge list of all IAM actions. This is used as part of the policyuniverse approach to minimizing
    IAM Policies to meet AWS-mandated character limits on policies.

    :param lowercase: Set to true to have the list of actions be in all lowercase strings.
    :return: A list of all actions present in the database.
    """
    all_service_prefixes = get_all_service_prefixes()

    all_actions: set[str] = set()

    for service_prefix in all_service_prefixes:
        service_prefix_data = get_service_prefix_data(service_prefix)
        if lowercase:
            action_names = service_prefix_data["privileges_lower_name"].keys()
        else:
            action_names = service_prefix_data["privileges_lower_name"].values()

        all_actions.update(f"{service_prefix}:{action_name}" for action_name in action_names)

    return all_actions


def get_service_authorization_url(service_prefix: str) -> str | None:
    """
    Gets the URL to the Actions, Resources, and Condition Keys page for a particular service.
    """
    result: str = iam_definition.get(service_prefix, {}).get("service_authorization_url")
    return result
