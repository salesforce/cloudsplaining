# cloudsplaining/shared/aws_principal.py
"""
AWS Principal Data Model
Holds IAM principal information (User, Role, Group) and privilege escalation findings.
"""

from typing import List


class AWSPrincipal:
    """Base class representing a generic AWS IAM Principal."""

    def __init__(self, name: str, arn: str, policies: list):
        self.name = name
        self.arn = arn
        self.policies = policies

        # Existing per-policy privilege escalation findings
        self.privilege_escalation: List[str] = []

        # New composite findings discovered from merged policies
        self.composite_privilege_escalation_paths: List[str] = []

    def add_composite_escalations(self, escalation_paths: list[str]):
        """Add findings from merged policy analysis."""
        if escalation_paths:
            self.composite_privilege_escalation_paths.extend(escalation_paths)


class AWSUser(AWSPrincipal):
    """IAM User Principal"""
    pass


class AWSRole(AWSPrincipal):
    """IAM Role Principal"""
    pass


class AWSGroup(AWSPrincipal):
    """IAM Group Principal"""
    pass
