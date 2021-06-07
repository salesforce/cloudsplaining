"""Manages the exclusions template for scanning the Authorizations file"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
from typing import List, Union, Dict

from cloudsplaining.shared.validation import check_exclusions_schema
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared import utils

logger = logging.getLogger(__name__)


class Exclusions:
    """Contains the exclusions configuration as an object"""

    def __init__(
        self, exclusions_config: Dict[str, List[str]] = DEFAULT_EXCLUSIONS_CONFIG
    ) -> None:
        check_exclusions_schema(exclusions_config)
        self.config = exclusions_config
        self.include_actions = self._include_actions()
        self.exclude_actions = self._exclude_actions()
        self.roles = self._roles()
        self.users = self._users()
        self.groups = self._groups()
        self.policies = self._policies()

    def _roles(self) -> List[str]:
        provided_roles = self.config.get("roles", [])
        # Normalize for comparisons
        roles = [role.lower() for role in provided_roles]
        return roles

    def _users(self) -> List[str]:
        provided_users = self.config.get("users", [])
        # Normalize for comparisons
        users = [user.lower() for user in provided_users]
        return users

    def _groups(self) -> List[str]:
        provided_groups = self.config.get("groups", [])
        # Normalize for comparisons
        groups = [group.lower() for group in provided_groups]
        return groups

    def _policies(self) -> List[str]:
        provided_policies = self.config.get("policies", [])
        # Normalize for comparisons
        policies = [policy.lower() for policy in provided_policies]
        return policies

    def _include_actions(self) -> List[str]:
        include_actions = self.config.get("include-actions", [])
        # Set to lowercase so subsequent evaluations are faster.
        always_include_actions = [x.lower() for x in include_actions]
        return always_include_actions

    def _exclude_actions(self) -> List[str]:
        exclude_actions = self.config.get("exclude-actions", [])
        # Set to lowercase so subsequent evaluations are faster.
        always_exclude_actions = [x.lower() for x in exclude_actions]
        return always_exclude_actions

    def is_action_always_included(self, action_in_question: str) -> Union[bool, str]:
        """
        Supply an IAM action, and get a decision about whether or not it is excluded.

        :return:
        """
        if action_in_question.lower() in self.include_actions:
            return action_in_question
        else:
            return False

    def is_action_always_excluded(self, action_in_question: str) -> bool:
        """
        Supply an IAM action, and get a decision about whether or not it is always included.

        :return:
        """
        if self.exclude_actions:
            return is_name_excluded(action_in_question.lower(), self.exclude_actions)
        else:
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
        elif principal_type == "Group":
            return is_name_excluded(principal.lower(), self.groups)
        elif principal_type == "Role":
            return is_name_excluded(principal.lower(), self.roles)
        else:  # pragma: no cover
            raise Exception(
                "Please supply User, Group, or Role as the principal argument."
            )

    def get_allowed_actions(self, requested_actions: List[str]) -> List[str]:
        """Given a list of actions, it will evaluate those actions against the exclusions configuration and return a
        list of actions after filtering for exclusions."""

        always_include_actions = set()
        actions_minus_exclusions = set()
        for action in requested_actions:
            # ALWAYS INCLUDE ACTIONS
            if action.lower() in self.include_actions:
                always_include_actions.add(action)
            # RULE OUT EXCLUDED ACTIONS
            if not is_name_excluded(action.lower(), self.exclude_actions):
                actions_minus_exclusions.add(action)

        return list(always_include_actions | actions_minus_exclusions)


# pylint: disable=inconsistent-return-statements
def is_name_excluded(name: str, exclusions_list: Union[str, List[str]]) -> bool:
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
