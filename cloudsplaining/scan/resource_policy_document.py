"""Represents the Resource-based policy"""

from __future__ import annotations

import logging
import re
from typing import Any

from policy_sentry.util.arns import ARN

CONDITION_KEY_CATEGORIES = {
    "aws:sourcearn": "arn",
    "aws:principalarn": "arn",
    "aws:sourceowner": "account",
    "aws:sourceaccount": "account",
    "aws:principalaccount": "account",
    "aws:principalorgid": "organization",
    "aws:principalorgpaths": "organization",
    "kms:calleraccount": "account",
    "aws:userid": "userid",
    "aws:sourceip": "cidr",
    "aws:sourcevpc": "vpc",
    "aws:sourcevpce": "vpce",
    # a key for SAML Federation trust policy.
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_saml.html
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_saml_assertions.html
    "saml:aud": "saml-endpoint",
}
RELEVANT_CONDITION_OPERATORS_PATTERN = re.compile(
    "((ForAllValues|ForAnyValue):)?(ARN(Equals|Like)|String(Equals|Like)(IgnoreCase)?|IpAddress)(IfExists)?",
    re.IGNORECASE,
)

logger = logging.getLogger(__name__)


class ResourcePolicyDocument:
    """Holds the Resource Policy document"""

    def __init__(self, policy: dict[str, Any]) -> None:
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        self.statements = []
        # leaving here but excluding from tests because IAM Policy grammar dictates that it must be a list
        if not isinstance(statement_structure, list):  # pragma: no cover
            statement_structure = [statement_structure]

        for statement in statement_structure:
            self.statements.append(ResourceStatement(statement))

    @property
    def json(self) -> dict[str, Any]:
        """Return the Resource Policy in JSON"""
        return self.policy

    @property
    def internet_accessible_actions(self) -> list[str]:
        result = []
        for statement in self.statements:
            actions = statement.internet_accessible_actions
            if actions:
                result.extend(actions)

        return result


