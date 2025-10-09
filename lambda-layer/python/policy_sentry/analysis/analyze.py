"""
Functions to support the analyze capability in this tool
"""

from __future__ import annotations

import logging
from typing import Any

from policy_sentry.analysis.expand import (
    determine_actions_to_expand,
    get_expanded_policy,
)
from policy_sentry.querying.actions import remove_actions_not_matching_access_level
from policy_sentry.util.policy_files import (
    get_actions_from_policy,
    get_actions_from_statement,
)

logger = logging.getLogger(__name__)


def analyze_by_access_level(policy_json: dict[str, Any], access_level: str) -> list[str]:
    """
    Determine if a policy has any actions with a given access level. This is particularly useful when determining who
    has 'Permissions management' level access

    Arguments:
        policy_json: a dictionary representing the AWS JSON policy
        access_level: The normalized access level - either 'read', 'list', 'write', 'tagging', or 'permissions-management'
    Return:
        List: A list of actions
    """
    expanded_policy = get_expanded_policy(policy_json)
    requested_actions = get_actions_from_policy(expanded_policy)
    # expanded_actions = determine_actions_to_expand(requested_actions)
    actions_by_level = remove_actions_not_matching_access_level(requested_actions, access_level)
    return actions_by_level


def analyze_statement_by_access_level(statement_json: dict[str, Any], access_level: str) -> list[str]:
    """
    Determine if a statement has any actions with a given access level.

    Arguments:
        statement_json: a dictionary representing a statement from an AWS JSON policy
        access_level: The access level - either 'Read', 'List', 'Write', 'Tagging', or 'Permissions management'
    Returns:
        List: A list of actions
    """
    requested_actions = get_actions_from_statement(statement_json)
    expanded_actions = determine_actions_to_expand(requested_actions)
    actions_by_level = remove_actions_not_matching_access_level(expanded_actions, access_level)
    return actions_by_level
