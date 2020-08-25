"""Processes an entry under GroupDetailList"""
from cloudsplaining.scan.inline_policy import InlinePolicy


class GroupDetailList:
    """Processes all entries under the GroupDetailList"""
    def __init__(self, group_details, policy_details):
        self.groups = []
        for group_detail in group_details:
            self.groups.append(GroupDetail(group_detail, policy_details))

    def get_group_detail(self, name):
        """Get a GroupDetail object by providing the Name of the group. This is useful to UserDetail objects"""
        result = None
        for group_detail in self.groups:
            if group_detail.group_name == name:
                result = group_detail
                break
        return result

    def get_all_allowed_actions_for_group(self, name):
        """Returns a list of all allowed actions by the group across all its policies"""
        result = None
        for group_detail in self.groups:
            if group_detail.group_name == name:
                result = group_detail.all_allowed_actions
                break
        return result

    def get_all_iam_statements_for_group(self, name):
        """Returns a list of all StatementDetail objects across all the policies assigned to the group"""
        result = None
        for group_detail in self.groups:
            if group_detail.group_name == name:
                result = group_detail.all_iam_statements
                break
        return result

    @property
    def group_names(self):
        """Get a list of all group names in the account"""
        results = []
        for group_detail in self.groups:
            results.append(group_detail.group_name)
        results.sort()
        return results

    @property
    def inline_policies_json(self):
        """Return JSON representation of attached inline policies"""
        results = {}
        for group_detail in self.groups:
            group_inline_policies = group_detail.inline_policies_json
            if group_inline_policies:
                for k in group_inline_policies:
                    if k not in results.keys():
                        results[k] = group_inline_policies[k].copy()
        return results

    @property
    def json(self):
        """Get all JSON results"""
        result = {}
        for group in self.groups:
            result[group.group_id] = group.json
        return result


class GroupDetail:
    """Processes an entry under GroupDetailList"""
    def __init__(self, group_detail, policy_details):
        """
        Initialize the GroupDetail object.

        :param group_detail: Details about a particular group
        :param policy_details: The ManagedPolicyDetails object - i.e., details about all managed policies in the account so the group can inherit those attributes
        """
        self.create_date = group_detail.get("CreateDate")
        self.arn = group_detail.get("Arn")
        self.path = group_detail.get("Path")
        self.group_id = group_detail.get("GroupId")
        self.group_name = group_detail.get("GroupName")

        # Inline Policies
        self.inline_policies = []
        if group_detail.get("GroupPolicyList"):
            self._inline_policies_details(
                group_detail.get("GroupPolicyList")
            )

        # Managed Policies (either AWS-managed or Customer managed)
        self.attached_managed_policies = []
        if group_detail.get("AttachedManagedPolicies"):
            self._attached_managed_policies_details(
                group_detail.get("AttachedManagedPolicies"),
                policy_details
            )

    def _attached_managed_policies_details(self, attached_managed_policies_list, policy_details):
        for policy in attached_managed_policies_list:
            arn = policy.get("PolicyArn")
            attached_managed_policy_details = policy_details.get_policy_detail(arn)
            self.attached_managed_policies.append(attached_managed_policy_details)

    def _inline_policies_details(self, group_policies_list):
        for policy in group_policies_list:
            inline_policy = InlinePolicy(policy)
            self.inline_policies.append(inline_policy)

    @property
    def all_allowed_actions(self):
        """Return a list of which actions are allowed by the principal"""
        privileges = []
        for managed_policy in self.attached_managed_policies:
            privileges.extend(managed_policy.policy_document.all_allowed_actions)
        for inline_policy in self.inline_policies:
            privileges.extend(inline_policy.policy_document.all_allowed_actions)
        return privileges

    @property
    def all_iam_statements(self):
        """Return a list of which actions are allowed by the principal"""
        statements = []
        for managed_policy in self.attached_managed_policies:
            statements.extend(managed_policy.policy_document.statements)
        for inline_policy in self.inline_policies:
            statements.extend(inline_policy.policy_document.statements)
        return statements

    @property
    def consolidated_risks(self):
        """Return a dict containing the consolidated risks from all inline and managed policies for the group"""
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
                if inline_policy.policy_document.allows_data_leak_actions:
                    for action in inline_policy.policy_document.allows_data_leak_actions:
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
                if managed_policy.policy_document.allows_data_leak_actions:
                    for action in managed_policy.policy_document.allows_data_leak_actions:
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

        # resource_exposure_results.sort()
        # data_exfiltration_results.sort()

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
        for policy in self.attached_managed_policies:
            policies[policy.policy_id] = policy.json_large
        return policies

    @property
    def attached_managed_policies_pointer_json(self):
        """Return metadata on attached managed policies so you can look it up in the policies section later."""
        policies = {}
        for policy in self.attached_managed_policies:
            policies[policy.policy_id] = policy.policy_name
        return policies

    @property
    def inline_policies_json(self):
        """Return JSON representation of attached inline policies"""
        policies = {}
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
        """Return the JSON representation of the Group Detail"""
        this_group_detail = dict(
            arn=self.arn,
            create_date=self.create_date,
            id=self.group_id,
            inline_policies=self.inline_policies_pointer_json,
            inline_policies_count=len(self.inline_policies_pointer_json),
            path=self.path,
            managed_policies_count=len(self.attached_managed_policies),
            managed_policies=self.attached_managed_policies_pointer_json,
            # risks=self.consolidated_risks
        )
        return this_group_detail
