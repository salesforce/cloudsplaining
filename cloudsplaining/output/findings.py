"""Classes that hold the results from scanning the authorization file."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
from operator import itemgetter
from policy_sentry.util.arns import get_account_from_arn, get_resource_string
from cloudsplaining.shared.constants import READ_ONLY_DATA_LEAK_ACTIONS
from cloudsplaining.shared.exclusions import is_name_excluded
from cloudsplaining.shared.utils import capitalize_first_character

logger = logging.getLogger(__name__)


class Findings:
    """
    Holds all the findings.
    """

    def __init__(self):
        self.findings = []
        self.exclusions = None

    def add(self, finding):
        """Add a finding to the list."""
        if isinstance(finding, list):
            for a_finding in finding:
                # Only add it if there are any actions after processing exclusions
                if a_finding.actions:
                    self.findings.append(a_finding)
        elif isinstance(finding, Finding):
            if finding.actions:
                self.findings.append(finding)

    @property
    def json(self):
        """Return the JSON representation of the findings"""
        these_findings = []
        for finding in self.findings:
            these_findings.append(finding.json)
        # sort it
        these_findings = sorted(these_findings, key=itemgetter("PolicyName"))
        return these_findings

    def __len__(self):
        return len(self.findings)  # pragma: no cover


class Finding:
    """Holds details on individual findings, including the original Policy Document in question."""

    def __init__(
        self,
        policy_name,
        arn,
        actions,
        policy_document,
        assume_role_policy_document=None,
        always_exclude_actions=None,
    ):
        self.policy_name = policy_name
        self.arn = arn
        self.type = capitalize_first_character(
            get_resource_string(self.arn).split("/")[0]
        )
        self.always_exclude_actions = always_exclude_actions
        self.actions = self._actions(actions)
        self.policy_document = policy_document
        self.assume_role_policy_document = assume_role_policy_document

    def _actions(self, actions):
        results = []
        if self.always_exclude_actions:
            for action in actions:
                if is_name_excluded(action.lower(), self.always_exclude_actions):
                    pass  # pragma: no cover
                else:
                    results.append(action)
            return results
        else:
            return actions

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
