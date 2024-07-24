"""Processes RoleDetailList"""

from __future__ import annotations

import json
import logging
from typing import Any

from cloudsplaining.scan.assume_role_policy_document import AssumeRolePolicyDocument
from cloudsplaining.scan.inline_policy import InlinePolicy
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails
from cloudsplaining.scan.statement_detail import StatementDetail
from cloudsplaining.shared import utils
from cloudsplaining.shared.exceptions import NotFoundException
from cloudsplaining.shared.exclusions import (
    DEFAULT_EXCLUSIONS,
    Exclusions,
    is_name_excluded,
)
from cloudsplaining.shared.utils import (
    get_full_policy_path,
    get_non_provider_id,
    get_policy_name,
    is_aws_managed,
)

logger = logging.getLogger(__name__)


class RoleDetailList:
    """Processes all entries under the RoleDetailList"""

    def __init__(
        self,
        role_details: list[dict[str, Any]],
        policy_details: ManagedPolicyDetails,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
        flag_conditional_statements: bool = False,
        flag_resource_arn_statements: bool = False,
        severity: list[str] | None = None,
    ) -> None:
        self.severity = [] if severity is None else severity
        self.roles = []

        if not isinstance(exclusions, Exclusions):
            raise Exception("For exclusions, please provide an object of the Exclusions type")
        self.exclusions = exclusions
        # Fix Issue #254 - Allow flagging risky actions even when there are resource constraints
        self.flag_conditional_statements = flag_conditional_statements
        self.flag_resource_arn_statements = flag_resource_arn_statements
        self.iam_data: dict[str, dict[Any, Any]] = {
            "groups": {},
            "users": {},
            "roles": {},
        }

        for role_detail in role_details:
            this_role_name = role_detail.get("RoleName")
            this_role_path = role_detail["Path"]
            if is_name_excluded(this_role_path, "/aws-service-role*"):
                logger.debug(
                    "%s role is excluded because it is an immutable AWS Service role with a path of %s",
                    this_role_name,
                    this_role_path,
                )
            else:
                self.roles.append(
                    RoleDetail(
                        role_detail,
                        policy_details,
                        exclusions=exclusions,
                        flag_conditional_statements=self.flag_conditional_statements,
                        flag_resource_arn_statements=self.flag_resource_arn_statements,
                        severity=self.severity,
                    )
                )

    def set_iam_data(self, iam_data: dict[str, dict[Any, Any]]) -> None:
        self.iam_data = iam_data
        for role in self.roles:
            role.set_iam_data(iam_data)

    def get_all_allowed_actions_for_role(self, name: str) -> list[str] | None:
        """Returns a list of all allowed actions by the role across all its policies"""
        for role_detail in self.roles:
            if role_detail.role_name == name:
                return role_detail.all_allowed_actions
        return None

    def get_all_iam_statements_for_role(self, name: str) -> list[StatementDetail] | None:
        """Returns a list of all StatementDetail objects across all the policies assigned to the role"""
        for role_detail in self.roles:
            if role_detail.role_name == name:
                return role_detail.all_iam_statements
        return None

    @property
    def role_names(self) -> list[str]:
        """Get a list of all role names in the account"""
        results = [role_detail.role_name for role_detail in self.roles]
        results.sort()
        return results

    @property
    def all_infrastructure_modification_actions_by_inline_policies(self) -> list[str]:
        """Return a list of all infrastructure modification actions allowed by all inline policies in violation."""
        result = set()
        for role in self.roles:
            for policy in role.inline_policies:
                result.update(policy.policy_document.infrastructure_modification)
        return sorted(result)

    @property
    def inline_policies_json(self) -> dict[str, dict[str, Any]]:
        """Return JSON representation of attached inline policies"""
        results = {}
        for role_detail in self.roles:
            results.update(role_detail.inline_policies_json)
        return results

    @property
    def json(self) -> dict[str, dict[str, Any]]:
        """Get all JSON results"""
        result = {role.role_id: role.json for role in self.roles}
        return result


