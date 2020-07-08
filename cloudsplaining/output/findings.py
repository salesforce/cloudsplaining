"""Holds all the finding classes"""
import logging
from operator import itemgetter
from policy_sentry.util.arns import get_resource_string, get_account_from_arn, get_resource_path_from_arn
from cloudsplaining.shared.exclusions import (
    is_name_excluded,
    Exclusions,
    DEFAULT_EXCLUSIONS,
)
from cloudsplaining.shared.constants import READ_ONLY_DATA_LEAK_ACTIONS
from cloudsplaining.shared.utils import capitalize_first_character, get_full_policy_path

logger = logging.getLogger(__name__)


class Findings:
    """Holds all the findings"""

    def __init__(self, exclusions=DEFAULT_EXCLUSIONS):
        self.users = []
        self.roles = []
        self.groups = []
        self.policies = []
        self.exclusions = exclusions
        self.principal_policy_mapping = []
        # Hacky way to determine whether it is running the scan or scan_policy_file command
        self.single_use = False

    def add_user_finding(self, user_finding):
        """Adds a UserFinding object"""
        if not isinstance(user_finding, UserFinding):
            raise Exception("Please supply a UserFinding object")
        if not user_finding.is_excluded(self.exclusions):
            self.users.append(user_finding)

    def add_group_finding(self, group_finding):
        """Adds a GroupFinding object"""
        if not isinstance(group_finding, GroupFinding):
            raise Exception("Please supply a GroupFinding object")
        if not group_finding.is_excluded(self.exclusions):
            self.groups.append(group_finding)

    def add_role_finding(self, role_finding):
        """Adds a RoleFinding object"""
        if not isinstance(role_finding, RoleFinding):
            raise Exception("Please supply a RoleFinding object")
        if not role_finding.is_excluded(self.exclusions):
            self.roles.append(role_finding)

    def add_policy_finding(self, policy_finding):
        """Adds a PolicyFinding object"""
        if not isinstance(policy_finding, PolicyFinding):
            raise Exception("Please supply a PolicyFinding object")
        if not policy_finding.is_excluded(self.exclusions):
            self.policies.append(policy_finding)

    @property
    def valid_principals(self):
        """Get a list of the principals (Users, Groups, Roles) that are used"""
        principals = []
        if self.users:
            for user_finding in self.users:
                principals.append(user_finding.name)
        if self.groups:
            for group_finding in self.groups:
                principals.append(group_finding.name)
        if self.roles:
            for role_finding in self.roles:
                principals.append(role_finding.name)
        return principals

    def policies_in_use(self):
        """Get a list of policy names that are in use"""
        if not self.principal_policy_mapping:
            raise Exception(
                "Set the principal_policy_mapping attribute before running."
            )
        these_policies_in_use = []
        for principal_policy_entry in self.principal_policy_mapping:
            # If they are not excluded:
            if principal_policy_entry.get("Type") == "User":
                if not self.exclusions.is_principal_excluded(
                    principal_policy_entry.get("Principal"), "User"
                ):
                    if not self.exclusions.is_policy_excluded(
                        principal_policy_entry.get("PolicyName")
                    ):
                        these_policies_in_use.append(
                            principal_policy_entry.get("PolicyName")
                        )
            if principal_policy_entry.get("Type") == "Group":
                if not self.exclusions.is_principal_excluded(
                    principal_policy_entry.get("Principal"), "User"
                ):
                    if not self.exclusions.is_policy_excluded(
                        principal_policy_entry.get("PolicyName")
                    ):
                        these_policies_in_use.append(
                            principal_policy_entry.get("PolicyName")
                        )
            if principal_policy_entry.get("Type") == "Role":
                if not self.exclusions.is_principal_excluded(
                    principal_policy_entry.get("Principal"), "Role"
                ):
                    if not self.exclusions.is_policy_excluded(
                        principal_policy_entry.get("PolicyName")
                    ):
                        these_policies_in_use.append(
                            principal_policy_entry.get("PolicyName")
                        )

        these_policies_in_use = list(
            dict.fromkeys(these_policies_in_use)
        )  # remove duplicates
        these_policies_in_use.sort()
        logger.debug(f"Policies in use: {these_policies_in_use}")
        return these_policies_in_use

    @property
    def json(self):
        """Return the JSON representation of the findings"""
        these_findings = []
        # Users
        if self.users:
            for finding in self.users:
                these_findings.append(finding.json)
        # Groups
        if self.groups:
            for finding in self.groups:
                these_findings.append(finding.json)
        # Roles
        if self.roles:
            for finding in self.roles:
                these_findings.append(finding.json)
        # Policies
        policies_in_use = self.policies_in_use()
        logger.debug("Policies in use: %s", str(policies_in_use))
        policies_in_use_lowercase = [x.lower() for x in policies_in_use]
        for finding in self.policies:
            if finding.policy_name.lower() in policies_in_use_lowercase:
                these_findings.append(finding.json)
            else:
                print(f"The Policy {finding.policy_name} is not used by any non-excluded principals, "
                      f"so it is being excluded from the scan.")
        # sort it
        these_findings = sorted(these_findings, key=itemgetter("PolicyName"))
        # print(json.dumps(these_findings, indent=4))
        return these_findings

    def __len__(self):
        length = (
            len(self.users) + len(self.groups) + len(self.roles) + len(self.policies)
        )
        return length


