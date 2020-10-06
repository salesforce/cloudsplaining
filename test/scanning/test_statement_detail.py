import unittest
from cloudsplaining.scan.statement_detail import StatementDetail
from cloudsplaining.shared.exclusions import is_name_excluded, Exclusions, DEFAULT_EXCLUSIONS


class TestStatementDetail(unittest.TestCase):
    def test_statement(self):
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
              "iam:CreateInstanceProfile",
              "iam:ListInstanceProfilesForRole",
              "iam:PassRole",
              "ec2:DescribeIamInstanceProfileAssociations",
              "iam:GetInstanceProfile",
              "ec2:DisassociateIamInstanceProfile",
              "ec2:AssociateIamInstanceProfile",
              "iam:AddRoleToInstanceProfile"
            ],
            "Resource": "*"
        }
        statement = StatementDetail(this_statement)
        # print(statement.actions)
        # print(json.dumps(statement.actions, indent=4))
        expected_result = [
            "iam:CreateInstanceProfile",
            "iam:ListInstanceProfilesForRole",
            "iam:PassRole",
            "ec2:DescribeIamInstanceProfileAssociations",
            "iam:GetInstanceProfile",
            "ec2:DisassociateIamInstanceProfile",
            "ec2:AssociateIamInstanceProfile",
            "iam:AddRoleToInstanceProfile"
        ]
        self.assertListEqual(statement.actions, expected_result)
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
              "ecr:*"
            ],
            "Resource": "*"
        }
        statement = StatementDetail(this_statement)
        # print(statement.expanded_actions)

    def test_services_in_use(self):
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:CreateInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "ec2:DescribeIamInstanceProfileAssociations",
            ],
            "Resource": "*"
        }
        statement = StatementDetail(this_statement)
        result = statement.services_in_use
        expected_result = ['ec2', 'iam']
        # print(result)
        self.assertListEqual(result, expected_result)

    def test_missing_resource_constraints(self):
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                # 3 wildcard only actions
                "secretsmanager:createsecret",
                "secretsmanager:getrandompassword",
                "secretsmanager:listsecrets",
                # This one is wildcard OR "secret"
                "secretsmanager:putsecretvalue",
            ],
            "Resource": "*"
        }
        statement = StatementDetail(this_statement)
        result = statement.missing_resource_constraints()
        # print(result)
        self.assertListEqual(result, ['secretsmanager:CreateSecret', 'secretsmanager:PutSecretValue'])

    def test_missing_resource_constraints_for_modify_actions(self):
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                # wildcard only actions
                "secretsmanager:getrandompassword",
                "secretsmanager:listsecrets",
                # This one is wildcard OR "secret"
                "secretsmanager:putsecretvalue",
                # This one is wildcard OR object
                "s3:GetObject"
            ],
            "Resource": "*"
        }
        statement = StatementDetail(this_statement)
        result = statement.missing_resource_constraints()

        # print(result)
        self.assertListEqual(result, ['s3:GetObject', 'secretsmanager:PutSecretValue'])
        result = statement.missing_resource_constraints_for_modify_actions()
        print(result)
        self.assertListEqual(result, ['s3:GetObject', 'secretsmanager:PutSecretValue'])

    def test_missing_resource_constraints_for_modify_actions_with_override(self):
        import logging
        import sys
        logger = logging.getLogger(__name__)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                # wildcard only actions
                "secretsmanager:getrandompassword",
                "secretsmanager:listsecrets",
                # This one is wildcard OR "secret"
                "secretsmanager:putsecretvalue",
                # This one is wildcard OR object
                "s3:GetObject"
            ],
            "Resource": "*"
        }

        statement = StatementDetail(this_statement)
        results = statement.missing_resource_constraints_for_modify_actions(DEFAULT_EXCLUSIONS)
        # print(results)
        self.assertListEqual(results, ['s3:GetObject', 'secretsmanager:PutSecretValue'])

    def test_statement_details_for_action_as_string_instead_of_list(self):
        # Case: when the "Action" is a string
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "*"
        }
        # always_look_for_actions = ["s3:GetObject"]
        statement = StatementDetail(this_statement)
        results = statement.missing_resource_constraints_for_modify_actions(DEFAULT_EXCLUSIONS)
        self.assertListEqual(results, ['s3:GetObject'])

    def test_statement_details_for_not_resource(self):
        # Case: when "NotResource" is not included with "Action" as a string
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "NotResource": "*"
        }
        statement = StatementDetail(this_statement)
        results = statement.missing_resource_constraints_for_modify_actions()
        self.assertListEqual(results, [])
        self.assertListEqual(statement.not_resource, ["*"])

    def test_statement_details_for_allow_not_action(self):
        # CASE 1:
        # Effect: Allow && Resource != "*"
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "NotAction": [
                "cloud9:Create*",
                "cloud9:Describe*",
                "cloud9:Delete*",
                "cloud9:Get*",
                "cloud9:List*",
                "cloud9:Update*",
            ],
            "Resource": [
                "arn:aws:cloud9:us-east-1:123456789012:environment:some-resource-id"
            ]
        }
        statement = StatementDetail(this_statement)
        results = statement.not_action_effective_actions
        # We excluded everything else besides TagResource on purpose. Not a typical pattern
        # but easier to maintain with unit tests
        self.assertListEqual(results, ["cloud9:TagResource", "cloud9:UntagResource"])

        # CASE 2:
        # Effect: Allow && Resource == "*"
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "NotAction": [
                "iam:*",
            ],
            "Resource": [
                "*"
            ]
        }
        statement = StatementDetail(this_statement)
        results = statement.not_action_effective_actions
        # there are over 7,000 IAM actions
        self.assertTrue(len(results) > 7000)
        results = statement.write_actions_without_constraints
        # print(len(results))
        # Includes over 3000 write actions
        self.assertTrue(len(results) > 3000)
        results = statement.tagging_actions_without_constraints
        # print(results)
        # print(len(results))
        self.assertTrue(len(results) > 250)

        # CASE 3:
        # Has resource constraints but effect == "Deny"
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Deny",
            "NotAction": [
                "iam:*",
            ],
            "Resource": [
                "arn:aws:cloud9:us-east-1:123456789012:environment:some-resource-id"
            ]
        }
        statement = StatementDetail(this_statement)
        results = statement.not_action_effective_actions
        self.assertIsNone(results)

        # CASE 4:
        # Does not have resource constraints but effect == "Deny"
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Deny",
            "NotAction": [
                "iam:*",
            ],
            "Resource": [
                "*"
            ]
        }
        statement = StatementDetail(this_statement)
        results = statement.not_action_effective_actions
        self.assertIsNone(results)

    def test_statement_details_for_has_not_resource_with_allow(self):
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "*",
            ],
            "NotResource": [
                "arn:aws:s3:::HRBucket"
            ]
        }
        statement = StatementDetail(this_statement)
        results = statement.has_not_resource_with_allow
        self.assertTrue(results)

    def test_statement_with_arn_plus_wildcard(self):
        this_statement = {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "*",
            ],
            "Resource": [
                "arn:aws:s3:::HRBucket",
                "*"
            ]
        }
        statement = StatementDetail(this_statement)
        results = statement.has_resource_constraints
        self.assertFalse(results)
