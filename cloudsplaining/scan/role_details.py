"""Processes RoleDetailList"""
from cloudsplaining.scan.assume_role_policy_document import AssumeRolePolicyDocument
from cloudsplaining.scan.inline_policy import InlinePolicy
from cloudsplaining.shared.utils import is_aws_managed


class RoleDetailList:
    """Processes all entries under the RoleDetailList"""

    def __init__(self, role_details, policy_details):
        self.roles = []
        for role_detail in role_details:
            self.roles.append(RoleDetail(role_detail, policy_details))

    def get_all_allowed_actions_for_role(self, name):
        """Returns a list of all allowed actions by the role across all its policies"""
        result = None
        for role_detail in self.roles:
            if role_detail.role_name == name:
                result = role_detail.all_allowed_actions
                break
        return result

    def get_all_iam_statements_for_role(self, name):
        """Returns a list of all StatementDetail objects across all the policies assigned to the role"""
        result = None
        for role_detail in self.roles:
            if role_detail.role_name == name:
                result = role_detail.all_iam_statements
                break
        return result

    @property
    def role_names(self):
        """Get a list of all role names in the account"""
        results = []
        for role_detail in self.roles:
            results.append(role_detail.role_name)
        results.sort()
        return results

    @property
    def inline_policies_json(self):
        """Return JSON representation of attached inline policies"""
        results = {}
        for role_detail in self.roles:
            role_inline_policies = role_detail.inline_policies_json
            if role_inline_policies:
                for k in role_inline_policies:
                    if k not in results.keys():
                        results[k] = role_inline_policies[k].copy()
        return results

    @property
    def json(self):
        """Get all JSON results"""
        result = {}
        for role in self.roles:
            result[role.role_id] = role.json
        return result