# pylint: disable=too-many-instance-attributes
class Finding:
    """Parent class for the various finding types"""

    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        exclusions=DEFAULT_EXCLUSIONS,
        assume_role_policy_document=None,
        attached_managed_policies=None,
        attached_to_principal=None,
    ):
        self.policy_name = policy_name
        self.arn = arn
        # The `scan` command uses this, whereas the `scan-policy-file` one does not.
        if "/" in self.arn:
            self.name = get_resource_string(self.arn).split("/")[1]
        else:
            self.name = policy_name
        self.type = capitalize_first_character(
            get_resource_string(self.arn).split("/")[0]
        )
        self.always_exclude_actions = exclusions.exclude_actions
        self.exclusions = exclusions
        self.actions = self._actions(actions)
        self.policy_document = policy_document
        # Roles only
        self.assume_role_policy_document = assume_role_policy_document
        # # Users only
        # self.group_membership = self._group_membership(group_membership)
        # Principals only (not policies)
        self.attached_managed_policies = self._attached_managed_policies(
            attached_managed_policies
        )
        self.attached_to_principal = attached_to_principal

    def _actions(self, actions):
        """Set the actions"""
        results = []
        if self.always_exclude_actions:
            for action in actions:
                # if is_name_excluded(action.lower(), self.always_exclude_actions):
                # If the action is always excluded, don't add it
                if self.exclusions.is_action_always_excluded(action):
                    pass  # pragma: no cover
                elif self.exclusions.is_action_always_included(action):
                    results.append(action)
                else:
                    results.append(action)
            return results
        else:
            return actions

    def _attached_managed_policies(self, attached_managed_policies):
        """Set the attached managed policies"""
        if self.type not in ["User", "Group", "Role"]:
            return None
        if isinstance(attached_managed_policies, list):
            return attached_managed_policies
        elif isinstance(attached_managed_policies, str):
            return [attached_managed_policies]
        elif attached_managed_policies is None:
            return None
        else:
            raise Exception("Please supply the attached policies as a list or string")

    @property
    def managed_by(self):
        """Determine whether the policy is AWS-Managed or Customer-managed based on a Policy ARN pattern."""
        if "arn:aws:iam::aws:" in self.arn:
            return "AWS"  # pragma: no cover
        else:
            return "Customer"

    @property
    def account_id(self):
        """Return the account ID, if applicable."""
        if "arn:aws:iam::aws:" in self.arn:
            return "N/A"  # pragma: no cover
        else:
            try:
                account_id = get_account_from_arn(self.arn)
                return account_id
            except IndexError as i_e:
                logger.debug(i_e)
                return "N/A"

    @property
    def services_affected(self):
        """Return a list of AWS service prefixes affected by the policy in question."""
        services_affected = []
        for action in self.actions:
            service, action_name = action.split(":")  # pylint: disable=unused-variable
            if service not in services_affected:
                services_affected.append(service)
        services_affected.sort()
        return services_affected

    @property
    def assume_role_policy_document_json(self):
        """Return the AssumeRole Policy in JSON"""
        if self.assume_role_policy_document:
            return self.assume_role_policy_document.json
        else:
            return None

    @property
    def role_assumable_by_compute_services(self):
        """Determines whether or not the role is assumed from a compute service, and if so which ones."""
        if self.assume_role_policy_document:
            compute_services = (
                self.assume_role_policy_document.role_assumable_by_compute_services
            )
            return compute_services
        else:
            return []

    @property
    def permissions_management_actions_without_constraints(self):
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
        """Return a list of actions that could cause Privilege Escalation, if applicable."""
        return self.policy_document.allows_privilege_escalation

    @property
    def data_leak_actions(self):
        """Return a list of actions that could cause data exfiltration, if applicable."""
        return self.policy_document.allows_specific_actions_without_constraints(
            READ_ONLY_DATA_LEAK_ACTIONS
        )

    @property
    def json(self):
        """Return the JSON representation of the Finding.
        This is used in the report output and the results data file."""
        result = {
            "AccountID": self.account_id,
            "ManagedBy": self.managed_by,
            "Name": self.name,
            "PolicyName": self.policy_name,
            "Type": self.type,
            "Arn": self.arn,
            "AttachedToPrincipal": self.attached_to_principal,
            # "ActionsCount": self.actions_count,
            # "ServicesCount": self.services_count,
            "ActionsCount": len(self.actions),
            "ServicesCount": len(self.services_affected),
            "Services": self.services_affected,
            "Actions": self.actions,
            "PolicyDocument": self.policy_document.json,
            "AssumeRolePolicyDocument": self.assume_role_policy_document_json,
            # These items help with prioritizing triage and remediation.
            "AssumableByComputeService": self.role_assumable_by_compute_services,
            "PrivilegeEscalation": self.privilege_escalation,
            "DataExfiltrationActions": self.data_leak_actions,
            "PermissionsManagementActions": self.permissions_management_actions_without_constraints,
            # Separate the "Write" and "Tagging" actions in the machine-readable output only
            # "WriteActions": self.policy_document.write_actions_without_constraints,
            # "TaggingActions": self.policy_document.tagging_actions_without_constraints,
        }
        return result


