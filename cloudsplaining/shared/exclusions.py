"""Manages the exclusions template for scanning the Authorizations file"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
from cloudsplaining.shared.validation import check_exclusions_schema
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG

logger = logging.getLogger(__name__)


class Exclusions:
    """Contains the exclusions configuration as an object"""

    def __init__(self, exclusions_config=DEFAULT_EXCLUSIONS_CONFIG):
        check_exclusions_schema(exclusions_config)
        self.config = exclusions_config
        self.include_actions = self._include_actions()
        self.exclude_actions = self._exclude_actions()
        self.roles = self._roles()
        self.users = self._users()
        self.groups = self._groups()
        self.policies = self._policies()

    def _roles(self):
        provided_roles = self.config.get("roles", None)
        roles = []
        # Normalize for comparisons
        if provided_roles:
            for role in provided_roles:
                roles.append(role.lower())
        return roles

    def _users(self):
        provided_users = self.config.get("users", None)
        users = []
        if provided_users:
            # Normalize for comparisons
            for user in provided_users:
                users.append(user.lower())
        return users

    def _groups(self):
        provided_groups = self.config.get("groups", None)
        groups = []
        if provided_groups:
            # Normalize for comparisons
            for group in provided_groups:
                groups.append(group.lower())
        return groups

    def _policies(self):
        provided_policies = self.config.get("policies", None)
        policies = []
        if provided_policies:
            # Normalize for comparisons
            for policy in provided_policies:
                policies.append(policy.lower())
        return policies

    def _include_actions(self):
        include_actions = self.config.get("include-actions", None)
        # Set to lowercase so subsequent evaluations are faster.
        if include_actions:
            always_include_actions = [x.lower() for x in include_actions]
            return always_include_actions
        else:
            return []

    def _exclude_actions(self):
        exclude_actions = self.config.get("exclude-actions", None)
        if exclude_actions:
            always_exclude_actions = [x.lower() for x in exclude_actions]
            return always_exclude_actions
        else:
            return []

    def is_action_always_included(self, action_in_question):
        """
        Supply an IAM action, and get a decision about whether or not it is excluded.

        :return:
        """
        if self.include_actions:
            if action_in_question.lower() in self.include_actions:
                return action_in_question
            else:
                return False
        else:
            return False

    def is_action_always_excluded(self, action_in_question):
        """
        Supply an IAM action, and get a decision about whether or not it is always included.

        :return:
        """
        if self.exclude_actions:
            return bool(
                is_name_excluded(action_in_question.lower(), self.exclude_actions)
            )
        else:
            return False  # pragma: no cover

    def is_policy_excluded(self, policy_name):
        """
        Supply a policy name or path, and get a decision about whether or not it is excluded.

        :param policy_name: Policy name or Policy path
        :return:
        """
        return bool(is_name_excluded(policy_name, self.policies))

    def is_principal_excluded(self, principal, principal_type):
        """
        Supply a principal name or path, and get a decision about whether or not it is excluded.

        :param principal: a principal name or path
        :param principal_type: User, Group, or Role
        :return: a boolean decision
        """
        if principal_type == "User":
            return bool(is_name_excluded(principal.lower(), self.users))
        elif principal_type == "Group":
            return bool(is_name_excluded(principal.lower(), self.groups))
        elif principal_type == "Role":
            return bool(is_name_excluded(principal.lower(), self.roles))
        else:  # pragma: no cover
            raise Exception(
                "Please supply User, Group, or Role as the principal argument."
            )

    def get_allowed_actions(self, requested_actions):
        """Given a list of actions, it will evaluate those actions against the exclusions configuration and return a
        list of actions after filtering for exclusions."""

        always_include_actions = []
        # ALWAYS INCLUDE ACTIONS
        for action in requested_actions:
            for include_action in self.include_actions:
                if action.lower() == include_action.lower():
                    always_include_actions.append(action)
        # RULE OUT EXCLUDED ACTIONS
        actions_minus_exclusions = []
        for action in requested_actions:
            if not is_name_excluded(action.lower(), self.exclude_actions):
                actions_minus_exclusions.append(action)

        results = always_include_actions + actions_minus_exclusions
        results = list(dict.fromkeys(results))
        return results


# pylint: disable=inconsistent-return-statements
def is_name_excluded(name, exclusions_list):
    """
    :param name: The name of the policy, role, user, or group
    :param exclusions_list: List of exclusions
    :return:
    """
    result = None
    if isinstance(exclusions_list, str):
        exclusions_list = [exclusions_list]

    for exclusion in exclusions_list:
        # Skip empty items
        if exclusion == "":
            continue
        if exclusion.lower() == name.lower():
            logger.debug(f"\tExcluded: {exclusion}")
            result = True
            break
        # ThePerfectManDoesntExi*
        if exclusion.endswith("*"):
            prefix = exclusion[: exclusion.index("*")]
            # print(prefix)
            if name.lower().startswith(prefix.lower()):
                # logger.debug(f"Excluded prefix: {exclusion}")
                print(f"\tExcluded prefix: {exclusion}")
                result = True
                break
        if exclusion.startswith("*"):
            suffix = exclusion.split("*")[-1]
            if name.lower().endswith(suffix.lower()):
                print(f"\tExcluded suffix: {exclusion}")
                result = True
                break
    return result


DEFAULT_EXCLUSIONS = Exclusions(DEFAULT_EXCLUSIONS_CONFIG)
