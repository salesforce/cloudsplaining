"""Returns results for a single Policy"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
from typing import List, Dict, Any

from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.constants import (
    READ_ONLY_DATA_EXFILTRATION_ACTIONS,
    ACTIONS_THAT_RETURN_CREDENTIALS,
)
from cloudsplaining.shared.exclusions import (
    Exclusions,
    DEFAULT_EXCLUSIONS,
    is_name_excluded,
)

logger = logging.getLogger(__name__)


class PolicyFinding:
    """A single policy finding"""

    def __init__(
        self,
        policy_document: PolicyDocument,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ) -> None:
        """
        Supply a PolicyDocument object and Exclusions object to get a single policy finding
        """
        if not isinstance(exclusions, Exclusions):
            raise Exception("Please supply a Exclusions object")
        self.policy_document = policy_document
        self.exclusions = exclusions
        self.always_exclude_actions = exclusions.exclude_actions

        self.missing_resource_constraints_for_modify_actions = (
            self._missing_resource_constraints_for_modify_actions()
        )

    def _missing_resource_constraints_for_modify_actions(self) -> List[str]:
        """Find modify actions that lack resource ARN constraints"""
        actions_missing_resource_constraints = set()
        for statement in self.policy_document.statements:
            logger.debug("Evaluating statement: %s", statement.json)
            if statement.effect == "Allow":
                actions_missing_resource_constraints.update(
                    statement.missing_resource_constraints_for_modify_actions(
                        self.exclusions
                    )
                )
        return sorted(actions_missing_resource_constraints)

    @property
    def services_affected(self) -> List[str]:
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
    def resource_exposure(self) -> List[str]:
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
    def privilege_escalation(self) -> List[Dict[str, Any]]:
        """Returns privilege escalation action combinations in the policy, if present"""
        return self.policy_document.allows_privilege_escalation

    @property
    def data_exfiltration(self) -> List[str]:
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
    def service_wildcard(self) -> List[str]:
        """Determine if the policy gives access to all actions within a service - simple grepping"""
        return self.policy_document.service_wildcard

    @property
    def credentials_exposure(self) -> List[str]:
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
    def results(self) -> Dict[str, Any]:
        """Return the results as JSON"""
        findings = dict(
            ServiceWildcard=self.service_wildcard,
            ServicesAffected=self.services_affected,
            PrivilegeEscalation=self.privilege_escalation,
            ResourceExposure=self.resource_exposure,
            DataExfiltration=self.data_exfiltration,
            CredentialsExposure=self.credentials_exposure,
            InfrastructureModification=self.missing_resource_constraints_for_modify_actions,
        )
        return findings