class UserFinding(Finding):
    """Findings for users"""

    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        group_membership,
        exclusions=DEFAULT_EXCLUSIONS,
        attached_managed_policies=None,
    ):
        if attached_managed_policies is None:
            attached_managed_policies = []
        super().__init__(
            policy_name,
            arn,
            actions,
            policy_document,
            exclusions=exclusions,
            attached_managed_policies=attached_managed_policies,
            attached_to_principal=get_resource_path_from_arn(arn)
        )
        self.group_membership = self._group_membership(group_membership)
        self.attached_to_principal = get_resource_path_from_arn(self.arn)

    # pylint: disable=no-self-use
    def _group_membership(self, group_membership):
        if isinstance(group_membership, list):
            return group_membership
        elif isinstance(group_membership, str):
            return [group_membership]
        elif group_membership is None:
            return None
        else:
            raise Exception("Please supply the group membership as a list or string")

    def is_excluded(self, exclusions):
        """Determine whether or not the User in question is excluded"""
        if not isinstance(exclusions, Exclusions):
            raise Exception("Please supply a Exclusions object")
        # (1) If the user is a member of an excluded group, return True
        excluded_groups = []
        if self.group_membership:
            for group in self.group_membership:
                if exclusions.is_principal_excluded(group, "Group"):
                    excluded_groups.append(group)
        if excluded_groups:
            # return True
            return excluded_groups

        # (2) If the user is explicitly excluded, return True
        if exclusions.is_principal_excluded(self.name, "User"):
            logger.debug(f"Excluded: the {self.name} user is explicitly excluded.")
            return [self.name]

        # Each finding will be limited to one policy - so if this user has multiple risky policies,
        # then there will be multiple findings per group
        # So, for this finding, we will check if the single PolicyName/path assigned to this group is excluded.
        # (3) If the policy attached is excluded
        # Policy Name
        if exclusions.is_policy_excluded(self.policy_name.lower()):
            return [self.policy_name]
        # Policy Path
        elif exclusions.is_policy_excluded(get_full_policy_path(self.arn)):
            return [get_full_policy_path(self.arn)]
        # (4) If we made it this far, it's not excluded
        else:
            return False


