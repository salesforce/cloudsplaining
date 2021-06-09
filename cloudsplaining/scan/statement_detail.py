"""Abstracts evaluation of IAM Policy statements."""
import logging
from typing import Dict, Any, List, Optional

from cached_property import cached_property

from policy_sentry.analysis.analyze import determine_actions_to_expand
from policy_sentry.querying.actions import (
    remove_actions_not_matching_access_level,
    get_actions_matching_arn,
)
from policy_sentry.querying.all import get_all_actions
from cloudsplaining.shared.utils import (
    remove_read_level_actions,
    remove_wildcard_only_actions,
)
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
logger = logging.getLogger(__name__)
logging.getLogger("policy_sentry").setLevel(logging.WARNING)

ALL_ACTIONS = get_all_actions()


# pylint: disable=too-many-instance-attributes
class StatementDetail:
    """
    Analyzes individual statements within a policy
    """

    def __init__(self, statement: Dict[str, Any]) -> None:
        self.json = statement
        self.statement = statement
        self.effect = statement["Effect"]
        self.condition = statement.get("Condition", None)
        self.resources = self._resources()
        self.actions = self._actions()
        self.not_action = self._not_action()

        self.has_resource_wildcard = self._has_resource_wildcard()
        self.not_action_effective_actions = self._not_action_effective_actions()
        self.not_resource = self._not_resource()
        self.has_condition = self._has_condition()

        self.restrictable_actions = remove_wildcard_only_actions(self.expanded_actions)
        self.unrestrictable_actions = list(
            set(self.expanded_actions or []) - set(self.restrictable_actions)
        )
        self.has_resource_constraints = self._has_resource_constraints()

    def _actions(self) -> List[str]:
        """Holds the actions in a statement"""
        actions = self.statement.get("Action")
        if not actions:
            return []
        if not isinstance(actions, list):
            return [actions]
        return actions

    def _resources(self) -> List[str]:
        """Holds the resource ARNs in a statement"""
        resources = self.statement.get("Resource")
        if not resources:
            return []
        # If it's a string, turn it into a list
        if not isinstance(resources, list):
            return [resources]
        return resources

    def _not_action(self) -> List[str]:
        """Holds the NotAction details.
        We won't do anything with it - but we will flag it as something for the assessor to triage."""
        not_action = self.statement.get("NotAction")
        if not not_action:
            return []
        if not isinstance(not_action, list):
            return [not_action]
        return not_action

    def _not_resource(self) -> List[str]:
        """Holds the NotResource details.
        We won't do anything with it - but we will flag it as something for the assessor to triage."""
        not_resource = self.statement.get("NotResource")
        if not not_resource:
            return []
        if not isinstance(not_resource, list):
            return [not_resource]
        return not_resource

    # @property
    def _not_action_effective_actions(self) -> Optional[List[str]]:
        """If NotAction is used, calculate the allowed actions - i.e., what it would be """
        effective_actions = []
        if not self.not_action:
            return None

        not_actions_expanded_lowercase = [
            a.lower() for a in determine_actions_to_expand(self.not_action)
        ]

        # Effect: Allow && Resource != "*"
        if not self.has_resource_wildcard and self.effect_allow:
            opposite_actions = []
            for arn in self.resources:
                actions_specific_to_arn = get_actions_matching_arn(arn)
                if actions_specific_to_arn:
                    opposite_actions.extend(actions_specific_to_arn)

            for opposite_action in opposite_actions:
                # If it's in NotActions, then it is not an action we want
                if opposite_action.lower() not in not_actions_expanded_lowercase:
                    effective_actions.append(opposite_action)
            effective_actions.sort()
            return effective_actions

        # Effect: Allow, Resource == "*", and Action == prefix:*
        if self.has_resource_wildcard and self.effect_allow:
            # Then we calculate the reverse using all_actions

            # If it's in NotActions, then it is not an action we want
            effective_actions = [
                action
                for action in ALL_ACTIONS
                if action.lower() not in not_actions_expanded_lowercase
            ]

            effective_actions.sort()
            return effective_actions

        if self.has_resource_wildcard and self.effect_deny:
            logger.debug("NOTE: Haven't decided if we support Effect Deny here?")
            return None

        if not self.has_resource_wildcard and self.effect_deny:
            logger.debug("NOTE: Haven't decided if we support Effect Deny here?")
            return None
        # only including this so Pylint doesn't yell at us
        return None  # pragma: no cover

    @property
    def has_not_resource_with_allow(self) -> bool:
        """Per the AWS documentation, the NotResource should NEVER be used with the Allow Effect.
        See documentation here. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_notresource.html#notresource-element-combinations"""
        if self.not_resource and self.effect_allow:
            logger.warning(
                "Per the AWS documentation, the NotResource should never be used with the "
                "Allow Effect. We suggest changing this ASAP"
            )
            return True
        return False

    @cached_property
    def expanded_actions(self) -> Optional[List[str]]:
        """Expands the full list of allowed actions from the Policy/"""

        if self.actions:
            expanded: List[str] = determine_actions_to_expand(self.actions)
            expanded.sort()
            return expanded
        elif self.not_action:
            return self.not_action_effective_actions
        else:
            raise Exception(  # pragma: no cover
                "The Policy should include either NotAction or Action in the statement."
            )

    @property
    def effect_deny(self) -> bool:
        """Check if the Effect of the Policy is 'Deny'"""
        return bool(self.effect == "Deny")

    @property
    def effect_allow(self) -> bool:
        """Check if the Effect of the Policy is 'Allow'"""
        return bool(self.effect == "Allow")

    @property
    def services_in_use(self) -> List[str]:
        """Get a list of the services in use by the statement."""
        service_prefixes = set()
        for action in self.expanded_actions:
            service, action_name = action.split(":")  # pylint: disable=unused-variable
            service_prefixes.add(service)
        return sorted(service_prefixes)

    @property
    def permissions_management_actions_without_constraints(self) -> List[str]:
        """Where applicable, returns a list of 'Permissions management' IAM actions in the statement that
        do not have resource constraints"""
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(
                self.restrictable_actions, "Permissions management"
            )
        return result

    @property
    def write_actions_without_constraints(self) -> List[str]:
        """Where applicable, returns a list of 'Write' level IAM actions in the statement that
        do not have resource constraints"""
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(
                self.restrictable_actions, "Write"
            )
        return result

    @property
    def tagging_actions_without_constraints(self) -> List[str]:
        """Where applicable, returns a list of 'Tagging' level IAM actions in the statement that
        do not have resource constraints"""
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(
                self.restrictable_actions, "Tagging"
            )
        return result

    def missing_resource_constraints(
        self, exclusions: Exclusions = DEFAULT_EXCLUSIONS
    ) -> List[str]:
        """Return a list of any actions - regardless of access level - allowed by the statement that do not leverage
        resource constraints."""
        if not isinstance(exclusions, Exclusions):
            raise Exception(  # pragma: no cover
                "The provided exclusions is not the Exclusions object type. "
                "Please use the Exclusions object."
            )
        actions_missing_resource_constraints = []
        if len(self.resources) == 1 and self.resources[0] == "*":
            actions_missing_resource_constraints = self.restrictable_actions
        return exclusions.get_allowed_actions(actions_missing_resource_constraints)

    def missing_resource_constraints_for_modify_actions(
        self, exclusions: Exclusions = DEFAULT_EXCLUSIONS
    ) -> List[str]:
        """
        Determine whether or not any actions at the 'Write', 'Permissions management', or 'Tagging' access levels
        are allowed by the statement without resource constraints.

        :param exclusions: Exclusions object
        """
        if not isinstance(exclusions, Exclusions):
            raise Exception(  # pragma: no cover
                "The provided exclusions is not the Exclusions object type. "
                "Please use the Exclusions object."
            )
        # This initially includes read-only and modify level actions
        if exclusions.include_actions:
            always_look_for_actions = [x.lower() for x in exclusions.include_actions]
        else:
            always_look_for_actions = []

        actions_missing_resource_constraints = self.missing_resource_constraints(
            exclusions
        )

        always_actions_found = []
        for action in actions_missing_resource_constraints:
            if action.lower() in always_look_for_actions:
                always_actions_found.append(action)

        modify_actions_missing_constraints = set()
        modify_actions_missing_constraints.update(
            remove_read_level_actions(actions_missing_resource_constraints)
        )
        modify_actions_missing_constraints.update(always_actions_found)

        return list(modify_actions_missing_constraints)

    def _has_condition(self) -> bool:
        if self.condition:
            return True
        return False

    def _has_resource_wildcard(self) -> bool:
        """Determine whether or not a wildcard is in the resources part."""
        if len(self.resources) == 0:
            # This is probably a NotResources situation which we do not support.
            pass
        if len(self.resources) == 1 and self.resources[0] == "*":
            return True
        elif len(self.resources) > 1:  # pragma: no cover
            # It's possible that someone writes a bad policy that includes both a resource ARN as well as a wildcard.
            return any(resource == "*" for resource in self.resources)
        return False

    def _has_resource_constraints(self) -> bool:
        """Determine whether or not the statement has resource constraints."""
        if self.has_resource_wildcard and self.restrictable_actions:
            return False
        return True
