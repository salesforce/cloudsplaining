import unittest
import os
import json
from cloudsplaining.command.scan_policy_file import scan_policy
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG


class PolicyFileTestCase(unittest.TestCase):
    def test_policy_file(self):
        policy_test_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "test_policy_file.json",
            )
        )

        # print(expected_results_file)
        with open(policy_test_file) as json_file:
            example_policy = json.load(json_file)
        expected_results = [
            {
                "AccountID": "N/A",
                "ManagedBy": "Customer",
                "PolicyName": "test",
                "Type": "",
                "Arn": "test",
                "ActionsCount": 4,
                "ServicesCount": 1,
                "Services": [
                    "ecr"
                ],
                "Actions": [
                    "ecr:CompleteLayerUpload",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart"
                ],
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ecr:GetAuthorizationToken",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:GetRepositoryPolicy",
                                "ecr:DescribeRepositories",
                                "ecr:ListImages",
                                "ecr:DescribeImages",
                                "ecr:BatchGetImage",
                                "ecr:InitiateLayerUpload",
                                "ecr:UploadLayerPart",
                                "ecr:CompleteLayerUpload",
                                "ecr:PutImage"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Sid": "AllowManageOwnAccessKeys",
                            "Effect": "Allow",
                            "Action": [
                                "iam:CreateAccessKey",
                                "iam:DeleteAccessKey",
                                "iam:ListAccessKeys",
                                "iam:UpdateAccessKey"
                            ],
                            "Resource": "arn:aws:iam::*:user/${aws:username}"
                        }
                    ]
                },
                "AssumeRolePolicyDocument": None,
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [],
                "PermissionsManagementActions": [],
                "WriteActions": [
                    "ecr:CompleteLayerUpload",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart"
                ],
                "TaggingActions": []
            }
        ]
        results = scan_policy(example_policy, "test", DEFAULT_EXCLUSIONS_CONFIG)
        print(json.dumps(results, indent=4))
        self.assertListEqual(results, expected_results)