class GroupFinding(Finding):
    """Findings for Groups"""

    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        members,
        exclusions=DEFAULT_EXCLUSIONS,
        attached_managed_policies=None,
    ):
        if attached_managed_policies is None:
            attached_managed_policies = []
        super().__init__(
            policy_name,
            arn,
            actions,
            policy_document,
            exclusions=exclusions,
            attached_managed_policies=attached_managed_policies,
            attached_to_principal=get_resource_path_from_arn(arn)
        )
        # Group members
        self.members = members

    def is_excluded(self, exclusions):
        """Determine whether or not the Group in question is excluded"""
        if not isinstance(exclusions, Exclusions):
            raise Exception("Please supply a Exclusions object")

        # (1) If there are no more users in the group
        members_in_use = []
        if self.members:
            for member in self.members:
                if not exclusions.is_principal_excluded(member, "User"):
                    members_in_use.append(member)
            if len(members_in_use) == 0:
                # decision_count += 1
                logger.debug(
                    f"Excluded: the {self.name} group's members are all excluded."
                )
                return members_in_use

        # (2) If the group itself is excluded.
        if exclusions.is_principal_excluded(self.name, "Group"):
            logger.debug(f"Excluded: the {self.name} group is explicitly excluded.")
            return self.name

        # Each finding will be limited to one policy - so if this group has multiple risky policies,
        # then there will be multiple findings per group
        # So, for this finding, we will check if the single PolicyName/path assigned to this group is excluded.
        # (3) If the policy attached is excluded
        # Policy Name
        if exclusions.is_policy_excluded(self.policy_name.lower()):
            return self.policy_name
        # Policy Path
        elif exclusions.is_policy_excluded(get_full_policy_path(self.arn)):
            return get_full_policy_path(self.arn)
        else:
            # (4) If we made it this far, it's not excluded
            return False


class RoleFinding(Finding):
    """Findings for roles"""

    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        exclusions=DEFAULT_EXCLUSIONS,
        assume_role_policy_document=None,
        attached_managed_policies=None,
    ):
        if attached_managed_policies is None:
            attached_managed_policies = []
        super().__init__(
            policy_name,
            arn,
            actions,
            policy_document,
            exclusions=exclusions,
            assume_role_policy_document=assume_role_policy_document,
            attached_managed_policies=attached_managed_policies,
            attached_to_principal=get_resource_path_from_arn(arn)
        )

    def is_excluded(self, exclusions):
        """Determine whether or not the Role in question is excluded"""
        if not isinstance(exclusions, Exclusions):
            raise Exception("Please supply a Exclusions object")
        # (1) If the role is explicitly excluded
        if exclusions.is_principal_excluded(self.name, "Role"):
            logger.debug(f"Excluded: the {self.name} role is explicitly excluded.")
            return True
        # Each finding will be limited to one policy - so if this user has multiple risky policies,
        # then there will be multiple findings per group
        # So, for this finding, we will check if the single PolicyName/path assigned to this group is excluded.
        # (2) If the policy attached is excluded
        # Policy Name
        if exclusions.is_policy_excluded(self.policy_name.lower()):
            return self.policy_name
        # Policy Path
        elif exclusions.is_policy_excluded(get_full_policy_path(self.arn)):
            return get_full_policy_path(self.arn)
        # (4) If we made it this far, it's not excluded
        else:
            return False


class PolicyFinding(Finding):
    """Findings for Policies"""

    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        exclusions=DEFAULT_EXCLUSIONS,
        assume_role_policy=None,
        attached_managed_policies=None,
    ):
        super().__init__(
            policy_name,
            arn,
            actions,
            policy_document,
            exclusions=exclusions,
            assume_role_policy_document=assume_role_policy,
            attached_managed_policies=attached_managed_policies,
        )

    def is_excluded(self, exclusions):
        """Determine whether or not the Policy in question is excluded"""
        if not isinstance(exclusions, Exclusions):
            raise Exception("Please supply a Exclusions object")

        # (1) If the policy attached is excluded
        # Policy Name
        if exclusions.is_policy_excluded(self.policy_name.lower()):
            return [self.policy_name]
        # Policy Path
        elif exclusions.is_policy_excluded(get_full_policy_path(self.arn)):
            return [get_full_policy_path(self.arn)]
        # (2) If we made it this far, it's not excluded
        else:
            return False
