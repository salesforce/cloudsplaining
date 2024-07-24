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

logger = logging.getLogger(__name__)


class AssumeRolePolicyDocument(ResourcePolicyDocument):
    """Holds the AssumeRole/Trust Policy document

    It is a specialized version of a Resource-based policy
    """

    def __init__(self, policy: dict[str, Any]) -> None:
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        # We would actually need to define a proper base class with a generic type for statements
        self.statements: list[AssumeRoleStatement] = []  # type:ignore[assignment]
        # leaving here but excluding from tests because IAM Policy grammar dictates that it must be a list
        if not isinstance(statement_structure, list):  # pragma: no cover
            statement_structure = [statement_structure]

        for statement in statement_structure:
            self.statements.append(AssumeRoleStatement(statement))

    @property
    def role_assumable_by_compute_services(self) -> list[str]:
        """Determines whether or not the role is assumed from a compute service, and if so which ones."""
        assumable_by_compute_services = []
        for statement in self.statements:
            if statement.role_assumable_by_compute_services:
                assumable_by_compute_services.extend(statement.role_assumable_by_compute_services)
        return assumable_by_compute_services


class AssumeRoleStatement(ResourceStatement):
    """
    Statements in an AssumeRole/Trust Policy document
    """

    def __init__(self, statement: dict[str, Any]) -> None:
        super().__init__(statement=statement)

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

        assumable_by_compute_services = []
        for principal in self.principals:
            if principal.endswith(".amazonaws.com"):
                service_prefix_to_evaluate = principal.split(".")[0]
                if service_prefix_to_evaluate in SERVICE_PREFIXES_WITH_COMPUTE_ROLES:
                    assumable_by_compute_services.append(service_prefix_to_evaluate)
        return assumable_by_compute_services
