import unittest
from cloudsplaining.scan.statement_detail import StatementDetail


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
        result = statement.missing_resource_constraints
        # print(result)
        self.assertListEqual(result, ['secretsmanager:PutSecretValue'])

    def test_missing_resource_constraints_for_modify_actions(self):
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
                # This one is wildcard OR object
                "s3:GetObject"
            ],
            "Resource": "*"
        }
        statement = StatementDetail(this_statement)
        result = statement.missing_resource_constraints
        # print(result)
        self.assertListEqual(result, ["s3:GetObject", 'secretsmanager:PutSecretValue'])
        result = statement.missing_resource_constraints_for_modify_actions()
        # There is no exclusion here so s3:GetObject will not be included
        self.assertListEqual(result, ['secretsmanager:PutSecretValue'])

    def test_missing_resource_constraints_for_modify_actions_with_override(self):
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
                # This one is wildcard OR object
                "s3:GetObject"
            ],
            "Resource": "*"
        }
        always_look_for_actions = ["s3:GetObject"]
        statement = StatementDetail(this_statement)
        results = statement.missing_resource_constraints_for_modify_actions(always_look_for_actions)
        # print(results)
        self.assertListEqual(results, ['secretsmanager:PutSecretValue', 's3:GetObject'])

