"""Manages the exclusions template for scanning the Authorizations file"""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
from __future__ import annotations

import logging

from cloudsplaining.shared import utils
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared.validation import check_exclusions_schema

logger = logging.getLogger(__name__)


class Exclusions:
    """Contains the exclusions configuration as an object"""

    def __init__(self, exclusions_config: dict[str, list[str]] = DEFAULT_EXCLUSIONS_CONFIG) -> None:
        check_exclusions_schema(exclusions_config)
        self.config = exclusions_config
        self.include_actions = self._include_actions()
        self.exclude_actions = self._exclude_actions()
        self.roles = self._roles()
        self.users = self._users()
        self.groups = self._groups()
        self.policies = self._policies()
        self.known_accounts = self._known_accounts()

    def _roles(self) -> list[str]:
        provided_roles = self.config.get("roles", [])
        # Normalize for comparisons
        return [role.lower() for role in provided_roles]

    def _users(self) -> list[str]:
        provided_users = self.config.get("users", [])
        # Normalize for comparisons
        return [user.lower() for user in provided_users]

    def _groups(self) -> list[str]:
        provided_groups = self.config.get("groups", [])
        # Normalize for comparisons
        return [group.lower() for group in provided_groups]

    def _policies(self) -> list[str]:
        provided_policies = self.config.get("policies", [])
        # Normalize for comparisons
        return [policy.lower() for policy in provided_policies]

    def _include_actions(self) -> list[str]:
        include_actions = self.config.get("include-actions", [])
        # Set to lowercase so subsequent evaluations are faster.
        return [x.lower() for x in include_actions]

    def _exclude_actions(self) -> list[str]:
        exclude_actions = self.config.get("exclude-actions", [])
        # Set to lowercase so subsequent evaluations are faster.
        return [x.lower() for x in exclude_actions]

    def _known_accounts(self) -> set[str]:
        provided_known_accounts = self.config.get("known-accounts", [])
        # Normalize for comparisons - remove empty strings
        return {account for account in provided_known_accounts if account.strip()}

    def is_action_always_included(self, action_in_question: str) -> bool | str:
        """
        Supply an IAM action, and get a decision about whether or not it is excluded.

        :return:
        """
        if action_in_question.lower() in self.include_actions:
            return action_in_question

        return False

    def is_action_always_excluded(self, action_in_question: str) -> bool:
        """
        Supply an IAM action, and get a decision about whether or not it is always included.

        :return:
        """
        if self.exclude_actions:
            return is_name_excluded(action_in_question.lower(), self.exclude_actions)

        return False  # pragma: no cover

    def is_policy_excluded(self, policy_name: str) -> bool:
        """
        Supply a policy name or path, and get a decision about whether or not it is excluded.

        :param policy_name: Policy name or Policy path
        :return:
        """
        return is_name_excluded(policy_name, self.policies)

    def is_principal_excluded(self, principal: str, principal_type: str) -> bool:
        """
        Supply a principal name or path, and get a decision about whether or not it is excluded.

        :param principal: a principal name or path
        :param principal_type: User, Group, or Role
        :return: a boolean decision
        """
        if principal_type == "User":
            return is_name_excluded(principal.lower(), self.users)
        if principal_type == "Group":
            return is_name_excluded(principal.lower(), self.groups)
        if principal_type == "Role":
            return is_name_excluded(principal.lower(), self.roles)

        raise Exception("Please supply User, Group, or Role as the principal argument.")  # pragma: no cover

    def get_allowed_actions(self, requested_actions: list[str]) -> list[str]:
        """Given a list of actions, it will evaluate those actions against the exclusions configuration and return a
        list of actions after filtering for exclusions."""
        if not self.exclude_actions:
            # no exclusion -> all allowed
            return list(set(requested_actions))

        allowed_actions = set()
        for action in requested_actions:
            action_lower = action.lower()
            # ALWAYS INCLUDE ACTIONS
            if action_lower in self.include_actions:
                allowed_actions.add(action)
            # RULE OUT EXCLUDED ACTIONS
            if not is_name_excluded(action_lower, self.exclude_actions):
                allowed_actions.add(action)

        return list(allowed_actions)


# pylint: disable=inconsistent-return-statements
def is_name_excluded(name: str, exclusions_list: str | list[str]) -> bool:
    """
    :param name: The name of the policy, role, user, or group
    :param exclusions_list: List of exclusions
    :return:
    """
    if isinstance(exclusions_list, str):
        exclusions_list = [exclusions_list]

    for exclusion in exclusions_list:
        # Skip empty items
        if exclusion == "":
            continue
        if exclusion.lower() == name.lower():
            logger.debug(f"\tExcluded: {exclusion}")
            return True
        # ThePerfectManDoesntExi*
        if exclusion.endswith("*"):
            prefix = exclusion[:-1]
            # print(prefix)
            if name.lower().startswith(prefix.lower()):
                # logger.debug(f"Excluded prefix: {exclusion}")
                utils.print_grey(f"\tExcluded prefix: {exclusion}")
                return True
        if exclusion.startswith("*"):
            suffix = exclusion[1:]
            if name.lower().endswith(suffix.lower()):
                utils.print_grey(f"\tExcluded suffix: {exclusion}")
                return True
    return False


DEFAULT_EXCLUSIONS = Exclusions(DEFAULT_EXCLUSIONS_CONFIG)
