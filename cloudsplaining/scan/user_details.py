"""Processes UserDetailList"""
from cloudsplaining.scan.inline_policy import InlinePolicy


class UserDetailList:
    """Processes all entries under the UserDetailList"""

    def __init__(self, user_details, policy_details, all_group_details):
        self.users = []
        for user_detail in user_details:
            self.users.append(UserDetail(user_detail, policy_details, all_group_details))

    def get_all_allowed_actions_for_user(self, name):
        """Returns a list of all allowed actions by the user across all its policies"""
        result = None
        for user_detail in self.users:
            if user_detail.user_name == name:
                result = user_detail.all_allowed_actions
                break
        return result

    def get_all_iam_statements_for_user(self, name):
        """Returns a list of all StatementDetail objects across all the policies assigned to the user"""
        result = None
        for user_detail in self.users:
            if user_detail.user_name == name:
                result = user_detail.all_iam_statements
                break
        return result

    @property
    def user_names(self):
        """Get a list of all user names in the account"""
        results = []
        for user_detail in self.users:
            results.append(user_detail.user_name)
        results.sort()
        return results

    @property
    def inline_policies_json(self):
        """Return JSON representation of attached inline policies"""
        results = {}
        for user_detail in self.users:
            user_inline_policies = user_detail.inline_policies_json
            if user_inline_policies:
                for k in user_inline_policies:
                    if k not in results.keys():
                        results[k] = user_inline_policies[k].copy()
        return results

    @property
    def json(self):
        """Get all JSON results"""
        result = {}
        for user in self.users:
            result[user.user_id] = user.json
        return result


# pylint: disable=too-many-instance-attributes,unused-argument
class UserDetail:
    """Processes an entry under UserDetailList"""

    def __init__(self, user_detail, policy_details, all_group_details):
        """
        Initialize the UserDetail object.

        :param user_detail: Details about a particular user
        :param policy_details: The ManagedPolicyDetails object - i.e., details about all managed policies in the account
        so the user can inherit those attributes
        :param all_group_details:
        """
        self.create_date = user_detail.get("CreateDate")
        self.arn = user_detail.get("Arn")
        self.path = user_detail.get("Path")
        self.user_id = user_detail.get("UserId")
        self.user_name = user_detail.get("UserName")

        # Groups
        self.groups = []
        if user_detail.get("GroupList"):
            self._add_group_details(
                user_detail.get("GroupList"),
                all_group_details
            )
        # self.inline_policies = user_detail.get("UserPolicyList")
        # self.groups = user_detail.get("GroupList")

        # Inline Policies
        self.inline_policies = []
        if user_detail.get("UserPolicyList"):
            self._inline_policies_details(
                user_detail.get("UserPolicyList")
            )

        # Managed Policies (either AWS-managed or Customer managed)
        self.attached_managed_policies = []
        if user_detail.get("AttachedManagedPolicies"):
            self._attached_managed_policies_details(
                user_detail.get("AttachedManagedPolicies"),
                policy_details
            )

    def _add_group_details(self, group_list, all_group_details):
        for group in group_list:
            this_group_detail = all_group_details.get_group_detail(group)
            self.groups.append(this_group_detail)

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
        actions = []
        for managed_policy in self.attached_managed_policies:
            actions.extend(managed_policy.policy_document.all_allowed_actions)
        for inline_policy in self.inline_policies:
            actions.extend(inline_policy.policy_document.all_allowed_actions)
        for group in self.groups:
            actions.extend(group.all_allowed_actions)
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
            statements.extend(inline_policy.policy_document.statements)
        for group in self.groups:
            statements.extend(group.all_iam_statements)
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
            policies[policy.policy_id] = policy.json
        return policies

    @property
    def attached_managed_policies_pointer_json(self):
        """Return JSON representation of attached managed policies - but just with pointers to the Policy ID"""
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
    def groups_json(self):
        """Return JSON representation of group object"""
        these_groups = {}
        if self.groups:
            for group in self.groups:
                # TODO: Change this to a group pointer?
                these_groups[group.group_name] = group.json
        return these_groups

    @property
    def json(self):
        """Return the JSON representation of the User Detail"""

        this_user_detail = dict(
            arn=self.arn,
            create_date=self.create_date,
            id=self.user_id,
            inline_policies=self.inline_policies_pointer_json,
            # inline_policies_count=len(self.inline_policies_pointer_json),
            # groups=self.groups,
            groups=self.groups_json,
            path=self.path,
            # managed_policies_count=len(self.attached_managed_policies),
            managed_policies=self.attached_managed_policies_pointer_json,
            # risks=self.consolidated_risks
        )
        return this_user_detail