class ResourceStatement:
    """Statements in a Resource Policy document"""

    def __init__(self, statement: dict[str, Any]) -> None:
        self.json = statement
        self.statement = statement
        self.effect = statement["Effect"]
        self.actions = self._actions()
        self.principals = self._principals()
        self.conditions = self._conditions()

    def _actions(self) -> list[str]:
        """Extracts all actions"""
        actions = self.statement.get("Action", [])
        if not actions:
            return []

        if isinstance(actions, list):
            return actions

        return [actions]

    def _principals(self) -> list[str]:
        """Extracts all principals from IAM statement.
        Should handle these cases:
        "Principal": "value"
        "Principal": ["value"]
        "Principal": { "AWS": "value" }
        "Principal": { "AWS": ["value", "value"] }
        "Principal": { "Federated": "value" }
        "Principal": { "Federated": ["value", "value"] }
        "Principal": { "Service": "value" }
        "Principal": { "Service": ["value", "value"] }
        Return: Set of principals
        """
        principals: list[str] = []
        principal = self.statement.get("Principal", None)
        if not principal:
            # It is possible not to define a principal, AWS ignores these statements.
            return principals  # pragma: no cover

        if isinstance(principal, dict):
            if "AWS" in principal:
                if isinstance(principal["AWS"], list):
                    principals.extend(principal["AWS"])
                else:
                    principals.append(principal["AWS"])

            if "Federated" in principal:
                if isinstance(principal["Federated"], list):
                    principals.extend(principal["Federated"])
                else:
                    principals.append(principal["Federated"])

            if "Service" in principal:
                if isinstance(principal["Service"], list):
                    principals.extend(principal["Service"])
                else:
                    principals.append(principal["Service"])
        else:
            principals.append(principal)

        return principals

    # Adapted version of policyuniverse's _condition_entries, here:
    # https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/statement.py#L146
    def _conditions(self) -> list[tuple[str, Any]]:
        """Extracts any ARNs, Account Numbers, UserIDs, Usernames, CIDRs, VPCs, and VPC Endpoints from a condition block.

        Ignores any negated condition operators like StringNotLike.
        Ignores weak condition keys like referer, date, etc.

        Reason: A condition is meant to limit the principal in a statement.  Often, resource policies use a wildcard principal
        and rely exclusively on the Condition block to limit access.

        We would want to alert if the Condition had no limitations (like a non-existent Condition block), or very weak
        limitations.  Any negation would be weak, and largely equivelant to having no condition block whatsoever.

        The alerting code that relies on this data must ensure the condition has at least one of the following:
        - A limiting ARN
        - Account Identifier
        - AWS Organization Principal Org ID
        - User ID
        - Source IP / CIDR
        - VPC
        - VPC Endpoint

        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html
        """

        conditions: list[tuple[str, Any]] = []
        condition = self.statement.get("Condition")
        if not condition:
            return conditions

        for condition_operator, condition_context in condition.items():
            if RELEVANT_CONDITION_OPERATORS_PATTERN.match(condition_operator):
                for key, value in condition_context.items():
                    key_lower = key.lower()
                    if key_lower in CONDITION_KEY_CATEGORIES:
                        if isinstance(value, list):
                            conditions.extend((CONDITION_KEY_CATEGORIES[key_lower], v) for v in value)
                        else:
                            conditions.append((CONDITION_KEY_CATEGORIES[key_lower], value))

        return conditions

    @property
    def internet_accessible_actions(self) -> list[str]:
        """Determines whether the actions can be used by everyone"""

        # compared to policyuniverse's implementation,
        # there is no need to check for the existence of 'NotPrincipal',
        # because it is not support with self.effect == "Allow"
        if self.effect == "Deny":
            return []

        for entry in self.conditions:
            if self._is_condition_entry_internet_accessible(entry=entry):
                return self.actions

        if self.conditions:
            # this means we have conditions, but they protect the policy to be accessible by everyone
            return []

        for principal in self.principals:
            if self._arn_internet_accessible(arn=principal):
                return self.actions

        return []

    # Adapted version of policyuniverse's _is_condition_entry_internet_accessible and the called methods, here:
    # https://github.com/Netflix-Skunkworks/policyuniverse/blob/master/policyuniverse/statement.py#L301
    # and onwards
    def _is_condition_entry_internet_accessible(self, entry: tuple[str, Any]) -> bool:
        category, condition_value = entry

        if category == "arn":
            return self._arn_internet_accessible(arn=condition_value)
        elif category == "cidr":
            return self._cidr_internet_accessible(cidr=condition_value)
        elif category == "organization":
            return self._organization_internet_accessible(org=condition_value)
        elif category == "userid":
            return self._userid_internet_accessible(userid=condition_value)

        return "*" in condition_value

    def _arn_internet_accessible(self, arn: str) -> bool:
        if arn == "*":
            return True

        if not arn.startswith("arn:"):
            # probably an account ID or AWS service
            return False

        try:
            parsed_arn = ARN(provided_arn=arn)
        except Exception:
            logger.info(f"ARN {arn} is not parsable")
            return "*" in arn

        if parsed_arn.service_prefix == "s3":
            # S3 ARNs don't have account numbers
            return False

        if not parsed_arn.account and not parsed_arn.service_prefix:
            logger.info(f"ARN {arn} is not valid")
            return True

        return parsed_arn.account == "*"

    def _cidr_internet_accessible(self, cidr: str) -> bool:
        return cidr.endswith("/0")

    def _organization_internet_accessible(self, org: str) -> bool:
        return "o-*" in org

    def _userid_internet_accessible(self, userid: str) -> bool:
        # Trailing wildcards are okay for user IDs:
        # AROAIIIIIIIIIIIIIIIII:*
        # note: this will also return False for a zero-length userid
        return userid.find("*") != len(userid) - 1
