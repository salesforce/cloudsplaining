"""Represents the AssumeRole Trust Policy. This is mainly used for identifying whether roles are assumable via AWS compute services."""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
from __future__ import annotations

import logging
from typing import Any

from cloudsplaining.scan.resource_policy_document import (
    ResourcePolicyDocument,
    ResourceStatement,
)
from cloudsplaining.shared.constants import SERVICE_PREFIXES_WITH_COMPUTE_ROLES
from cloudsplaining.shared.exclusions import (
    DEFAULT_EXCLUSIONS,
    Exclusions,
)
from cloudsplaining.shared.utils import get_account_id_from_principal

logger = logging.getLogger(__name__)


class AssumeRolePolicyDocument(ResourcePolicyDocument):
    """Holds the AssumeRole/Trust Policy document

    It is a specialized version of a Resource-based policy
    """

    def __init__(
        self,
        policy: dict[str, Any],
        current_account_id: str | None = None,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ) -> None:
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        self.current_account_id = current_account_id
        # We would actually need to define a proper base class with a generic type for statements
        self.statements: list[AssumeRoleStatement] = []  # type:ignore[assignment]
        self.exclusions = exclusions
        # leaving here but excluding from tests because IAM Policy grammar dictates that it must be a list
        if not isinstance(statement_structure, list):  # pragma: no cover
            statement_structure = [statement_structure]

        for statement in statement_structure:
            self.statements.append(AssumeRoleStatement(statement, current_account_id, exclusions))

    @property
    def role_assumable_by_compute_services(self) -> list[str]:
        """Determines whether or not the role is assumed from a compute service, and if so which ones."""
        return [
            principal
            for statement in self.statements
            if statement.role_assumable_by_compute_services
            for principal in statement.role_assumable_by_compute_services
        ]

    @property
    def role_assumable_by_cross_account_principals(self) -> list[str]:
        """Determines whether or not the role can be assumed from principals in other accounts, and if so which ones."""
        return [
            principal
            for statement in self.statements
            if statement.role_assumable_by_cross_account_principals
            for principal in statement.role_assumable_by_cross_account_principals
        ]

    @property
    def role_assumable_by_any_principal(self) -> list[str]:
        """Determines whether or not the role can be assumed by any principal (*) or any AWS account root."""
        return [
            principal
            for statement in self.statements
            if statement.role_assumable_by_any_principal
            for principal in statement.role_assumable_by_any_principal
        ]

    @property
    def role_assumable_by_any_principal_with_conditions(self) -> list[str]:
        """Determines whether or not the role can be assumed by any principal (*) or any AWS account root with conditions."""
        return [
            principal
            for statement in self.statements
            if statement.role_assumable_by_any_principal_with_conditions
            for principal in statement.role_assumable_by_any_principal_with_conditions
        ]


class AssumeRoleStatement(ResourceStatement):
    """
    Statements in an AssumeRole/Trust Policy document
    """

    def __init__(
        self,
        statement: dict[str, Any],
        current_account_id: str | None = None,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ) -> None:
        super().__init__(statement=statement)
        self.current_account_id = current_account_id
        self.exclusions = exclusions

        # self.not_principal = statement.get("NotPrincipal")
        if statement.get("NotPrincipal"):
            logger.critical(  # pragma: no cover
                "NotPrincipal is used in the IAM AssumeRole Trust Policy. "
                "This should NOT be used. We suggest reviewing it ASAP."
            )

    def _assume_role_actions(self) -> list[str]:
        """Verifies that this is limited to just sts:AssumeRole"""
        actions = self.statement.get("Action", [])
        if not actions:
            logger.debug("The AssumeRole Policy has no actions in it.")
            return []

        if isinstance(actions, list):
            return actions

        return [actions]

    @property
    def role_assumable_by_compute_services(self) -> list[str]:
        """Determines whether or not the role is assumed from a compute service, and if so which ones."""
        # sts:AssumeRole must be there
        lowercase_actions = [x.lower() for x in self.actions]
        if "sts:AssumeRole".lower() not in lowercase_actions:
            return []

        # Effect must be Allow
        if self.effect.lower() != "allow":
            return []

        assumable_by_compute_services = []
        for principal in self.principals:
            if principal.endswith(".amazonaws.com"):
                service_prefix_to_evaluate = principal.split(".")[0]
                if service_prefix_to_evaluate in SERVICE_PREFIXES_WITH_COMPUTE_ROLES:
                    assumable_by_compute_services.append(service_prefix_to_evaluate)
        return assumable_by_compute_services

    @property
    def role_assumable_by_cross_account_principals(self) -> list[str]:
        """Determines whether or not the role can be assumed from principals in other accounts, and if so which ones."""
        # sts:AssumeRole must be there
        lowercase_actions = [x.lower() for x in self.actions]
        if "sts:AssumeRole".lower() not in lowercase_actions:
            return []

        # Effect must be Allow
        if self.effect.lower() != "allow":
            return []

        return [
            principal
            for principal in self.principals
            if (principal_account_id := get_account_id_from_principal(principal))
            and (self.current_account_id is None or principal_account_id != self.current_account_id)
            and principal_account_id not in self.exclusions.known_accounts
        ]

    @property
    def role_assumable_by_any_principal(self) -> list[str]:
        """Determines whether or not the role can be assumed by any principal (*) or any AWS account root."""
        # sts:AssumeRole must be there
        lowercase_actions = [x.lower() for x in self.actions]
        if "sts:AssumeRole".lower() not in lowercase_actions:
            return []

        # Effect must be Allow
        if self.effect.lower() != "allow":
            return []

        # Must have no conditions
        if self.statement.get("Condition"):
            return []

        # Check if any principal is "*" or "arn:aws:iam::*:root"
        return [principal for principal in self.principals if principal == "*" or principal == "arn:aws:iam::*:root"]

    @property
    def role_assumable_by_any_principal_with_conditions(self) -> list[str]:
        """Determines whether or not the role can be assumed by any principal (*) or any AWS account root with conditions."""
        # sts:AssumeRole must be there
        lowercase_actions = [x.lower() for x in self.actions]
        if "sts:AssumeRole".lower() not in lowercase_actions:
            return []

        # Effect must be Allow
        if self.effect.lower() != "allow":
            return []

        # Must have conditions (opposite of role_assumable_by_any_principal)
        if not self.statement.get("Condition"):
            return []

        # Check if any principal is "*" or "arn:aws:iam::*:root"
        return [principal for principal in self.principals if principal == "*" or principal == "arn:aws:iam::*:root"]
