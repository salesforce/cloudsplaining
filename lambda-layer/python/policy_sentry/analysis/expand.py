"""Functions to expand wilcard actions into a full list of actions."""

from __future__ import annotations

import copy
import fnmatch
import logging
from typing import Any

from policy_sentry.querying.actions import get_actions_for_service
from policy_sentry.querying.all import get_all_actions
from policy_sentry.util.policy_files import get_actions_from_statement

logger = logging.getLogger(__name__)


def expand(action: str | list[str]) -> list[str]:
    """
    expand the action wildcards into a full action

    Arguments:
        action: An action in the form with a wildcard - like s3:Get*, or s3:L*
    Returns:
        List: A list of all the expanded actions (like actions matching s3:Get*)
    """

    if isinstance(action, list):
        expanded_actions = []
        for item in action:
            expanded_actions.extend(expand(item))
        return expanded_actions

    if action == "*":
        return list(get_all_actions())
    elif "*" in action:
        service_prefix = action.split(":", maxsplit=1)[0]
        service_actions = get_actions_for_service(service_prefix=service_prefix)
        expanded = [
            expanded_action
            for expanded_action in service_actions
            if fnmatch.fnmatchcase(expanded_action.lower(), action.lower())
        ]

        # if we get a wildcard for a tech we've never heard of, just return the
        # wildcard
        if not expanded:
            logger.debug(
                "ERROR: The action %s references a wildcard for an unknown resource.",
                action,
            )
            return [action]

        return expanded
    return [action]


def determine_actions_to_expand(action_list: list[str]) -> list[str]:
    """
    Determine if an action needs to get expanded from its wildcard

    Arguments:
        action_list: A list of actions
    Returns:
        List: A list of actions
    """
    new_action_list = []
    for action in action_list:
        if "*" in action:
            expanded_action = expand(action)
            new_action_list.extend(expanded_action)
        else:
            # If there is no wildcard, copy that action name over to the new_action_list
            new_action_list.append(action)
    new_action_list.sort()
    return new_action_list


def get_expanded_policy(policy: dict[str, Any]) -> dict[str, Any]:
    """
    Given a policy, expand the * Actions in IAM policy files to improve readability

    Arguments:
        policy: dictionary containing valid AWS IAM Policy
    Returns:
        Dictionary: the policy that has the `*` expanded
    """
    modified_policy = copy.deepcopy(policy)

    modified_statement = modified_policy["Statement"]
    if isinstance(modified_statement, dict):
        requested_actions = get_actions_from_statement(modified_statement)
        expanded_actions = determine_actions_to_expand(requested_actions)
        if "NotAction" in modified_statement:
            if isinstance(modified_statement["NotAction"], list):
                modified_statement["NotAction"] = expanded_actions
            elif isinstance(modified_statement["NotAction"], str):
                modified_statement["NotAction"] = []
            logger.warning(
                "NotAction is in the statement. Policy Sentry will expand any wildcard actions "
                "that are in the NotAction list, but it will not factor the NotAction actions into any analysis about "
                "whether or not the actions are allowed by the policy. "
                "If you are concerned about this, please review this specific policy manually."
            )
        elif "Action" in modified_statement:
            modified_statement["Action"] = expanded_actions
    # Otherwise it will be a list of Sids
    elif isinstance(modified_statement, list):
        for statement in modified_statement:
            requested_actions = get_actions_from_statement(statement)
            expanded_actions = determine_actions_to_expand(requested_actions)
            if "NotAction" in statement:
                if isinstance(statement["NotAction"], list):
                    statement["NotAction"] = expanded_actions
                elif isinstance(statement["NotAction"], str):
                    statement["NotAction"] = []
                logger.warning(
                    "NotAction is in the statement. Policy Sentry will expand any wildcard actions "
                    "that are in the NotAction list, but it will not factor the NotAction actions into any analysis "
                    "about whether or not the actions are allowed by the policy."
                    "If you are concerned about this, please review this specific policy manually."
                )
            elif "Action" in statement:
                statement["Action"] = expanded_actions
    else:
        logger.critical("Unknown error: The 'Statement' is neither a dict nor a list")
    return modified_policy
