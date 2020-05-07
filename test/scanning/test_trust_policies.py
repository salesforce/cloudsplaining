from cloudsplaining.scan.assume_role_policy_document import AssumeRoleStatement, AssumeRolePolicyDocument
import os
import unittest
import json


class TestAssumeRole(unittest.TestCase):
    """
    "Principal": "value"
    "Principal": ["value"]
    "Principal": { "AWS": "value" }
    "Principal": { "AWS": ["value", "value"] }
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

        # "Principal": { "Service": "value", "AWS": "value" }
        statement05 = dict(
            Effect="Allow",
            Principal={
                "Service": "lambda.amazonaws.com",
                "AWS": "arn:aws:iam::012345678910:root",
            },
            Action=["rds:*"],
            Resource="*",
        )

        # "Principal": { "Service": ["value", "value"] }
        statement06 = dict(
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

        self.assertListEqual(assume_role_statement_02.principals, ['arn:aws:iam::012345678910:root'])
        self.assertListEqual(assume_role_statement_03.principals, ['arn:aws:iam::012345678910:root'])
        self.assertListEqual(assume_role_statement_04.principals, ['arn:aws:iam::012345678910:root'])
        self.assertListEqual(assume_role_statement_05.principals, ['arn:aws:iam::012345678910:root', 'lambda.amazonaws.com'])
        self.assertListEqual(assume_role_statement_06.principals, ['lambda.amazonaws.com'])

        self.assertListEqual(assume_role_statement_02.role_assumable_by_compute_services, [])
        self.assertListEqual(assume_role_statement_03.role_assumable_by_compute_services, [])
        self.assertListEqual(assume_role_statement_04.role_assumable_by_compute_services, [])
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
