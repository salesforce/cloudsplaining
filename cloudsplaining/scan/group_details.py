"""Processes an entry under GroupDetailList"""
import json
from typing import Optional, Dict, Any, List

from cloudsplaining.scan.inline_policy import InlinePolicy
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails
from cloudsplaining.scan.statement_detail import StatementDetail
from cloudsplaining.shared.utils import (
    is_aws_managed,
    get_full_policy_path,
    get_policy_name,
    get_non_provider_id,
)
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions


class GroupDetailList:
    """Processes all entries under the GroupDetailList"""

    def __init__(
        self,
        group_details: List[Dict[str, Any]],
        policy_details: ManagedPolicyDetails,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ) -> None:
        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.exclusions = exclusions

        self.groups = [
            GroupDetail(group_detail, policy_details, exclusions)
            for group_detail in group_details
        ]

    def get_group_detail(self, name: str) -> Optional["GroupDetail"]:
        """Get a GroupDetail object by providing the Name of the group. This is useful to UserDetail objects"""
        for group_detail in self.groups:
            if group_detail.group_name == name:
                return group_detail
        return None

    def get_all_allowed_actions_for_group(self, name: str) -> Optional[List[str]]:
        """Returns a list of all allowed actions by the group across all its policies"""
        for group_detail in self.groups:
            if group_detail.group_name == name:
                return group_detail.all_allowed_actions
        return None

    def get_all_iam_statements_for_group(
        self, name: str
    ) -> Optional[List[StatementDetail]]:
        """Returns a list of all StatementDetail objects across all the policies assigned to the group"""
        for group_detail in self.groups:
            if group_detail.group_name == name:
                return group_detail.all_iam_statements
        return None

    @property
    def group_names(self) -> List[str]:
        """Get a list of all group names in the account"""
        results = [group_detail.group_name for group_detail in self.groups]
        results.sort()
        return results

    @property
    def all_infrastructure_modification_actions_by_inline_policies(self) -> List[str]:
        """Return a list of all infrastructure modification actions allowed by all inline policies in violation."""
        result = set()
        for group in self.groups:
            for policy in group.inline_policies:
                result.update(policy.policy_document.infrastructure_modification)
        return sorted(result)

    @property
    def inline_policies_json(self) -> Dict[str, Dict[str, Any]]:
        """Return JSON representation of attached inline policies"""
        results = {}
        for group_detail in self.groups:
            results.update(group_detail.inline_policies_json)
        return results

    @property
    def json(self) -> Dict[str, Dict[str, Any]]:
        """Get all JSON results"""
        result = {group.group_id: group.json for group in self.groups}
        return result