# pylint: disable=too-many-instance-attributes
class RoleDetail:
    """Processes an entry under RoleDetailList"""

    def __init__(self, role_detail, policy_details):
        """
        Initialize the RoleDetail object.

        :param role_detail: Details about a particular Role
        :param policy_details: The ManagedPolicyDetails object - i.e., details about all managed policies in the account
        so the role can inherit those attributes
        """
        # Metadata
        self.path = role_detail.get("Path")
        self.role_name = role_detail.get("RoleName")
        self.role_id = role_detail.get("RoleId")
        self.arn = role_detail.get("Arn")
        self.create_date = role_detail.get("CreateDate")
        self.tags = role_detail.get("Tags")
        self.role_last_used = role_detail.get("RoleLastUsed")
        self.role_detail = role_detail  # just to reference later in debugging

        # Metadata in object form
        if role_detail.get("AssumeRolePolicyDocument"):
            self.assume_role_policy_document = AssumeRolePolicyDocument(role_detail.get("AssumeRolePolicyDocument"))
        else:
            self.assume_role_policy_document = None

        # TODO: Create a class for InstanceProfileList
        self.instance_profile_list = role_detail.get("InstanceProfileList")

        # Inline Policies
        self.inline_policies = []
        if role_detail.get("RolePolicyList"):
            self._inline_policies_details(
                role_detail.get("RolePolicyList")
            )

        # Managed Policies (either AWS-managed or Customer managed)
        self.attached_managed_policies = []
        if role_detail.get("AttachedManagedPolicies"):
            self._attached_managed_policies_details(
                role_detail.get("AttachedManagedPolicies"),
                policy_details
            )

    def _attached_managed_policies_details(self, attached_managed_policies_list, policy_details):
        if attached_managed_policies_list:
            for policy in attached_managed_policies_list:
                arn = policy.get("PolicyArn")
                attached_managed_policy_details = policy_details.get_policy_detail(arn)
                self.attached_managed_policies.append(attached_managed_policy_details)

    def _inline_policies_details(self, group_policies_list):
        if group_policies_list:
            for policy in group_policies_list:
                inline_policy = InlinePolicy(policy)
                self.inline_policies.append(inline_policy)

    @property
    def all_allowed_actions(self):
        """Return a list of which actions are allowed by the principal"""
        actions = []
        for managed_policy in self.attached_managed_policies:
            actions.extend(managed_policy.policy_document.all_allowed_actions)
        for inline_policy in self.inline_policies:
            actions.extend(self.inline_policies[inline_policy]["PolicyDocument"].all_allowed_actions)
        actions = list(dict.fromkeys(actions))
        actions.sort()
        return actions

    @property
    def all_iam_statements(self):
        """Return a list of which actions are allowed by the principal"""
        statements = []
        for managed_policy in self.attached_managed_policies:
            statements.extend(managed_policy.policy_document.statements)
        for inline_policy in self.inline_policies:
            statements.extend(self.inline_policies[inline_policy]["PolicyDocument"].statements)
        return statements

    @property
    def consolidated_risks(self):
        """Return a dict containing the consolidated risks from all inline and managed policies"""
        privilege_escalation_results = {}
        resource_exposure_results = []
        data_exfiltration_results = []

        # Get it from each inline policy
        if self.inline_policies:
            for inline_policy in self.inline_policies:
                # Privilege Escalation
                if inline_policy.policy_document.allows_privilege_escalation:
                    for entry in inline_policy.policy_document.allows_privilege_escalation:
                        if entry["type"] not in privilege_escalation_results.keys():
                            privilege_escalation_results[entry["type"]] = entry["actions"]
                # Resource Exposure
                if inline_policy.policy_document.permissions_management_without_constraints:
                    for action in inline_policy.policy_document.permissions_management_without_constraints:
                        if action not in resource_exposure_results:
                            resource_exposure_results.append(action)
                # Data Exfiltration
                if inline_policy.policy_document.allows_data_exfiltration_actions:
                    for action in inline_policy.policy_document.allows_data_exfiltration_actions:
                        if action not in data_exfiltration_results:
                            data_exfiltration_results.append(action)

        if self.attached_managed_policies:
            for managed_policy in self.attached_managed_policies:
                # Privilege Escalation
                if managed_policy.policy_document.allows_privilege_escalation:
                    for entry in managed_policy.policy_document.allows_privilege_escalation:
                        if entry["type"] not in privilege_escalation_results.keys():
                            privilege_escalation_results[entry["type"]] = entry["actions"]
                # Resource Exposure
                if managed_policy.policy_document.permissions_management_without_constraints:
                    for action in managed_policy.policy_document.permissions_management_without_constraints:
                        if action not in resource_exposure_results:
                            resource_exposure_results.append(action)
                # Data Exfiltration
                if managed_policy.policy_document.allows_data_exfiltration_actions:
                    for action in managed_policy.policy_document.allows_data_exfiltration_actions:
                        if action not in data_exfiltration_results:
                            data_exfiltration_results.append(action)

        # turn it into a list because we want to be able to count the number of results
        these_privilege_escalation_results = []

        for key in privilege_escalation_results:
            result = {
                "type": key,
                "actions": privilege_escalation_results[key]
            }
            these_privilege_escalation_results.append(result)

        # Let's just return the count
        results = {
            "PrivilegeEscalation": len(these_privilege_escalation_results),
            "ResourceExposure": len(resource_exposure_results),
            "DataExfiltration": len(data_exfiltration_results),
        }

        return results

    @property
    def attached_managed_policies_json(self):
        """Return JSON representation of attached managed policies"""
        policies = {}
        if self.attached_managed_policies:
            for policy in self.attached_managed_policies:
                try:
                    policies[policy.policy_id] = policy.json_large
                except AttributeError as a_e:
                    print(a_e)
        return policies

    @property
    def attached_managed_policies_pointer_json(self):
        """Return JSON representation of attached managed policies - but just with pointers to the Policy ID"""
        policies = {}
        if self.attached_managed_policies:
            for policy in self.attached_managed_policies:
                try:
                    policies[policy.policy_id] = policy.policy_name
                except AttributeError as a_e:
                    print(a_e)
        return policies

    @property
    def attached_customer_managed_policies_pointer_json(self):
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {}
        for policy in self.attached_managed_policies:
            if not is_aws_managed(policy.arn):
                policies[policy.policy_id] = policy.policy_name
        return policies

    @property
    def attached_aws_managed_policies_pointer_json(self):
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {}
        for policy in self.attached_managed_policies:
            if is_aws_managed(policy.arn):
                policies[policy.policy_id] = policy.policy_name
        return policies

    @property
    def inline_policies_json(self):
        """Return JSON representation of attached inline policies"""
        policies = {}
        if self.inline_policies:
            for policy in self.inline_policies:
                policies[policy.policy_id] = policy.json_large
        return policies

    @property
    def inline_policies_pointer_json(self):
        """Return metadata on attached inline policies so you can look it up in the policies section later."""
        policies = {}
        for policy in self.inline_policies:
            policies[policy.policy_id] = policy.policy_name
        return policies

    @property
    def json(self):
        """Return the JSON representation of the Role Detail"""
        if self.assume_role_policy_document:
            assume_role_json = self.assume_role_policy_document.json
        else:
            assume_role_json = {}
        this_role_detail = dict(
            arn=self.arn,
            assume_role_policy=dict(PolicyDocument=assume_role_json),
            create_date=self.create_date,
            id=self.role_id,
            name=self.role_name,
            inline_policies=self.inline_policies_pointer_json,
            instance_profiles=self.instance_profile_list,
            instances_count=len(self.instance_profile_list),
            path=self.path,
            customer_managed_policies=self.attached_customer_managed_policies_pointer_json,
            aws_managed_policies=self.attached_aws_managed_policies_pointer_json,
            # managed_policies=self.attached_managed_policies_pointer_json,
        )
        return this_role_detail
