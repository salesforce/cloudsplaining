"""PolicyDocument is re-used whenever IAM Policy Documents are found in the output of the
aws iam get-account-authorization-details command."""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
from __future__ import annotations

import logging
from typing import Any

from policy_sentry.querying.all import get_all_service_prefixes

from cloudsplaining.scan.statement_detail import StatementDetail
from cloudsplaining.shared.constants import (
    ACTIONS_THAT_RETURN_CREDENTIALS,
    PRIVILEGE_ESCALATION_METHODS,
    READ_ONLY_DATA_EXFILTRATION_ACTIONS,
)
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions

logger = logging.getLogger(__name__)
RED = "\033[1;31m"
RESET = "\033[0;0m"


class PolicyDocument:
    """
    Holds the actual AWS IAM Policy document
    """

    def __init__(
        self,
        policy: dict[str, Any],
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
        flag_conditional_statements: bool = False,
        flag_resource_arn_statements: bool = False,
    ) -> None:
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        self.statements = []
        self.flag_conditional_statements = flag_conditional_statements
        self.flag_resource_arn_statements = flag_resource_arn_statements

        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.exclusions = exclusions

        # leaving here but excluding from tests because IAM Policy grammar dictates that it must be a list
        if not isinstance(statement_structure, list):
            statement_structure = [statement_structure]  # pragma: no cover

        for statement in statement_structure:
            self.statements.append(
                StatementDetail(
                    statement,
                    flag_conditional_statements=self.flag_conditional_statements,
                    flag_resource_arn_statements=self.flag_resource_arn_statements,
                )
            )

    @property
    def json(self) -> dict[str, Any]:
        """Return the Policy in JSON"""
        return self.policy

    @property
    def all_allowed_actions(self) -> list[str]:
        """Output all allowed IAM Actions, regardless of resource constraints"""
        allowed_actions = set()
        for statement in self.statements:
            # if Effect is "Deny" - it is not an allowed action
            if statement.effect_allow and statement.expanded_actions:
                allowed_actions.update(statement.expanded_actions)
        allowed_actions = self.filter_deny_statements(allowed_actions)
        return list(allowed_actions)

    def filter_deny_statements(self, allowed_actions: set[str]) -> set[str]:
        """
        filter all denied statements from actions
        """
        for statement in self.statements:
            if statement.effect_deny and statement.expanded_actions:
                allowed_actions = allowed_actions.difference(statement.expanded_actions)
        return allowed_actions

    @property
    def all_allowed_unrestricted_actions(self) -> list[str]:
        """Output all IAM actions that do not practice resource constraints"""
        allowed_actions = set()
        for statement in self.statements:
            if (
                statement.has_resource_wildcard
                and not statement.has_condition
                and statement.effect_allow
                and statement.restrictable_actions
            ):
                allowed_actions.update(statement.restrictable_actions)
            # Fix Issue #254 - Allow flagging risky actions even when there are resource constraints
            if self.flag_resource_arn_statements and statement.effect_allow:
                allowed_actions.update(statement.restrictable_actions)
        allowed_actions = self.filter_deny_statements(allowed_actions)
        return list(allowed_actions)

    @property
    def all_allowed_unrestrictable_actions(self) -> list[str]:
        """Output all IAM actions that cannot be restricted by resource constraints"""
        allowed_actions = set()
        for statement in self.statements:
            if statement.effect_allow and not statement.has_condition and statement.unrestrictable_actions:
                allowed_actions.update(statement.unrestrictable_actions)
            # Fix Issue #254 - Allow flagging risky actions even when there are resource constraints
            if statement.effect_allow and not statement.has_condition and self.flag_resource_arn_statements:
                allowed_actions.update(statement.unrestrictable_actions)
        allowed_actions = self.filter_deny_statements(allowed_actions)
        return list(allowed_actions)

    @property
    def infrastructure_modification(self) -> list[str]:
        """Return a list of modify only missing resource constraints"""
        actions_missing_resource_constraints = []
        for statement in self.statements:
            if statement.effect == "Allow" and not statement.has_condition:
                for action in statement.missing_resource_constraints_for_modify_actions(self.exclusions):
                    if action.lower() not in self.exclusions.exclude_actions:
                        actions_missing_resource_constraints.append(action)  # noqa: PERF401
        actions_missing_resource_constraints.sort()
        return actions_missing_resource_constraints

    @property
    def contains_statement_using_not_action(self) -> list[dict[str, Any]]:
        """If NotAction is used, flag it so the assessor can triage manually"""
        not_action_statements = []
        for statement in self.statements:
            if statement.not_action:
                not_action_statements.append(statement.json)
                if not statement.has_resource_constraints and statement.effect_allow:
                    print(
                        f"{RED}\tNOTE: The policy has Effect=Allow and uses NotAction without any resource "
                        f"constraints: {statement.json}{RESET}"
                    )
        return not_action_statements

    @property
    def allows_privilege_escalation(self) -> list[dict[str, Any]]:
        """
        Determines whether or not the policy allows privilege escalation action combinations published by
        Rhino Security Labs.
        """
        # if severity
        escalations = []
        all_allowed_unrestricted_actions_lowercase = set(x.lower() for x in self.all_allowed_unrestricted_actions)
        all_allowed_unrestricted_actions_lowercase.update([x.lower() for x in self.all_allowed_unrestrictable_actions])
        for escalation_type, actions in PRIVILEGE_ESCALATION_METHODS.items():
            if set(actions).issubset(all_allowed_unrestricted_actions_lowercase):
                # if set(PRIVILEGE_ESCALATION_METHODS[key]).issubset(all_allowed_actions_lowercase):
                escalation = {"type": escalation_type, "actions": actions}
                escalations.append(escalation)
        return escalations

    @property
    def permissions_management_without_constraints(self) -> list[str]:
        """Where applicable, returns a list of 'Permissions management' IAM actions in the statement that
        do not have resource constraints"""
        result = []
        for statement in self.statements:
            if statement.effect == "Allow" and statement.permissions_management_actions_without_constraints:
                result.extend(statement.permissions_management_actions_without_constraints)
        return result

    @property
    def write_actions_without_constraints(self) -> list[str]:
        """Where applicable, returns a list of 'Write' level IAM actions in the statement that
        do not have resource constraints"""
        result = []
        for statement in self.statements:
            if statement.effect == "Allow" and statement.write_actions_without_constraints:
                result.extend(statement.write_actions_without_constraints)
        return result

    @property
    def tagging_actions_without_constraints(self) -> list[str]:
        """Where applicable, returns a list of 'Tagging' level IAM actions in the statement that
        do not have resource constraints"""
        result = []
        for statement in self.statements:
            if statement.effect == "Allow" and statement.tagging_actions_without_constraints:
                result.extend(statement.tagging_actions_without_constraints)
        return result

    def allows_specific_actions_without_constraints(self, specific_actions: list[str]) -> list[str]:
        """Determine whether or not a list of specific IAM Actions are allowed without resource constraints."""
        allowed: set[str] = set()
        if not isinstance(specific_actions, list):
            raise Exception("Please supply a list of actions.")

        # grab the lowercase representation for unrestricted and unrestrictable actions
        unrestricted_actions_lower = {a.lower(): a for a in self.all_allowed_unrestricted_actions}
        unrestrictable_actions_lower = {a.lower(): a for a in self.all_allowed_unrestrictable_actions}

        # Doing this for loop so we can get results that use the official CamelCase actions, and
        # the results don't fail if given lowercase input.
        # this is less efficient but more accurate and the results are pretty :)
        for specific_action in specific_actions:
            specific_action_lower = specific_action.lower()
            if specific_action_lower in unrestricted_actions_lower:
                allowed.add(unrestricted_actions_lower[specific_action_lower])
            elif specific_action_lower in unrestrictable_actions_lower:
                allowed.add(unrestrictable_actions_lower[specific_action_lower])
        results = list(allowed)
        results.sort()
        return results

    @property
    def allows_data_exfiltration_actions(self) -> list[str]:
        """If any 'Data exfiltration' actions are allowed without resource constraints, return those actions."""
        return [
            action
            for action in self.allows_specific_actions_without_constraints(READ_ONLY_DATA_EXFILTRATION_ACTIONS)
            if action.lower() not in self.exclusions.exclude_actions
        ]

    @property
    def credentials_exposure(self) -> list[str]:
        """Determine if the action returns credentials"""
        # https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a
        return [
            action
            for action in self.allows_specific_actions_without_constraints(ACTIONS_THAT_RETURN_CREDENTIALS)
            if action.lower() not in self.exclusions.exclude_actions
        ]

    @property
    def service_wildcard(self) -> list[str]:
        """Determine if the policy gives access to all actions within a service - simple grepping"""
        services = set()
        all_service_prefixes = get_all_service_prefixes()

        for statement in self.statements:
            logger.debug("Evaluating statement: %s", statement.json)
            if statement.effect_allow and not statement.has_condition:
                if isinstance(statement.actions, list):
                    for action in statement.actions:
                        # If the action is a straight up *
                        if action == "*":
                            logger.debug("All actions are allowed by this policy")
                            services.update(all_service_prefixes)
                        # Otherwise, it will take the format of service:*
                        else:
                            service, this_action = action.split(":")
                            # service:*
                            if this_action == "*":
                                services.add(service)
                elif isinstance(statement.actions, str):
                    # If the action is a straight up *
                    if statement.actions == "*":
                        logger.debug("All actions are allowed by this policy")
                        services.update(all_service_prefixes)
                    else:
                        service, this_action = statement.actions.split(":")
                        # service:*
                        if this_action == "*":
                            services.add(service)
        return sorted(services)
