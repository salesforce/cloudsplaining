"""Represents the AssumeRole Trust Policy. This is mainly used for identifying whether roles are assumable via AWS compute services."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
from typing import Dict, Any, List

from cloudsplaining.shared.constants import SERVICE_PREFIXES_WITH_COMPUTE_ROLES

logger = logging.getLogger(__name__)


class AssumeRolePolicyDocument:
    """
    Holds the AssumeRole/Trust Policy document
    """

    def __init__(self, policy: Dict[str, Any]) -> None:
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        self.statements = []
        # leaving here but excluding from tests because IAM Policy grammar dictates that it must be a list
        if not isinstance(statement_structure, list):  # pragma: no cover
            statement_structure = [statement_structure]

        for statement in statement_structure:
            self.statements.append(AssumeRoleStatement(statement))

    @property
    def json(self) -> Dict[str, Any]:
        """Return the AssumeRole Policy in JSON"""
        return self.policy

    @property
    def role_assumable_by_compute_services(self) -> List[str]:
        """Determines whether or not the role is assumed from a compute service, and if so which ones."""
        assumable_by_compute_services = []
        for statement in self.statements:
            if statement.role_assumable_by_compute_services:
                assumable_by_compute_services.extend(
                    statement.role_assumable_by_compute_services
                )
        return assumable_by_compute_services


class AssumeRoleStatement:
    """
    Statements in an AssumeRole/Trust Policy document
    """

    def __init__(self, statement: Dict[str, Any]) -> None:
        self.json = statement
        self.statement = statement
        self.effect = statement["Effect"]
        self.actions = self._assume_role_actions()
        self.principals = self._principals()

        # self.not_principal = statement.get("NotPrincipal")
        if statement.get("NotPrincipal"):
            logger.critical(  # pragma: no cover
                "NotPrincipal is used in the IAM AssumeRole Trust Policy. "
                "This should NOT be used. We suggest reviewing it ASAP."
            )

    def _assume_role_actions(self) -> List[str]:
        """Verifies that this is limited to just sts:AssumeRole"""
        actions = self.statement.get("Action", [])
        if not actions:
            logger.debug("The AssumeRole Policy has no actions in it.")
            return []

        if isinstance(actions, list):
            return actions

        return [actions]

    def _principals(self) -> List[str]:
        """Extracts all principals from IAM statement.
        Should handle these cases:
        "Principal": "value"
        "Principal": ["value"]
        "Principal": { "AWS": "value" }
        "Principal": { "AWS": ["value", "value"] }
        "Principal": { "Service": "value" }
        "Principal": { "Service": ["value", "value"] }
        Return: Set of principals
        """
        principals: List[str] = []
        principal = self.statement.get("Principal", None)
        if not principal:
            # It is possible not to define a principal, AWS ignores these statements.
            return principals  # pragma: no cover

        if isinstance(principal, dict):

            if "AWS" in principal:
                if isinstance(principal["AWS"], list):
                    principals.extend(principal["AWS"])
                else:
                    principals.append(principal["AWS"])

            if "Service" in principal:
                if isinstance(principal["Service"], list):
                    principals.extend(principal["Service"])
                else:
                    principals.append(principal["Service"])
        else:
            principals.append(principal)
        # principals = list(principals).sort()
        return principals

    @property
    def role_assumable_by_compute_services(self) -> List[str]:
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
