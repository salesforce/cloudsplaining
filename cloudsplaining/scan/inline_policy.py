"""Represents the Inline Policies (UserPolicyList, GroupPolicyList, RolePolicyList) entries under each principal."""
import json
from typing import Dict, Any, cast

from cloudsplaining.shared.utils import get_non_provider_id
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions


class InlinePolicy:
    """
    Contains information about an Inline Policy, including the Policy Document
    """

    def __init__(
        self, policy_detail: Dict[str, Any], exclusions: Exclusions = DEFAULT_EXCLUSIONS
    ) -> None:
        """
        Initialize the InlinePolicy object.

        :param policy_detail: The JSON containing the PolicyName and PolicyDocument
        """
        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.policy_name = policy_detail.get("PolicyName", "")
        self.policy_document = PolicyDocument(
            cast(Dict[str, Any], policy_detail.get("PolicyDocument")), exclusions
        )
        # Generating the provider ID based on a string representation of the Policy Document,
        # to avoid collisions where there are inline policies with the same name but different contents
        # self.policy_id = get_non_provider_id(self.policy_name)
        self.policy_id = get_non_provider_id(json.dumps(self.policy_document.json))

        self.exclusions = exclusions
        self.is_excluded = self._is_excluded(exclusions)

    def _is_excluded(self, exclusions: Exclusions) -> bool:
        """Determine whether the policy name or policy ID is excluded"""
        return bool(
            exclusions.is_policy_excluded(self.policy_name)
            or exclusions.is_policy_excluded(self.policy_id)
        )

    @property
    def json(self) -> Dict[str, Any]:
        """Return JSON output for high risk actions"""
        result = dict(
            PolicyName=self.policy_name,
            PolicyId=self.policy_id,
            PolicyDocument=self.policy_document.json,
            PrivilegeEscalation=self.policy_document.allows_privilege_escalation,
            DataExfiltration=self.policy_document.allows_data_exfiltration_actions,
            ResourceExposure=self.policy_document.permissions_management_without_constraints,
            ServiceWildcard=self.policy_document.service_wildcard,
            CredentialsExposure=self.policy_document.credentials_exposure,
            is_excluded=self.is_excluded,
        )
        return result

    @property
    def json_large(self) -> Dict[str, Any]:
        """Return JSON output - including Infra Modification actions, which can be large"""
        result = dict(
            PolicyName=self.policy_name,
            PolicyId=self.policy_id,
            PolicyDocument=self.policy_document.json,
            PrivilegeEscalation=self.policy_document.allows_privilege_escalation,
            DataExfiltration=self.policy_document.allows_data_exfiltration_actions,
            ResourceExposure=self.policy_document.permissions_management_without_constraints,
            ServiceWildcard=self.policy_document.service_wildcard,
            CredentialsExposure=self.policy_document.credentials_exposure,
            InfrastructureModification=self.policy_document.infrastructure_modification,
            is_excluded=self.is_excluded,
        )
        return result
