"""Classes that hold the results from scanning the authorization file."""
from policy_sentry.util.arns import get_account_from_arn
from cloudsplaining.shared.constants import READ_ONLY_DATA_LEAK_ACTIONS


class Findings:
    """
    Holds all the findings.
    """

    def __init__(self):
        self.findings = []

    def add(self, finding):
        if isinstance(finding, list):
            self.findings.extend(finding)
        elif isinstance(finding, Finding):
            self.findings.append(finding)

    @property
    def is_empty(self):
        if self.findings:
            return False
        else:
            return True

    @property
    def json(self):
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
    def actions_count(self):
        return len(self.actions)

    @property
    def managed_by(self):
        if "arn:aws:iam::aws:" in self.arn:
            return "AWS"
        else:
            return "Customer"

    @property
    def account_id(self):
        if "arn:aws:iam::aws:" in self.arn:
            return "N/A"
        else:
            account_id = get_account_from_arn(self.arn)
            return account_id

    @property
    def services_affected(self):
        services_affected = []
        for action in self.actions:
            service, action_name = action.split(":")
            if service not in services_affected:
                services_affected.append(service)
        services_affected.sort()
        return services_affected

    @property
    def services_count(self):
        return len(self.services_affected)

    @property
    def permissions_management_actions_without_constraints(self):
        return self.policy_document.permissions_management_without_constraints

    @property
    def privilege_escalation(self):
        return self.policy_document.allows_privilege_escalation

    @property
    def data_leak_actions(self):
        return self.policy_document.allows_specific_actions_without_constraints(READ_ONLY_DATA_LEAK_ACTIONS)

    @property
    def json(self):
        result = {
            "AccountID": self.account_id,
            "ManagedBy": self.managed_by,
            "PolicyName": self.policy_name,
            "Arn": self.arn,
            "ActionsCount": self.actions_count,
            "ServicesCount": self.services_count,
            "Services": self.services_affected,
            "Actions": self.actions,
            "PolicyDocument": self.policy_document.json,
            # These items help with prioritizing triage and remediation.
            "PrivilegeEscalation": self.privilege_escalation,
            "AllowsDataLeakActions": self.data_leak_actions,
            "PermissionsManagementActions": self.permissions_management_actions_without_constraints,
            "WriteActions": self.policy_document.write_actions_without_constraints,
            "TaggingActions": self.policy_document.tagging_actions_without_constraints,
        }
        return result
