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
        always_include_actions = [x.lower() for x in include_actions]
        return always_include_actions

    def _exclude_actions(self):
        exclude_actions = self.config.get("exclude-actions", None)
        always_exclude_actions = [x.lower() for x in exclude_actions]
        return always_exclude_actions

    def get_allowed_actions(self, requested_actions):
        """Given a list of actions, it will evaluate those actions against the exclusions configuration and return a
        list of actions after filtering for exclusions. """
        # normalize the incoming list of actions
        actions_lowercase = [x.lower() for x in requested_actions]
        # ALWAYS EXCLUDE ACTIONS
        # Determine if there is an intersection between the requested one and the excluded ones
        intersection_exclusions = list(set(actions_lowercase) & set(self.exclude_actions))
        actions_included = []
        if intersection_exclusions:
            for action in requested_actions:
                if not is_name_excluded(action, self.exclude_actions):
                    actions_included.append(action)
        return actions_included


# pylint: disable=inconsistent-return-statements
def is_name_excluded(name, exclusions_list):
    """
    :param name: The name of the policy, role, user, or group
    :param exclusions_list: List of exclusions
    :return:
    """
    for exclusion in exclusions_list:
        # Skip empty items
        if exclusion == "":
            continue
        if exclusion.lower() == name.lower():
            print(f"\tExcluded: {exclusion}")
            return True
        # ThePerfectManDoesntExi*
        if exclusion.endswith("*"):
            prefix = exclusion[: exclusion.index("*")]
            # print(prefix)
            if name.lower().startswith(prefix.lower()):
                # logger.debug(f"Excluded prefix: {exclusion}")
                print(f"\tExcluded prefix: {exclusion}")
                return True
        if exclusion.startswith("*"):
            suffix = exclusion.split("*")[-1]
            if name.lower().endswith(suffix.lower()):
                # logger.debug(f"Excluded suffix: {exclusion}")
                print(f"\tExcluded suffix: {exclusion}")
                return True
