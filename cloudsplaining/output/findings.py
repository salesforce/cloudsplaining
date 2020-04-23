"""Classes that hold the results from scanning the authorization file."""
import logging
from policy_sentry.util.arns import get_account_from_arn
from cloudsplaining.shared.constants import READ_ONLY_DATA_LEAK_ACTIONS
logger = logging.getLogger(__name__)


class Findings:
    """
    Holds all the findings.
    """

    def __init__(self):
        self.findings = []

    def add(self, finding):
        """Add a finding to the list."""
        if isinstance(finding, list):
            self.findings.extend(finding)
        elif isinstance(finding, Finding):
            self.findings.append(finding)

    @property
    def json(self):
        """Return the JSON representation of the findings"""
        these_findings = []
        for finding in self.findings:
            these_findings.append(finding.json)
        return these_findings

    def __len__(self):
        return len(self.findings)


class Finding:
    """Holds details on individual findings, including the original Policy Document in question."""
    def __init__(self, policy_name, arn, actions, policy_document):
        self.policy_name = policy_name
        self.arn = arn
        self.actions = actions
        self.policy_document = policy_document

    @property
    def managed_by(self):
        """Determine whether the policy is AWS-Managed or Customer-managed based on a Policy ARN pattern."""
        if "arn:aws:iam::aws:" in self.arn:
            return "AWS"
        else:
            return "Customer"

    @property
    def account_id(self):
        """Return the account ID, if applicable."""
        if "arn:aws:iam::aws:" in self.arn:
            return "N/A"
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
    def permissions_management_actions_without_constraints(self):
        """Return a list of actions that could cause resource exposure via actions at the 'Permissions management' access level, if applicable."""
        return self.policy_document.permissions_management_without_constraints

    @property
    def privilege_escalation(self):
        """Return a list of actions that could cause Privilege Escalation, if applicable."""
        return self.policy_document.allows_privilege_escalation

    @property
    def data_leak_actions(self):
        """Return a list of actions that could cause data exfiltration, if applicable."""
        return self.policy_document.allows_specific_actions_without_constraints(READ_ONLY_DATA_LEAK_ACTIONS)

    @property
    def json(self):
        """Return the JSON representation of the Finding. This is used in the report output and the results data file."""
        result = {
            "AccountID": self.account_id,
            "ManagedBy": self.managed_by,
            "PolicyName": self.policy_name,
            "Arn": self.arn,
            # "ActionsCount": self.actions_count,
            # "ServicesCount": self.services_count,
            "ActionsCount": len(self.actions),
            "ServicesCount": len(self.services_affected),
            "Services": self.services_affected,
            "Actions": self.actions,
            "PolicyDocument": self.policy_document.json,
            # These items help with prioritizing triage and remediation.
            "PrivilegeEscalation": self.privilege_escalation,
            "DataExfiltrationActions": self.data_leak_actions,
            "PermissionsManagementActions": self.permissions_management_actions_without_constraints,
            "WriteActions": self.policy_document.write_actions_without_constraints,
            "TaggingActions": self.policy_document.tagging_actions_without_constraints,
        }
        return result