# pylint: disable=too-many-instance-attributes
class RoleDetail:
    """Processes an entry under RoleDetailList"""

    def __init__(
        self,
        role_detail: dict[str, Any],
        policy_details: ManagedPolicyDetails,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
        flag_conditional_statements: bool = False,
        flag_resource_arn_statements: bool = False,
        severity: list[str] | None = None,
    ) -> None:
        """
        Initialize the RoleDetail object.

        :param role_detail: Details about a particular Role
        :param policy_details: The ManagedPolicyDetails object - i.e., details about all managed policies in the account
        so the role can inherit those attributes
        """
        # Metadata
        self.path = role_detail["Path"]
        self.role_name = role_detail["RoleName"]
        self.role_id = role_detail["RoleId"]
        self.arn = role_detail.get("Arn")
        self.create_date = role_detail.get("CreateDate")
        self.tags = role_detail.get("Tags")
        self.role_last_used = role_detail.get("RoleLastUsed", {}).get("LastUsedDate")
        self.role_detail = role_detail  # just to reference later in debugging
        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.is_excluded = self._is_excluded(exclusions)
        # Fix Issue #254 - Allow flagging risky actions even when there are resource constraints
        self.flag_conditional_statements = flag_conditional_statements
        self.flag_resource_arn_statements = flag_resource_arn_statements

        self.iam_data: dict[str, dict[Any, Any]] = {
            "groups": {},
            "users": {},
            "roles": {},
        }

        # Metadata in object form
        self.assume_role_policy_document = None
        assume_role_policy = role_detail.get("AssumeRolePolicyDocument")
        if assume_role_policy:
            self.assume_role_policy_document = AssumeRolePolicyDocument(assume_role_policy)

        # TODO: Create a class for InstanceProfileList
        self.instance_profile_list = role_detail.get("InstanceProfileList", [])

        # Inline Policies
        self.inline_policies = []
        # If the role itself is NOT excluded, add its inline policies
        if not self.is_excluded:
            for policy_detail in role_detail.get("RolePolicyList", []):
                policy_name = policy_detail.get("PolicyName")
                policy_document = policy_detail.get("PolicyDocument")
                policy_id = get_non_provider_id(json.dumps(policy_document))
                if not (exclusions.is_policy_excluded(policy_name) or exclusions.is_policy_excluded(policy_id)):
                    inline_policy = InlinePolicy(
                        policy_detail,
                        exclusions=exclusions,
                        flag_conditional_statements=flag_conditional_statements,
                        flag_resource_arn_statements=flag_resource_arn_statements,
                        severity=severity,
                    )
                    self.inline_policies.append(inline_policy)

        # Managed Policies (either AWS-managed or Customer managed)
        self.attached_managed_policies = []
        # If the role itself is NOT excluded, add its AWS-managed or Customer-managed policies
        if not self.is_excluded:
            for policy in role_detail.get("AttachedManagedPolicies", []):
                arn = policy.get("PolicyArn")
                if not (
                    exclusions.is_policy_excluded(arn)
                    or exclusions.is_policy_excluded(get_full_policy_path(arn))
                    or exclusions.is_policy_excluded(get_policy_name(arn))
                ):
                    try:
                        attached_managed_policy_details = policy_details.get_policy_detail(arn)
                        self.attached_managed_policies.append(attached_managed_policy_details)
                    except NotFoundException as e:
                        utils.print_red(f"\tError in role {self.role_name}: {e}")

    def set_iam_data(self, iam_data: dict[str, dict[Any, Any]]) -> None:
        self.iam_data = iam_data
        for inline_policy in self.inline_policies:
            inline_policy.set_iam_data(iam_data)

    def _is_excluded(self, exclusions: Exclusions) -> bool:
        """Determine whether the principal name or principal ID is excluded"""
        return (
            exclusions.is_principal_excluded(self.role_name, "Role")
            or exclusions.is_principal_excluded(self.role_id, "Role")
            or exclusions.is_principal_excluded(self.path, "Role")
            or is_name_excluded(self.path, "/aws-service-role*")
        )

    @property
    def all_allowed_actions(self) -> list[str]:
        """Return a list of which actions are allowed by the principal"""
        actions = set()
        for managed_policy in self.attached_managed_policies:
            actions.update(managed_policy.policy_document.all_allowed_actions)
        for inline_policy in self.inline_policies:
            actions.update(inline_policy.policy_document.all_allowed_actions)
        return sorted(actions)

    @property
    def all_iam_statements(self) -> list[StatementDetail]:
        """Return a list of which actions are allowed by the principal"""
        statements = set()
        for managed_policy in self.attached_managed_policies:
            statements.update(managed_policy.policy_document.statements)
        for inline_policy in self.inline_policies:
            statements.update(inline_policy.policy_document.statements)
        return list(statements)

    @property
    def attached_managed_policies_json(self) -> dict[str, dict[str, Any]]:
        """Return JSON representation of attached managed policies"""
        policies = {}
        for policy in self.attached_managed_policies:
            try:
                policies[policy.policy_id] = policy.json_large
            except AttributeError as a_e:  # noqa: PERF203
                print(a_e)
        return policies

    @property
    def attached_managed_policies_pointer_json(self) -> dict[str, str]:
        """Return JSON representation of attached managed policies - but just with pointers to the Policy ID"""
        policies = {}
        for policy in self.attached_managed_policies:
            try:
                policies[policy.policy_id] = policy.policy_name
            except AttributeError as a_e:  # noqa: PERF203
                print(a_e)
        return policies

    @property
    def attached_customer_managed_policies_pointer_json(self) -> dict[str, str]:
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {
            policy.policy_id: policy.policy_name
            for policy in self.attached_managed_policies
            if not is_aws_managed(policy.arn)
        }
        return policies

    @property
    def attached_aws_managed_policies_pointer_json(self) -> dict[str, str]:
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {
            policy.policy_id: policy.policy_name
            for policy in self.attached_managed_policies
            if is_aws_managed(policy.arn)
        }
        return policies

    @property
    def all_infrastructure_modification_actions_by_inline_policies(self) -> list[str]:
        """Return a list of all infrastructure modification actions allowed by all inline policies in violation."""
        result = set()
        for policy in self.inline_policies:
            result.update(policy.policy_document.infrastructure_modification)
        return sorted(result)

    @property
    def inline_policies_json(self) -> dict[str, dict[str, Any]]:
        """Return JSON representation of attached inline policies"""
        policies = {policy.policy_id: policy.json_large for policy in self.inline_policies}
        return policies

    @property
    def inline_policies_pointer_json(self) -> dict[str, str]:
        """Return metadata on attached inline policies so you can look it up in the policies section later."""
        policies = {policy.policy_id: policy.policy_name for policy in self.inline_policies}
        return policies

    @property
    def json(self) -> dict[str, Any]:
        """Return the JSON representation of the Role Detail"""
        assume_role_json = self.assume_role_policy_document.json if self.assume_role_policy_document else {}
        this_role_detail = dict(
            arn=self.arn,
            assume_role_policy=dict(PolicyDocument=assume_role_json),
            create_date=self.create_date,
            role_last_used=self.role_last_used,
            id=self.role_id,
            name=self.role_name,
            inline_policies=self.inline_policies_pointer_json,
            instance_profiles=self.instance_profile_list,
            instances_count=len(self.instance_profile_list),
            path=self.path,
            customer_managed_policies=self.attached_customer_managed_policies_pointer_json,
            aws_managed_policies=self.attached_aws_managed_policies_pointer_json,
            is_excluded=self.is_excluded,
        )
        return this_role_detail
