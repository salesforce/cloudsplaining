"""Returns results for a single Policy"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
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

    def __init__(self, policy_document, exclusions=DEFAULT_EXCLUSIONS):
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

    def _missing_resource_constraints_for_modify_actions(self):
        """Find modify actions that lack resource ARN constraints"""
        actions_missing_resource_constraints = []
        for statement in self.policy_document.statements:
            logger.debug("Evaluating statement: %s", statement.json)
            if statement.effect == "Allow":
                actions_missing_resource_constraints.extend(
                    statement.missing_resource_constraints_for_modify_actions(
                        self.exclusions
                    )
                )
        if actions_missing_resource_constraints:
            these_results = list(
                dict.fromkeys(actions_missing_resource_constraints)
            )  # remove duplicates
            these_results.sort()
            return these_results
        else:
            return []

    @property
    def services_affected(self):
        """Return a list of AWS service prefixes affected by the policy in question."""
        services_affected = []
        for action in self.missing_resource_constraints_for_modify_actions:
            service = action.split(":")[0]
            if service not in services_affected:
                services_affected.append(service)
        # Credentials exposure; since some of those are read-only,
        # they are not in the modify actions so we need to include them here
        for action in self.credentials_exposure:
            service = action.split(":")[0]
            if service not in services_affected:
                services_affected.append(service)
        # Data Exfiltration; since some of those are read-only,
        # they are not in the modify actions so we need to include them here
        for action in self.data_exfiltration:
            service = action.split(":")[0]
            if service not in services_affected:
                services_affected.append(service)
        services_affected = list(dict.fromkeys(services_affected))
        services_affected.sort()
        return services_affected

    @property
    def resource_exposure(self):
        """Return a list of actions that could cause resource exposure via actions at the 'Permissions management'
        access level, if applicable."""
        results = []
        if self.always_exclude_actions:
            for (
                action
            ) in self.policy_document.permissions_management_without_constraints:
                if is_name_excluded(action.lower(), self.always_exclude_actions):
                    pass  # pragma: no cover
                else:
                    results.append(action)
            return results
        else:
            return self.policy_document.permissions_management_without_constraints

    @property
    def privilege_escalation(self):
        """Returns privilege escalation action combinations in the policy, if present"""
        return self.policy_document.allows_privilege_escalation

    @property
    def data_exfiltration(self):
        """Returns data exfiltration actions in the policy, if present"""
        result = []
        for action in self.policy_document.allows_specific_actions_without_constraints(
            READ_ONLY_DATA_EXFILTRATION_ACTIONS
        ):
            if action.lower() not in self.exclusions.exclude_actions:
                result.append(action)
        return result

    @property
    def service_wildcard(self):
        """Determine if the policy gives access to all actions within a service - simple grepping"""
        return self.policy_document.service_wildcard

    @property
    def credentials_exposure(self):
        """Determine if the action returns credentials"""
        # https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a
        results = []
        for action in self.policy_document.allows_specific_actions_without_constraints(
            ACTIONS_THAT_RETURN_CREDENTIALS
        ):
            if action.lower() not in self.exclusions.exclude_actions:
                results.append(action)
        return results

    @property
    def results(self):
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
