import logging
from operator import itemgetter
from policy_sentry.util.arns import get_resource_string, get_account_from_arn
from cloudsplaining.shared.exclusions import is_name_excluded, Exclusions, DEFAULT_EXCLUSIONS
from cloudsplaining.shared.constants import READ_ONLY_DATA_LEAK_ACTIONS
from cloudsplaining.shared.utils import capitalize_first_character, get_full_policy_path

logger = logging.getLogger(__name__)


class NewFindings:
    """Holds all the findings"""

    def __init__(self, exclusions=DEFAULT_EXCLUSIONS):
        self.users = []
        self.roles = []
        self.groups = []
        self.policies = []
        self.exclusions = exclusions

    def add_user_finding(self, user_finding):
        if not isinstance(user_finding, UserFinding):
            raise Exception("Please supply a UserFinding object")
        if not user_finding.is_excluded(self.exclusions):
            self.users.append(user_finding)

    def add_group_finding(self, group_finding):
        if not isinstance(group_finding, GroupFinding):
            raise Exception("Please supply a GroupFinding object")
        if not group_finding.is_excluded(self.exclusions):
            self.groups.append(group_finding)

    def add_role_finding(self, role_finding):
        if not isinstance(role_finding, RoleFinding):
            raise Exception("Please supply a RoleFinding object")
        if not role_finding.is_excluded(self.exclusions):
            self.roles.append(role_finding)

    def add_policy_finding(self, policy_finding):
        if not isinstance(policy_finding, PolicyFinding):
            raise Exception("Please supply a PolicyFinding object")
        if not policy_finding.is_excluded(self.exclusions):
            self.policies.append(policy_finding)

    @property
    def json(self):
        """Return the JSON representation of the findings"""
        these_findings = []
        # Users
        for finding in self.users:
            these_findings.append(finding.json)
        # Groups
        for finding in self.groups:
            these_findings.append(finding.json)
        # Roles
        for finding in self.roles:
            these_findings.append(finding.json)
        # Policies
        for finding in self.policies:
            these_findings.append(finding.json)
        # sort it
        these_findings = sorted(these_findings, key=itemgetter("PolicyName"))
        return these_findings

    def __len__(self):
        length = len(self.users) + len(self.groups) + len(self.roles) + len(self.policies)
        return length


class NewFinding:
    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        exclusions=DEFAULT_EXCLUSIONS,
        assume_role_policy_document=None,
        attached_policies=None
    ):
        self.policy_name = policy_name
        self.arn = arn
        self.name = get_resource_string(self.arn).split("/")[1]
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
        self.attached_policies = self._attached_policies(attached_policies)

    def _actions(self, actions):
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

    def _attached_policies(self, attached_policies):
        if self.type in ["User", "Group", "Role"]:
            return None
        if isinstance(attached_policies, list):
            return attached_policies
        elif isinstance(attached_policies, str):
            return [attached_policies]
        elif attached_policies is None:
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
            "Name": get_resource_string(self.arn).split("/")[1],
            "PolicyName": self.policy_name,
            "Type": self.type,
            "Arn": self.arn,
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


class UserFinding(NewFinding):
    def __init__(self, policy_name, arn, actions, policy_document, group_membership=None, exclusions=DEFAULT_EXCLUSIONS, attached_policies=None):
        super().__init__(policy_name, arn, actions, policy_document, exclusions=exclusions, attached_policies=attached_policies)
        self.group_membership = self._group_membership(group_membership)

    def _group_membership(self, group_membership):
        if isinstance(group_membership, list):
            return group_membership
        elif isinstance(group_membership, str):
            return [group_membership]
        elif group_membership is None:
            return None
        else:
            raise Exception("Please supply the group membership as a list or string")

    def _attached_policies(self, attached_policies):
        if self.type in ["User", "Group", "Role"]:
            return None
        if isinstance(attached_policies, list):
            return attached_policies
        elif isinstance(attached_policies, str):
            return [attached_policies]
        elif attached_policies is None:
            return None
        else:
            raise Exception("Please supply the attached policies as a list or string")

    def is_excluded(self, exclusions):
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


class GroupFinding(NewFinding):
    def __init__(self, policy_name, arn, actions, policy_document, members=None, exclusions=DEFAULT_EXCLUSIONS, attached_policies=None):
        super().__init__(policy_name, arn, actions, policy_document, exclusions=exclusions, attached_policies=attached_policies)
        # Group members
        self.members = members

    def is_excluded(self, exclusions):
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
                logger.debug(f"Excluded: the {self.name} group's members are all excluded.")
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

    def _attached_policies(self, attached_policies):
        if self.type in ["User", "Group", "Role"]:
            return None
        if isinstance(attached_policies, list):
            return attached_policies
        elif isinstance(attached_policies, str):
            return [attached_policies]
        elif attached_policies is None:
            return None
        else:
            raise Exception("Please supply the attached policies as a list or string")


class RoleFinding(NewFinding):
    def __init__(self, policy_name, arn, actions, policy_document, exclusions=DEFAULT_EXCLUSIONS, assume_role_policy_document=None, attached_policies=None):
        super().__init__(policy_name, arn, actions, policy_document, exclusions=exclusions, assume_role_policy_document=assume_role_policy_document, attached_policies=None)

    def is_excluded(self, exclusions):
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

    # TODO: Make an AssumeRolePolicyDocument item here - maybe.

    def _attached_policies(self, attached_policies):
        if self.type in ["User", "Group", "Role"]:
            return None
        if isinstance(attached_policies, list):
            return attached_policies
        elif isinstance(attached_policies, str):
            return [attached_policies]
        elif attached_policies is None:
            return None
        else:
            raise Exception("Please supply the attached policies as a list or string")


class PolicyFinding(NewFinding):
    def __init__(self, policy_name, arn, actions, policy_document, exclusions=DEFAULT_EXCLUSIONS, assume_role_policy=None, attached_policies=None):
        super().__init__(
            policy_name,
            arn,
            actions,
            policy_document,
            exclusions=exclusions,
            assume_role_policy_document=assume_role_policy,
            attached_policies=None
         )

    def is_excluded(self, exclusions):
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
