"""Abstracts evaluation of IAM Policy statements."""
import logging
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

all_actions = get_all_actions()


# pylint: disable=too-many-instance-attributes
class StatementDetail:
    """
    Analyzes individual statements within a policy
    """

    def __init__(self, statement):
        self.json = statement
        self.statement = statement
        self.effect = statement["Effect"]
        self.resources = self._resources()
        self.actions = self._actions()
        self.not_action = self._not_action()
        self.not_action_effective_actions = self._not_action_effective_actions()
        self.not_resource = self._not_resource()

    def _actions(self):
        """Holds the actions in a statement"""
        actions = self.statement.get("Action")
        if not actions:
            return []
        if not isinstance(actions, list):
            actions = [actions]
        return actions

    def _resources(self):
        """Holds the resource ARNs in a statement"""
        resources = self.statement.get("Resource")
        if not resources:
            return []
        # If it's a string, turn it into a list
        if not isinstance(resources, list):
            resources = [resources]
        return resources

    def _not_action(self):
        """Holds the NotAction details.
        We won't do anything with it - but we will flag it as something for the assessor to triage."""
        not_action = self.statement.get("NotAction")
        if not not_action:
            return []
        if not isinstance(not_action, list):
            not_action = [not_action]
        return not_action

    def _not_resource(self):
        """Holds the NotResource details.
        We won't do anything with it - but we will flag it as something for the assessor to triage."""
        not_resource = self.statement.get("NotResource")
        if not not_resource:
            return []
        if not isinstance(not_resource, list):
            not_resource = [not_resource]
        return not_resource

    # @property
    def _not_action_effective_actions(self):
        """If NotAction is used, calculate the allowed actions - i.e., what it would be """
        effective_actions = []
        if not self.not_action:
            return None
        not_actions_expanded = determine_actions_to_expand(self.not_action)
        not_actions_expanded_lowercase = [x.lower() for x in not_actions_expanded]

        # Effect: Allow && Resource != "*"
        if self.has_resource_constraints and self.effect_allow:
            opposite_actions = []
            for arn in self.resources:
                actions_specific_to_arn = get_actions_matching_arn(arn)
                if actions_specific_to_arn:
                    opposite_actions.extend(get_actions_matching_arn(arn))

            for opposite_action in opposite_actions:
                # If it's in NotActions, then it is not an action we want
                if opposite_action.lower() in not_actions_expanded_lowercase:
                    pass
                # Otherwise add it
                else:
                    effective_actions.append(opposite_action)
            effective_actions.sort()
            return effective_actions
        # Effect: Allow, Resource != "*", and Action == prefix:*
        elif not self.has_resource_constraints and self.effect_allow:
            # Then we calculate the reverse using all_actions
            for action in all_actions:
                # If it's in NotActions, then it is not an action we want
                if action.lower() in not_actions_expanded_lowercase:
                    pass
                    # Otherwise add it
                else:
                    effective_actions.append(action)
            effective_actions.sort()
            return effective_actions
        elif self.has_resource_constraints and self.effect_deny:
            logger.debug("NOTE: Haven't decided if we support Effect Deny here?")
            return None
        elif not self.has_resource_constraints and self.effect_deny:
            logger.debug("NOTE: Haven't decided if we support Effect Deny here?")
            return None
        # only including this so Pylint doesn't yell at us
        else:
            return None  # pragma: no cover

    @property
    def has_not_resource_with_allow(self):
        """Per the AWS documentation, the NotResource should NEVER be used with the Allow Effect.
        See documentation here. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_notresource.html#notresource-element-combinations"""
        result = False
        if self.not_resource:
            if self.effect_allow:
                result = True
                logger.warning(
                    "Per the AWS documentation, the NotResource should never be used with the "
                    "Allow Effect. We suggest changing this ASAP"
                )
        return result

    @property
    def expanded_actions(self):
        """Expands the full list of allowed actions from the Policy/"""
        if self.actions:
            expanded = determine_actions_to_expand(self.actions)
            expanded.sort()
            return expanded
        elif self.not_action:
            return self.not_action_effective_actions
        else:
            raise Exception(  # pragma: no cover
                "The Policy should include either NotAction or Action in the statement."
            )

    @property
    def effect_deny(self):
        """Check if the Effect of the Policy is 'Deny'"""
        return bool(self.effect == "Deny")

    @property
    def effect_allow(self):
        """Check if the Effect of the Policy is 'Allow'"""
        return bool(self.effect == "Allow")

    @property
    def services_in_use(self):
        """Get a list of the services in use by the statement."""
        service_prefixes = []
        for action in self.expanded_actions:
            service, action_name = action.split(":")  # pylint: disable=unused-variable
            if service not in service_prefixes:
                service_prefixes.append(service)
        service_prefixes.sort()
        return service_prefixes

    @property
    def has_resource_constraints(self):
        """Determine whether or not the statement allows resource constraints."""
        answer = True
        if len(self.resources) == 0:
            # This is probably a NotResources situation which we do not support.
            pass
        if len(self.resources) == 1:
            if self.resources[0] == "*":
                answer = False
        elif len(self.resources) > 1:  # pragma: no cover
            # It's possible that someone writes a bad policy that includes both a resource ARN as well as a wildcard.
            for resource in self.resources:
                if resource == "*":
                    answer = False
        return answer

    @property
    def permissions_management_actions_without_constraints(self):
        """Where applicable, returns a list of 'Permissions management' IAM actions in the statement that
        do not have resource constraints"""
        result = []
        if not self.has_resource_constraints:
            if self.expanded_actions:
                result = remove_actions_not_matching_access_level(
                    self.expanded_actions, "Permissions management"
                )
        return result

    @property
    def write_actions_without_constraints(self):
        """Where applicable, returns a list of 'Write' level IAM actions in the statement that
        do not have resource constraints"""
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(
                self.expanded_actions, "Write"
            )
        return result

    @property
    def tagging_actions_without_constraints(self):
        """Where applicable, returns a list of 'Tagging' level IAM actions in the statement that
        do not have resource constraints"""
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(
                self.expanded_actions, "Tagging"
            )
        return result

    def missing_resource_constraints(self, exclusions=DEFAULT_EXCLUSIONS):
        """Return a list of any actions - regardless of access level - allowed by the statement that do not leverage
        resource constraints."""
        if not isinstance(exclusions, Exclusions):
            raise Exception(  # pragma: no cover
                "The provided exclusions is not the Exclusions object type. "
                "Please use the Exclusions object."
            )
        actions_missing_resource_constraints = []
        if len(self.resources) == 1:
            if self.resources[0] == "*":
                actions_missing_resource_constraints = remove_wildcard_only_actions(
                    self.expanded_actions
                )
        results = exclusions.get_allowed_actions(actions_missing_resource_constraints)
        return results

    def missing_resource_constraints_for_modify_actions(
        self, exclusions=DEFAULT_EXCLUSIONS
    ):
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
        if exclusions.include_actions is None:
            always_look_for_actions = []  # pragma: no cover
        else:
            always_look_for_actions = exclusions.include_actions
        actions_missing_resource_constraints = self.missing_resource_constraints(
            exclusions
        )

        always_actions_found = []
        for action in actions_missing_resource_constraints:
            if action.lower() in [x.lower() for x in always_look_for_actions]:
                always_actions_found.append(action)
        modify_actions_missing_constraints = remove_read_level_actions(
            actions_missing_resource_constraints
        )
        modify_actions_missing_constraints = (
            modify_actions_missing_constraints + always_actions_found
        )

        modify_actions_missing_constraints = list(
            dict.fromkeys(modify_actions_missing_constraints)
        )
        modify_actions_missing_constraints.sort()
        return modify_actions_missing_constraints
