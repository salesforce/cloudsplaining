import unittest

from cloudsplaining.scan.assume_role_policy_document import AssumeRolePolicyDocument, AssumeRoleStatement
from cloudsplaining.shared.exclusions import Exclusions


class TestAssumeRole(unittest.TestCase):
    """
    "Principal": "value"
    "Principal": ["value"]
    "Principal": { "AWS": "value" }
    "Principal": { "AWS": ["value", "value"] }
    "Principal": { "Federated": "value" }
    "Principal": { "Federated": ["value", "value"] }
    "Principal": { "Service": "value" }
    "Principal": { "Service": ["value", "value"] }
    """

    def test_assume_role_statement_principal_formats(self):
        """scan.assume_role_policy_document.AssumeRoleStatement._principal: Format case 1"""
        # "Principal": "value"
        statement02 = dict(
            Effect="Allow",
            Principal="arn:aws:iam::012345678910:root",
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "AWS": "value" }
        statement03 = dict(
            Effect="Allow",
            Principal={"AWS": "arn:aws:iam::012345678910:root"},
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "AWS": ["value", "value"] }
        statement04 = dict(
            Effect="Allow",
            Principal={"AWS": ["arn:aws:iam::012345678910:root"]},
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "Federated": "value" }
        statement05 = dict(
            Effect="Allow",
            Principal={"Federated": "accounts.google.com"},
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "Federated": ["value", "value"] }
        statement06 = dict(
            Effect="Allow",
            Principal={"Federated": ["cognito-identity.amazonaws.com", "www.amazon.com"]},
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "Service": "value", "AWS": "value" }
        statement07 = dict(
            Effect="Allow",
            Principal={
                "Service": "lambda.amazonaws.com",
                "AWS": "arn:aws:iam::012345678910:root",
            },
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "Service": ["value", "value"] }
        statement08 = dict(
            Effect="Allow",
            Principal={"Service": ["lambda.amazonaws.com"]},
            Action=["rds:*"],
            Resource="*",
        )
        assume_role_statement_02 = AssumeRoleStatement(statement02)
        assume_role_statement_03 = AssumeRoleStatement(statement03)
        assume_role_statement_04 = AssumeRoleStatement(statement04)
        assume_role_statement_05 = AssumeRoleStatement(statement05)
        assume_role_statement_06 = AssumeRoleStatement(statement06)
        assume_role_statement_07 = AssumeRoleStatement(statement07)
        assume_role_statement_08 = AssumeRoleStatement(statement08)

        self.assertListEqual(assume_role_statement_02.principals, ["arn:aws:iam::012345678910:root"])
        self.assertListEqual(assume_role_statement_03.principals, ["arn:aws:iam::012345678910:root"])
        self.assertListEqual(assume_role_statement_04.principals, ["arn:aws:iam::012345678910:root"])
        self.assertListEqual(assume_role_statement_05.principals, ["accounts.google.com"])
        self.assertListEqual(assume_role_statement_06.principals, ["cognito-identity.amazonaws.com", "www.amazon.com"])
        self.assertListEqual(
            assume_role_statement_07.principals, ["arn:aws:iam::012345678910:root", "lambda.amazonaws.com"]
        )
        self.assertListEqual(assume_role_statement_08.principals, ["lambda.amazonaws.com"])

        self.assertListEqual(assume_role_statement_02.role_assumable_by_compute_services, [])
        self.assertListEqual(assume_role_statement_03.role_assumable_by_compute_services, [])
        self.assertListEqual(assume_role_statement_04.role_assumable_by_compute_services, [])
        self.assertListEqual(assume_role_statement_05.role_assumable_by_compute_services, [])
        self.assertListEqual(assume_role_statement_06.role_assumable_by_compute_services, [])
        # self.assertListEqual(assume_role_statement_05.role_assumable_by_compute_services, ["lambda"])
        # self.assertListEqual(assume_role_statement_06.role_assumable_by_compute_services, ["lambda"])

    def test_assume_role_assumable_by_compute_services(self):
        """scan.assume_role_policy_document.AssumeRoleStatement.role_assumable_by_compute_services"""
        # Case: From a compute service
        statement07 = dict(
            Effect="Allow",
            Principal={
                "Service": "ecs-tasks.amazonaws.com",
                "AWS": "arn:aws:iam::012345678910:root",
            },
            Action=["sts:AssumeRole"],
        )
        assume_role_statement_07 = AssumeRoleStatement(statement07)
        self.assertListEqual(assume_role_statement_07.role_assumable_by_compute_services, ["ecs-tasks"])

        # Case: Not a compute service, with AssumeRole
        statement08 = dict(
            Effect="Allow",
            Principal={"Service": ["somethingelse.amazonaws.com"]},
            Action=["sts:AssumeRole"],
        )
        assume_role_statement_08 = AssumeRoleStatement(statement08)
        self.assertListEqual(assume_role_statement_08.role_assumable_by_compute_services, [])

        # Case: Not a compute service, with AssumeRole
        empty_actions_statement = dict(
            Effect="Allow",
            Principal={"Service": ["somethingelse.amazonaws.com"]},
            Action=[],
        )
        assume_role_empty_actions_statement = AssumeRoleStatement(empty_actions_statement)
        self.assertListEqual(assume_role_empty_actions_statement.actions, [])

        # Case: Deny statement, for a  compute service
        deny_statement = dict(
            Effect="Deny",
            Principal={"Service": ["lambda.amazonaws.com"]},
            Action=["sts:AssumeRole"],
        )
        assume_role_deny_statement = AssumeRoleStatement(deny_statement)
        self.assertListEqual(assume_role_deny_statement.role_assumable_by_compute_services, [])

    def test_assume_role_assumable_by_cross_account_principals(self):
        """scan.assume_role_policy_document.AssumeRoleStatement.role_assumable_by_cross_account_principals"""

        # Test basic cross-account detection with different principal types
        statement_cross_account = dict(
            Effect="Allow",
            Principal={
                "AWS": [
                    "arn:aws:iam::123456789012:root",
                    "arn:aws:iam::123456789012:user/testuser",
                    "arn:aws:iam::098765432109:role/testrole",
                ]
            },
            Action=["sts:AssumeRole"],
        )
        assume_role_cross_account = AssumeRoleStatement(statement_cross_account)
        expected = [
            "arn:aws:iam::123456789012:root",
            "arn:aws:iam::123456789012:user/testuser",
            "arn:aws:iam::098765432109:role/testrole",
        ]
        self.assertListEqual(assume_role_cross_account.role_assumable_by_cross_account_principals, expected)

        # Test current account filtering
        assume_role_with_filtering = AssumeRoleStatement(statement_cross_account, current_account_id="123456789012")
        self.assertListEqual(
            assume_role_with_filtering.role_assumable_by_cross_account_principals,
            ["arn:aws:iam::098765432109:role/testrole"],
        )

        # Test known accounts exclusions
        exclusions_config = {"known-accounts": ["123456789012", "098765432109"]}
        exclusions = Exclusions(exclusions_config)
        assume_role_with_exclusions = AssumeRoleStatement(statement_cross_account, exclusions=exclusions)
        # All accounts should be excluded since they're in the known-accounts list
        self.assertListEqual(assume_role_with_exclusions.role_assumable_by_cross_account_principals, [])

        # Test partial exclusions - only exclude one account
        partial_exclusions_config = {"known-accounts": ["123456789012"]}
        partial_exclusions = Exclusions(partial_exclusions_config)
        assume_role_partial_exclusions = AssumeRoleStatement(statement_cross_account, exclusions=partial_exclusions)
        # Only the principals from non-excluded accounts should remain
        self.assertListEqual(
            assume_role_partial_exclusions.role_assumable_by_cross_account_principals,
            ["arn:aws:iam::098765432109:role/testrole"],
        )

        # Test exclusions with current account filtering combined
        assume_role_combined_filtering = AssumeRoleStatement(
            statement_cross_account, current_account_id="123456789012", exclusions=partial_exclusions
        )
        # Current account filtering should happen first, then exclusions applied
        # Since 123456789012 is the current account AND in exclusions, 098765432109 should remain
        self.assertListEqual(
            assume_role_combined_filtering.role_assumable_by_cross_account_principals,
            ["arn:aws:iam::098765432109:role/testrole"],
        )

        # Test conditions that should return empty results
        # No sts:AssumeRole action
        statement_no_assume_role = dict(
            Effect="Allow", Principal={"AWS": "arn:aws:iam::123456789012:root"}, Action=["s3:GetObject"]
        )
        self.assertListEqual(
            AssumeRoleStatement(statement_no_assume_role).role_assumable_by_cross_account_principals, []
        )

        # Deny effect
        statement_deny = dict(
            Effect="Deny", Principal={"AWS": "arn:aws:iam::123456789012:root"}, Action=["sts:AssumeRole"]
        )
        self.assertListEqual(AssumeRoleStatement(statement_deny).role_assumable_by_cross_account_principals, [])

        # Service principals only
        statement_service = dict(
            Effect="Allow", Principal={"Service": "lambda.amazonaws.com"}, Action=["sts:AssumeRole"]
        )
        self.assertListEqual(AssumeRoleStatement(statement_service).role_assumable_by_cross_account_principals, [])

        # Test AssumeRolePolicyDocument aggregation
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"AWS": "arn:aws:iam::123456789012:root"}, "Action": "sts:AssumeRole"},
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "arn:aws:iam::098765432109:user/testuser"},
                    "Action": "sts:AssumeRole",
                },
            ],
        }
        policy_doc = AssumeRolePolicyDocument(policy)
        expected_policy = ["arn:aws:iam::123456789012:root", "arn:aws:iam::098765432109:user/testuser"]
        self.assertListEqual(policy_doc.role_assumable_by_cross_account_principals, expected_policy)

        # Test AssumeRolePolicyDocument with exclusions
        partial_exclusions_config_doc = {"known-accounts": ["123456789012"]}
        partial_exclusions_doc = Exclusions(partial_exclusions_config_doc)
        policy_doc_with_exclusions = AssumeRolePolicyDocument(policy, exclusions=partial_exclusions_doc)
        expected_policy_with_exclusions = ["arn:aws:iam::098765432109:user/testuser"]
        self.assertListEqual(
            policy_doc_with_exclusions.role_assumable_by_cross_account_principals, expected_policy_with_exclusions
        )

    def test_assume_role_assumable_by_any_principal(self):
        """scan.assume_role_policy_document.AssumeRoleStatement.role_assumable_by_any_principal"""

        # Test wildcard principal "*"
        statement_wildcard = dict(
            Effect="Allow",
            Principal="*",
            Action=["sts:AssumeRole"],
        )
        assume_role_wildcard = AssumeRoleStatement(statement_wildcard)
        self.assertListEqual(assume_role_wildcard.role_assumable_by_any_principal, ["*"])

        # Test "arn:aws:iam::*:root" principal
        statement_any_root = dict(
            Effect="Allow",
            Principal="arn:aws:iam::*:root",
            Action=["sts:AssumeRole"],
        )
        assume_role_any_root = AssumeRoleStatement(statement_any_root)
        self.assertListEqual(assume_role_any_root.role_assumable_by_any_principal, ["arn:aws:iam::*:root"])

        # Test both wildcard and any root in the same statement
        statement_both = dict(
            Effect="Allow",
            Principal={"AWS": ["*", "arn:aws:iam::*:root"]},
            Action=["sts:AssumeRole"],
        )
        assume_role_both = AssumeRoleStatement(statement_both)
        self.assertListEqual(assume_role_both.role_assumable_by_any_principal, ["*", "arn:aws:iam::*:root"])

        # Test conditions that should return empty results
        # No sts:AssumeRole action
        statement_no_assume_role = dict(Effect="Allow", Principal="*", Action=["s3:GetObject"])
        self.assertListEqual(AssumeRoleStatement(statement_no_assume_role).role_assumable_by_any_principal, [])

        # Deny effect
        statement_deny = dict(Effect="Deny", Principal="*", Action=["sts:AssumeRole"])
        self.assertListEqual(AssumeRoleStatement(statement_deny).role_assumable_by_any_principal, [])

        # Specific principals only (not wildcard)
        statement_specific = dict(
            Effect="Allow", Principal={"AWS": "arn:aws:iam::123456789012:root"}, Action=["sts:AssumeRole"]
        )
        self.assertListEqual(AssumeRoleStatement(statement_specific).role_assumable_by_any_principal, [])

        # Wildcard principal with conditions (should return empty)
        statement_with_conditions = dict(
            Effect="Allow",
            Principal="*",
            Action=["sts:AssumeRole"],
            Condition={"StringEquals": {"aws:sourceip": "203.0.113.0/24"}},
        )
        self.assertListEqual(AssumeRoleStatement(statement_with_conditions).role_assumable_by_any_principal, [])

        # Test AssumeRolePolicyDocument aggregation
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": "*", "Action": "sts:AssumeRole"},
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "arn:aws:iam::*:root"},
                    "Action": "sts:AssumeRole",
                },
            ],
        }
        policy_doc = AssumeRolePolicyDocument(policy)
        expected_policy = ["*", "arn:aws:iam::*:root"]
        self.assertListEqual(policy_doc.role_assumable_by_any_principal, expected_policy)

    def test_assume_role_assumable_by_any_principal_with_conditions(self):
        """scan.assume_role_policy_document.AssumeRoleStatement.role_assumable_by_any_principal_with_conditions"""

        # Test wildcard principal "*" with conditions
        statement_wildcard_with_conditions = dict(
            Effect="Allow",
            Principal="*",
            Action=["sts:AssumeRole"],
            Condition={"StringEquals": {"aws:sourceip": "203.0.113.0/24"}},
        )
        assume_role_wildcard_conditions = AssumeRoleStatement(statement_wildcard_with_conditions)
        self.assertListEqual(assume_role_wildcard_conditions.role_assumable_by_any_principal_with_conditions, ["*"])

        # Test "arn:aws:iam::*:root" principal with conditions
        statement_any_root_with_conditions = dict(
            Effect="Allow",
            Principal="arn:aws:iam::*:root",
            Action=["sts:AssumeRole"],
            Condition={"StringEquals": {"sts:ExternalId": "unique-id"}},
        )
        assume_role_any_root_conditions = AssumeRoleStatement(statement_any_root_with_conditions)
        self.assertListEqual(
            assume_role_any_root_conditions.role_assumable_by_any_principal_with_conditions, ["arn:aws:iam::*:root"]
        )

        # Test both wildcard and any root with conditions
        statement_both_with_conditions = dict(
            Effect="Allow",
            Principal={"AWS": ["*", "arn:aws:iam::*:root"]},
            Action=["sts:AssumeRole"],
            Condition={"StringEquals": {"aws:RequestedRegion": "us-east-1"}},
        )
        assume_role_both_conditions = AssumeRoleStatement(statement_both_with_conditions)
        self.assertListEqual(
            assume_role_both_conditions.role_assumable_by_any_principal_with_conditions, ["*", "arn:aws:iam::*:root"]
        )

        # Test conditions that should return empty results
        # No sts:AssumeRole action
        statement_no_assume_role = dict(
            Effect="Allow",
            Principal="*",
            Action=["s3:GetObject"],
            Condition={"StringEquals": {"aws:sourceip": "203.0.113.0/24"}},
        )
        self.assertListEqual(
            AssumeRoleStatement(statement_no_assume_role).role_assumable_by_any_principal_with_conditions, []
        )

        # Deny effect
        statement_deny = dict(
            Effect="Deny",
            Principal="*",
            Action=["sts:AssumeRole"],
            Condition={"StringEquals": {"aws:sourceip": "203.0.113.0/24"}},
        )
        self.assertListEqual(AssumeRoleStatement(statement_deny).role_assumable_by_any_principal_with_conditions, [])

        # Wildcard principal without conditions (should return empty)
        statement_no_conditions = dict(
            Effect="Allow",
            Principal="*",
            Action=["sts:AssumeRole"],
        )
        self.assertListEqual(
            AssumeRoleStatement(statement_no_conditions).role_assumable_by_any_principal_with_conditions, []
        )

        # Specific principals only (not wildcard) with conditions
        statement_specific_with_conditions = dict(
            Effect="Allow",
            Principal={"AWS": "arn:aws:iam::123456789012:root"},
            Action=["sts:AssumeRole"],
            Condition={"StringEquals": {"aws:sourceip": "203.0.113.0/24"}},
        )
        self.assertListEqual(
            AssumeRoleStatement(statement_specific_with_conditions).role_assumable_by_any_principal_with_conditions, []
        )

        # Test AssumeRolePolicyDocument aggregation
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "sts:AssumeRole",
                    "Condition": {"StringEquals": {"aws:sourceip": "203.0.113.0/24"}},
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "arn:aws:iam::*:root"},
                    "Action": "sts:AssumeRole",
                    "Condition": {"StringEquals": {"sts:ExternalId": "unique-id"}},
                },
            ],
        }
        policy_doc = AssumeRolePolicyDocument(policy)
        expected_policy = ["*", "arn:aws:iam::*:root"]
        self.assertListEqual(policy_doc.role_assumable_by_any_principal_with_conditions, expected_policy)
