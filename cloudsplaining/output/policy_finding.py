"""Returns results for a single Policy"""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
from __future__ import annotations

import logging
from typing import Any

from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.constants import (
    ACTIONS_THAT_RETURN_CREDENTIALS,
    ISSUE_SEVERITY,
    READ_ONLY_DATA_EXFILTRATION_ACTIONS,
    RISK_DEFINITION,
)
from cloudsplaining.shared.exclusions import (
    DEFAULT_EXCLUSIONS,
    Exclusions,
    is_name_excluded,
)

logger = logging.getLogger(__name__)


class PolicyFinding:
    """A single policy finding"""

    def __init__(
        self,
        policy_document: PolicyDocument,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
        severity: list[str] | None = None,
    ) -> None:
        """
        Supply a PolicyDocument object and Exclusions object to get a single policy finding
        """
        if not isinstance(exclusions, Exclusions):
            raise Exception("Please supply a Exclusions object")
        self.policy_document = policy_document
        self.exclusions = exclusions
        self.always_exclude_actions = exclusions.exclude_actions

        self.missing_resource_constraints_for_modify_actions = self._missing_resource_constraints_for_modify_actions()
        self.severity = [] if severity is None else severity

    def _missing_resource_constraints_for_modify_actions(self) -> list[str]:
        """Find modify actions that lack resource ARN constraints"""
        actions_missing_resource_constraints = set()
        for statement in self.policy_document.statements:
            logger.debug("Evaluating statement: %s", statement.json)
            if statement.effect == "Allow" and not statement.has_condition:
                actions_missing_resource_constraints.update(
                    statement.missing_resource_constraints_for_modify_actions(self.exclusions)
                )
        return sorted(actions_missing_resource_constraints)

    @property
    def services_affected(self) -> list[str]:
        """Return a list of AWS service prefixes affected by the policy in question."""
        services_affected = set()
        for action in self.missing_resource_constraints_for_modify_actions:
            service = action.partition(":")[0]
            services_affected.add(service)
        # Credentials exposure; since some of those are read-only,
        # they are not in the modify actions so we need to include them here
        for action in self.credentials_exposure:
            service = action.partition(":")[0]
            services_affected.add(service)
        # Data Exfiltration; since some of those are read-only,
        # they are not in the modify actions so we need to include them here
        for action in self.data_exfiltration:
            service = action.partition(":")[0]
            services_affected.add(service)
        return sorted(services_affected)

    @property
    def resource_exposure(self) -> list[str]:
        """Return a list of actions that could cause resource exposure via actions at the 'Permissions management'
        access level, if applicable."""
        if self.always_exclude_actions:
            results = [
                action
                for action in self.policy_document.permissions_management_without_constraints
                if not is_name_excluded(action.lower(), self.always_exclude_actions)
            ]
            return results
        else:
            return self.policy_document.permissions_management_without_constraints

    @property
    def privilege_escalation(self) -> list[dict[str, Any]]:
        """Returns privilege escalation action combinations in the policy, if present"""
        return self.policy_document.allows_privilege_escalation

    @property
    def data_exfiltration(self) -> list[str]:
        """Returns data exfiltration actions in the policy, if present"""
        result = [
            action
            for action in self.policy_document.allows_specific_actions_without_constraints(
                READ_ONLY_DATA_EXFILTRATION_ACTIONS
            )
            if action.lower() not in self.exclusions.exclude_actions
        ]
        return result

    @property
    def service_wildcard(self) -> list[str]:
        """Determine if the policy gives access to all actions within a service - simple grepping"""
        return self.policy_document.service_wildcard

    @property
    def credentials_exposure(self) -> list[str]:
        """Determine if the action returns credentials"""
        # https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a
        results = [
            action
            for action in self.policy_document.allows_specific_actions_without_constraints(
                ACTIONS_THAT_RETURN_CREDENTIALS
            )
            if action.lower() not in self.exclusions.exclude_actions
        ]
        return results

    @property
    def results(self) -> dict[str, Any]:
        """Return the results as JSON"""
        findings = dict(
            ServiceWildcard={
                "severity": ISSUE_SEVERITY["ServiceWildcard"],
                "description": RISK_DEFINITION["ServiceWildcard"],
                "findings": (
                    self.service_wildcard
                    if ISSUE_SEVERITY["ServiceWildcard"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            ServicesAffected=self.services_affected,
            PrivilegeEscalation={
                "severity": ISSUE_SEVERITY["PrivilegeEscalation"],
                "description": RISK_DEFINITION["PrivilegeEscalation"],
                "findings": (
                    self.privilege_escalation
                    if ISSUE_SEVERITY["PrivilegeEscalation"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            DataExfiltration={
                "severity": ISSUE_SEVERITY["DataExfiltration"],
                "description": RISK_DEFINITION["DataExfiltration"],
                "findings": (
                    self.data_exfiltration
                    if ISSUE_SEVERITY["DataExfiltration"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            ResourceExposure={
                "severity": ISSUE_SEVERITY["ResourceExposure"],
                "description": RISK_DEFINITION["ResourceExposure"],
                "findings": (
                    self.resource_exposure
                    if ISSUE_SEVERITY["ResourceExposure"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            CredentialsExposure={
                "severity": ISSUE_SEVERITY["CredentialsExposure"],
                "description": RISK_DEFINITION["CredentialsExposure"],
                "findings": (
                    self.credentials_exposure
                    if ISSUE_SEVERITY["CredentialsExposure"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            InfrastructureModification={
                "severity": ISSUE_SEVERITY["InfrastructureModification"],
                "description": RISK_DEFINITION["InfrastructureModification"],
                "findings": (
                    self.missing_resource_constraints_for_modify_actions
                    if ISSUE_SEVERITY["InfrastructureModification"] in [x.lower() for x in self.severity]
                    or not self.severity
                    else []
                ),
            },
        )
        return findings
