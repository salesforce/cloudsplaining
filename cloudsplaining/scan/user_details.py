"""Processes UserDetailList"""
import json
from typing import List, Dict, Any, Optional

from cloudsplaining.scan.group_details import GroupDetailList, GroupDetail
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


class UserDetailList:
    """Processes all entries under the UserDetailList"""

    def __init__(
        self,
        user_details: List[Dict[str, Any]],
        policy_details: ManagedPolicyDetails,
        all_group_details: GroupDetailList,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ) -> None:
        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.exclusions = exclusions

        self.users = [
            UserDetail(user_detail, policy_details, all_group_details, exclusions)
            for user_detail in user_details
        ]

    def get_all_allowed_actions_for_user(self, name: str) -> Optional[List[str]]:
        """Returns a list of all allowed actions by the user across all its policies"""
        for user_detail in self.users:
            if user_detail.user_name == name:
                return user_detail.all_allowed_actions
        return None

    def get_all_iam_statements_for_user(
        self, name: str
    ) -> Optional[List[StatementDetail]]:
        """Returns a list of all StatementDetail objects across all the policies assigned to the user"""
        for user_detail in self.users:
            if user_detail.user_name == name:
                return user_detail.all_iam_statements
        return None

    @property
    def user_names(self) -> List[str]:
        """Get a list of all user names in the account"""
        results = [user_detail.user_name for user_detail in self.users]
        results.sort()
        return results

    @property
    def all_infrastructure_modification_actions_by_inline_policies(self) -> List[str]:
        """Return a list of all infrastructure modification actions allowed by all inline policies in violation."""
        result = set()
        for user in self.users:
            for policy in user.inline_policies:
                result.update(policy.policy_document.infrastructure_modification)
        return sorted(result)

    @property
    def inline_policies_json(self) -> Dict[str, Dict[str, Any]]:
        """Return JSON representation of attached inline policies"""
        results = {}
        for user_detail in self.users:
            results.update(user_detail.inline_policies_json)
        return results

    @property
    def json(self) -> Dict[str, Dict[str, Any]]:
        """Get all JSON results"""
        result = {user.user_id: user.json for user in self.users}
        return result


# pylint: disable=too-many-instance-attributes,unused-argument
class UserDetail:
    """Processes an entry under UserDetailList"""

    def __init__(
        self,
        user_detail: Dict[str, Any],
        policy_details: ManagedPolicyDetails,
        all_group_details: GroupDetailList,
        exclusions: Exclusions = DEFAULT_EXCLUSIONS,
    ) -> None:
        """
        Initialize the UserDetail object.

        :param user_detail: Details about a particular user
        :param policy_details: The ManagedPolicyDetails object - i.e., details about all managed policies in the account
        so the user can inherit those attributes
        :param all_group_details:
        """
        self.create_date = user_detail.get("CreateDate")
        self.arn = user_detail.get("Arn")
        self.path = user_detail["Path"]
        self.user_id = user_detail["UserId"]
        self.user_name = user_detail["UserName"]

        if not isinstance(exclusions, Exclusions):
            raise Exception(
                "The exclusions provided is not an Exclusions type object. "
                "Please supply an Exclusions object and try again."
            )
        self.is_excluded = self._is_excluded(exclusions)

        # Groups
        self.groups: List[GroupDetail] = []
        group_list = user_detail.get("GroupList")
        if group_list:
            self._add_group_details(group_list, all_group_details)
        # self.inline_policies = user_detail.get("UserPolicyList")
        # self.groups = user_detail.get("GroupList")

        # Inline Policies
        self.inline_policies = []
        # If the user itself is NOT excluded, add its inline policies
        if not self.is_excluded:
            for policy_detail in user_detail.get("UserPolicyList", []):
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
        # If the user itself is NOT excluded, add its AWS-managed or Customer-managed policies
        if not self.is_excluded:
            for policy in user_detail.get("AttachedManagedPolicies", []):
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
        return bool(
            exclusions.is_principal_excluded(self.user_name, "User")
            or exclusions.is_principal_excluded(self.user_id, "User")
            or exclusions.is_principal_excluded(self.path, "User")
        )

    def _add_group_details(
        self, group_list: List[str], all_group_details: GroupDetailList
    ) -> None:
        for group in group_list:
            this_group_detail = all_group_details.get_group_detail(group)
            if this_group_detail:
                self.groups.append(this_group_detail)

    @property
    def all_allowed_actions(self) -> List[str]:
        """Return a list of which actions are allowed by the principal"""
        actions = set()
        for managed_policy in self.attached_managed_policies:
            actions.update(managed_policy.policy_document.all_allowed_actions)
        for inline_policy in self.inline_policies:
            actions.update(inline_policy.policy_document.all_allowed_actions)
        for group in self.groups:
            actions.update(group.all_allowed_actions)
        return sorted(actions)

    @property
    def all_iam_statements(self) -> List[StatementDetail]:
        """Return a list of which actions are allowed by the principal"""
        statements = set()
        for managed_policy in self.attached_managed_policies:
            statements.update(managed_policy.policy_document.statements)
        for inline_policy in self.inline_policies:
            statements.update(inline_policy.policy_document.statements)
        for group in self.groups:
            statements.update(group.all_iam_statements)
        return list(statements)

    @property
    def attached_managed_policies_json(self) -> Dict[str, Dict[str, Any]]:
        """Return JSON representation of attached managed policies"""
        policies = {
            policy.policy_id: policy.json for policy in self.attached_managed_policies
        }
        return policies

    @property
    def attached_managed_policies_pointer_json(self) -> Dict[str, str]:
        """Return JSON representation of attached managed policies - but just with pointers to the Policy ID"""
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
    def groups_json(self) -> Dict[str, Dict[str, Any]]:
        """Return JSON representation of group object"""
        these_groups = {
            group.group_name: group.json  # TODO: Change this to a group pointer?
            for group in self.groups
        }
        return these_groups

    @property
    def json(self) -> Dict[str, Any]:
        """Return the JSON representation of the User Detail"""

        this_user_detail = dict(
            arn=self.arn,
            create_date=self.create_date,
            id=self.user_id,
            name=self.user_name,
            inline_policies=self.inline_policies_pointer_json,
            groups=self.groups_json,
            path=self.path,
            customer_managed_policies=self.attached_customer_managed_policies_pointer_json,
            aws_managed_policies=self.attached_aws_managed_policies_pointer_json,
            is_excluded=self.is_excluded,
        )
        return this_user_detail
