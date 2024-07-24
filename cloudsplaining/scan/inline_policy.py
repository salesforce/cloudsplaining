"""Represents the Inline Policies (UserPolicyList, GroupPolicyList, RolePolicyList) entries under each principal."""

from __future__ import annotations

import json
from typing import Any, cast

from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.constants import ISSUE_SEVERITY, RISK_DEFINITION
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions
from cloudsplaining.shared.utils import get_non_provider_id


class InlinePolicy:
    """
    Contains information about an Inline Policy, including the Policy Document
    """

    def __init__(
        self,
        policy_detail: dict[str, Any],
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
        flag_conditional_statements: bool = False,
        flag_resource_arn_statements: bool = False,
        severity: list[str] | None = None,
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
        # Fix Issue #254 - Allow flagging risky actions even when there are resource constraints
        self.flag_conditional_statements = flag_conditional_statements
        self.flag_resource_arn_statements = flag_resource_arn_statements

        self.policy_name = policy_detail.get("PolicyName", "")
        self.policy_document = PolicyDocument(
            cast("dict[str, Any]", policy_detail.get("PolicyDocument")),
            exclusions=exclusions,
            flag_conditional_statements=flag_conditional_statements,
            flag_resource_arn_statements=flag_resource_arn_statements,
        )
        # Generating the provider ID based on a string representation of the Policy Document,
        # to avoid collisions where there are inline policies with the same name but different contents
        # self.policy_id = get_non_provider_id(self.policy_name)
        self.policy_id = get_non_provider_id(json.dumps(self.policy_document.json))

        self.exclusions = exclusions
        self.is_excluded = self._is_excluded(exclusions)
        self.severity = [] if severity is None else severity
        self.iam_data: dict[str, dict[Any, Any]] = {
            "groups": {},
            "users": {},
            "roles": {},
        }

    def set_iam_data(self, iam_data: dict[str, dict[Any, Any]]) -> None:
        self.iam_data = iam_data

    def _is_excluded(self, exclusions: Exclusions) -> bool:
        """Determine whether the policy name or policy ID is excluded"""
        return bool(exclusions.is_policy_excluded(self.policy_name) or exclusions.is_policy_excluded(self.policy_id))

    def getFindingLinks(self, findings: list[dict[str, Any]]) -> dict[str, str]:  # noqa: N802
        links = {}
        for finding in findings:
            links[finding["type"]] = (
                f'https://cloudsplaining.readthedocs.io/en/latest/glossary/privilege-escalation/#{finding["type"]}'
            )
        return links

    @property
    def getAttached(self) -> dict[str, list[Any]]:  # noqa: N802
        attached: dict[str, list[Any]] = {"roles": [], "groups": [], "users": []}
        for principal_type in ["roles", "groups", "users"]:
            principals = (self.iam_data[principal_type]).keys()
            for principal_id in principals:
                inline_policies = {}
                if self.is_excluded:
                    return {}
                inline_policies.update(self.iam_data[principal_type][principal_id]["inline_policies"])
                if self.policy_id in inline_policies:
                    attached[principal_type].append(self.iam_data[principal_type][principal_id]["name"])
        return attached

    @property
    def json(self) -> dict[str, Any]:
        """Return JSON output for high risk actions"""
        result = dict(
            PolicyName=self.policy_name,
            PolicyId=self.policy_id,
            PolicyDocument=self.policy_document.json,
            AttachedTo=self.getAttached,
            PrivilegeEscalation={
                "severity": ISSUE_SEVERITY["PrivilegeEscalation"],
                "description": RISK_DEFINITION["PrivilegeEscalation"],
                "findings": (
                    self.policy_document.allows_privilege_escalation
                    if ISSUE_SEVERITY["PrivilegeEscalation"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
                "links": self.getFindingLinks(
                    self.policy_document.allows_privilege_escalation
                    if ISSUE_SEVERITY["PrivilegeEscalation"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            DataExfiltration={
                "severity": ISSUE_SEVERITY["DataExfiltration"],
                "description": RISK_DEFINITION["DataExfiltration"],
                "findings": (
                    self.policy_document.allows_data_exfiltration_actions
                    if ISSUE_SEVERITY["DataExfiltration"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            ResourceExposure={
                "severity": ISSUE_SEVERITY["ResourceExposure"],
                "description": RISK_DEFINITION["ResourceExposure"],
                "findings": (
                    self.policy_document.permissions_management_without_constraints
                    if ISSUE_SEVERITY["ResourceExposure"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            ServiceWildcard={
                "severity": ISSUE_SEVERITY["ServiceWildcard"],
                "description": RISK_DEFINITION["ServiceWildcard"],
                "findings": (
                    self.policy_document.service_wildcard
                    if ISSUE_SEVERITY["ServiceWildcard"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            CredentialsExposure={
                "severity": ISSUE_SEVERITY["CredentialsExposure"],
                "description": RISK_DEFINITION["CredentialsExposure"],
                "findings": (
                    self.policy_document.credentials_exposure
                    if ISSUE_SEVERITY["CredentialsExposure"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            is_excluded=self.is_excluded,
        )
        return result

    @property
    def json_large(self) -> dict[str, Any]:
        """Return JSON output - including Infra Modification actions, which can be large"""
        result = dict(
            PolicyName=self.policy_name,
            PolicyId=self.policy_id,
            PolicyDocument=self.policy_document.json,
            AttachedTo=self.getAttached,
            PrivilegeEscalation={
                "severity": ISSUE_SEVERITY["PrivilegeEscalation"],
                "description": RISK_DEFINITION["PrivilegeEscalation"],
                "findings": (
                    self.policy_document.allows_privilege_escalation
                    if ISSUE_SEVERITY["PrivilegeEscalation"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
                "links": self.getFindingLinks(
                    self.policy_document.allows_privilege_escalation
                    if ISSUE_SEVERITY["PrivilegeEscalation"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            DataExfiltration={
                "severity": ISSUE_SEVERITY["DataExfiltration"],
                "description": RISK_DEFINITION["DataExfiltration"],
                "findings": (
                    self.policy_document.allows_data_exfiltration_actions
                    if ISSUE_SEVERITY["DataExfiltration"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            ResourceExposure={
                "severity": ISSUE_SEVERITY["ResourceExposure"],
                "description": RISK_DEFINITION["ResourceExposure"],
                "findings": (
                    self.policy_document.permissions_management_without_constraints
                    if ISSUE_SEVERITY["ResourceExposure"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            ServiceWildcard={
                "severity": ISSUE_SEVERITY["ServiceWildcard"],
                "description": RISK_DEFINITION["ServiceWildcard"],
                "findings": (
                    self.policy_document.service_wildcard
                    if ISSUE_SEVERITY["ServiceWildcard"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            CredentialsExposure={
                "severity": ISSUE_SEVERITY["CredentialsExposure"],
                "description": RISK_DEFINITION["CredentialsExposure"],
                "findings": (
                    self.policy_document.credentials_exposure
                    if ISSUE_SEVERITY["CredentialsExposure"] in [x.lower() for x in self.severity] or not self.severity
                    else []
                ),
            },
            InfrastructureModification={
                "severity": ISSUE_SEVERITY["InfrastructureModification"],
                "description": RISK_DEFINITION["InfrastructureModification"],
                "findings": (
                    self.policy_document.infrastructure_modification
                    if ISSUE_SEVERITY["InfrastructureModification"] in [x.lower() for x in self.severity]
                    or not self.severity
                    else []
                ),
            },
            is_excluded=self.is_excluded,
        )
        return result
