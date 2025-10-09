# pylint: disable=W1202,E1305
"""
Functions for Minimizing statements, heavily borrowed from policyuniverse.
https://github.com/Netflix-Skunkworks/policyuniverse/

IAM Policies have character limits, which apply to individual policies, and there are also limits on the total
aggregate policy sizes. As such, it is not possible to use exhaustive list of explicit IAM actions.
To have granular control of specific IAM policies, we must use wildcards on IAM Actions, only in a programmatic manner.

This is typically performed by humans by reducing policies to s3:Get*, ec2:Describe*, and other approaches of the sort.

Netflix's PolicyUniverse has addressed this in their minimization code. We borrowed this logic from their code and modified it a bit to fit our needs.

https://aws.amazon.com/iam/faqs/
Q: How many policies can I attach to an IAM role?
* For inline policies: You can add as many inline policies as you want to a user, role, or group, but
  the total aggregate policy size (the sum size of all inline policies) per entity cannot exceed the following limits:
  - User policy size cannot exceed 2,048 characters.
  - Role policy size cannot exceed 10,240 characters.
  - Group policy size cannot exceed 5,120 characters.
* For managed policies: You can add up to 10 managed policies to a user, role, or group.
* The size of each managed policy cannot exceed 6,144 characters.
"""

from __future__ import annotations

import functools
import logging

logger = logging.getLogger(__name__)


# Borrowed from policyuniverse to reduce size
# https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L45
@functools.lru_cache(maxsize=1024)
def _get_prefixes_for_action(action: str) -> list[str]:
    """
    :param action: iam:cat
    :return: [ "iam:", "iam:c", "iam:ca", "iam:cat" ]
    """
    technology, permission = action.split(":")
    retval = [f"{technology}:{permission[:i]}" for i in range(len(permission) + 1)]

    return retval


# Adapted version of policyuniverse's _get_denied_prefixes_from_desired, here:
# https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L101
def get_denied_prefixes_from_desired(desired_actions: list[str], all_actions: set[str]) -> set[str]:  # pylint: disable=missing-function-docstring
    """
    Adapted version of policyuniverse's _get_denied_prefixes_from_desired, here: https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L101
    """
    denied_actions = all_actions.difference(desired_actions)
    denied_prefixes = {
        denied_prefix for denied_action in denied_actions for denied_prefix in _get_prefixes_for_action(denied_action)
    }

    return denied_prefixes


# Adapted version of policyuniverse's _check_permission_length. We are commenting out the skipping prefix message
# https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L111
def check_min_permission_length(permission: str, minchars: int | None = None) -> bool:  # pylint: disable=missing-function-docstring
    """
    Adapted version of policyuniverse's _check_permission_length. We are commenting out the skipping prefix message
    https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L111
    """
    return bool(minchars and permission and len(permission) < int(minchars))


# This is a condensed version of policyuniverse's minimize_statement_actions, changed for our purposes.
# https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L123
def minimize_statement_actions(
    desired_actions: list[str], all_actions: set[str], minchars: int | None = None
) -> list[str]:  # pylint: disable=missing-function-docstring
    """
    This is a condensed version of policyuniverse's minimize_statement_actions, changed for our purposes.
    https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/expander_minimizer.py#L123
    """
    minimized_actions = set()

    desired_actions = [x.lower() for x in desired_actions]
    desired_services = {f"{action.split(':')[0]}:" for action in desired_actions}
    filtered_actions = {
        action for action in all_actions if any(action.startswith(service) for service in desired_services)
    }

    denied_prefixes = get_denied_prefixes_from_desired(desired_actions, filtered_actions)
    for action in desired_actions:
        if action in denied_prefixes:
            # print("Action is a denied prefix. Action: {}".format(action))
            minimized_actions.add(action)
            continue

        found_prefix = False
        prefixes = _get_prefixes_for_action(action)
        for prefix in prefixes:
            permission = prefix.split(":")[1]
            if check_min_permission_length(permission, minchars=minchars):
                continue
            # If the action name is not empty
            if prefix not in denied_prefixes and permission:
                minimized_actions.add(prefix if prefix in desired_actions else f"{prefix}*")
                found_prefix = True
                break

        if not found_prefix:
            logger.debug(f"Could not find suitable prefix. Defaulting to {prefixes[-1]}")
            minimized_actions.add(prefixes[-1])
    # sort the actions
    minimized_actions_list = sorted(minimized_actions)

    return minimized_actions_list
