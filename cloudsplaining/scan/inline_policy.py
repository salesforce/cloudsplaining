"""Represents the Inline Policies (UserPolicyList, GroupPolicyList, RolePolicyList) entries under each principal."""
from cloudsplaining.shared.utils import get_non_provider_id
from cloudsplaining.scan.policy_document import PolicyDocument


class InlinePolicy:
    """
    Contains information about an Inline Policy, including the Policy Document
    """

    def __init__(self, policy_detail):
        """
        Initialize the InlinePolicy object.

        :param policy_detail: The JSON containing the PolicyName and PolicyDocument
        """
        self.policy_name = policy_detail.get("PolicyName")
        self.policy_document = PolicyDocument(policy_detail.get("PolicyDocument"))
        self.policy_id = get_non_provider_id(self.policy_name)

    @property
    def json(self):
        """Return JSON output for high risk actions"""
        result = dict(
            PolicyName=self.policy_name,
            PolicyId=self.policy_id,
            PrivilegeEscalation=self.policy_document.allows_privilege_escalation,
            DataExfiltrationActions=self.policy_document.allows_data_leak_actions,
            PermissionsManagementActions=self.policy_document.permissions_management_without_constraints,
        )
        return result

    @property
    def json_large(self):
        """Return JSON output - including Infra Modification actions, which can be large"""
        result = dict(
            PolicyName=self.policy_name,
            PolicyId=self.policy_id,
            PrivilegeEscalation=self.policy_document.allows_privilege_escalation,
            DataExfiltrationActions=self.policy_document.allows_data_leak_actions,
            PermissionsManagementActions=self.policy_document.permissions_management_without_constraints,
            InfrastructureModification=self.policy_document.all_allowed_unrestricted_actions
        )
        return result