# pylint: disable=too-many-instance-attributes
class GroupDetail:
    """Processes an entry under GroupDetailList"""

    def __init__(
        self,
        group_detail: Dict[str, Any],
        policy_details: ManagedPolicyDetails,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ):
        """
        Initialize the GroupDetail object.

        :param group_detail: Details about a particular group
        :param policy_details: The ManagedPolicyDetails object - i.e., details about all managed policies in the account so the group can inherit those attributes
        """
        self.create_date = group_detail.get("CreateDate")
        self.arn = group_detail.get("Arn")
        self.path = group_detail["Path"]
        self.group_id = group_detail["GroupId"]
        self.group_name = group_detail["GroupName"]

        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.is_excluded = self._is_excluded(exclusions)

        # Inline Policies
        self.inline_policies = []
        # If the group itself is NOT excluded, add its inline policies
        if not self.is_excluded:
            for policy_detail in group_detail.get("GroupPolicyList", []):
                policy_name = policy_detail.get("PolicyName")
                policy_document = policy_detail.get("PolicyDocument")
                policy_id = get_non_provider_id(json.dumps(policy_document))
                if not (
                    exclusions.is_policy_excluded(policy_name)
                    or exclusions.is_policy_excluded(policy_id)
                ):
                    inline_policy = InlinePolicy(policy_detail)
                    self.inline_policies.append(inline_policy)

        # Managed Policies (either AWS-managed or Customer managed)
        self.attached_managed_policies = []
        # If the group itself is NOT excluded, add its AWS-managed or Customer-managed policies
        if not self.is_excluded:
            for policy in group_detail.get("AttachedManagedPolicies", []):
                arn = policy.get("PolicyArn")
                if not (
                    exclusions.is_policy_excluded(arn)
                    or exclusions.is_policy_excluded(get_full_policy_path(arn))
                    or exclusions.is_policy_excluded(get_policy_name(arn))
                ):
                    attached_managed_policy_details = policy_details.get_policy_detail(
                        arn
                    )
                    self.attached_managed_policies.append(
                        attached_managed_policy_details
                    )

    def _is_excluded(self, exclusions: Exclusions) -> bool:
        """Determine whether the principal name or principal ID is excluded"""
        return (
            exclusions.is_principal_excluded(self.group_name, "Group")
            or exclusions.is_principal_excluded(self.group_id, "Group")
            or exclusions.is_principal_excluded(self.path, "Group")
        )

    @property
    def all_allowed_actions(self) -> List[str]:
        """Return a list of which actions are allowed by the principal"""
        actions = set()
        for managed_policy in self.attached_managed_policies:
            actions.update(managed_policy.policy_document.all_allowed_actions)
        for inline_policy in self.inline_policies:
            actions.update(inline_policy.policy_document.all_allowed_actions)
        return sorted(actions)

    @property
    def all_iam_statements(self) -> List[StatementDetail]:
        """Return a list of which actions are allowed by the principal"""
        statements = set()
        for managed_policy in self.attached_managed_policies:
            statements.update(managed_policy.policy_document.statements)
        for inline_policy in self.inline_policies:
            statements.update(inline_policy.policy_document.statements)
        return list(statements)

    @property
    def attached_managed_policies_json(self) -> Dict[str, Dict[str, Any]]:
        """Return JSON representation of attached managed policies"""
        policies = {
            policy.policy_id: policy.json_large
            for policy in self.attached_managed_policies
        }
        return policies

    @property
    def attached_managed_policies_pointer_json(self) -> Dict[str, str]:
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {
            policy.policy_id: policy.policy_name
            for policy in self.attached_managed_policies
        }
        return policies

    @property
    def attached_customer_managed_policies_pointer_json(self) -> Dict[str, str]:
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {
            policy.policy_id: policy.policy_name
            for policy in self.attached_managed_policies
            if not is_aws_managed(policy.arn)
        }
        return policies

    @property
    def attached_aws_managed_policies_pointer_json(self) -> Dict[str, str]:
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {
            policy.policy_id: policy.policy_name
            for policy in self.attached_managed_policies
            if is_aws_managed(policy.arn)
        }
        return policies

    @property
    def all_infrastructure_modification_actions_by_inline_policies(self) -> List[str]:
        """Return a list of all infrastructure modification actions allowed by all inline policies in violation."""
        result = set()
        for policy in self.inline_policies:
            result.update(policy.policy_document.infrastructure_modification)
        return sorted(result)

    @property
    def inline_policies_json(self) -> Dict[str, Dict[str, Any]]:
        """Return JSON representation of attached inline policies"""
        policies = {
            policy.policy_id: policy.json_large for policy in self.inline_policies
        }
        return policies

    @property
    def inline_policies_pointer_json(self) -> Dict[str, str]:
        """Return metadata on attached inline policies so you can look it up in the policies section later."""
        policies = {
            policy.policy_id: policy.policy_name for policy in self.inline_policies
        }
        return policies

    @property
    def json(self) -> Dict[str, Any]:
        """Return the JSON representation of the Group Detail"""
        this_group_detail = dict(
            arn=self.arn,
            name=self.group_name,
            create_date=self.create_date,
            id=self.group_id,
            inline_policies=self.inline_policies_pointer_json,
            path=self.path,
            customer_managed_policies=self.attached_customer_managed_policies_pointer_json,
            aws_managed_policies=self.attached_aws_managed_policies_pointer_json,
            is_excluded=self.is_excluded,
        )
        return this_group_detail
