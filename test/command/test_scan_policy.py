import unittest
import os
import json
from cloudsplaining.command.scan_policy_file import scan_policy
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions


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
        expected_results = {
            "AccountID": "N/A",
            "ManagedBy": "Customer",
            "PolicyName": "test",
            "Name": "test",
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
            "PermissionsManagementActions": []
        }
        results = scan_policy(example_policy, "test", DEFAULT_EXCLUSIONS)
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results)

    def test_excluded_actions_scan_policy_file(self):
        """Test the scan_policy command when we have excluded actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "iam:CreateAccessKey"
                    ],
                    "Resource": "*"
                },
            ]
        }
        results = scan_policy(test_policy, "test", DEFAULT_EXCLUSIONS)
        expected_results_before_exclusion = {
            "AccountID": "N/A",
            "ManagedBy": "Customer",
            "PolicyName": "test",
            "Name": "test",
            "Type": "",
            "Arn": "test",
            "ActionsCount": 2,
            "ServicesCount": 2,
            "Services": [
                "iam",
                "s3"
            ],
            "Actions": [
                "iam:CreateAccessKey",
                "s3:GetObject"
            ],
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "iam:CreateAccessKey"
                        ],
                        "Resource": "*"
                    }
                ]
            },
            "AssumeRolePolicyDocument": None,
            "AssumableByComputeService": [],
            "PrivilegeEscalation": [
                {
                    "type": "CreateAccessKey",
                    "actions": [
                        "iam:createaccesskey"
                    ]
                }
            ],
            "DataExfiltrationActions": [
                "s3:GetObject"
            ],
            "PermissionsManagementActions": [
                "iam:CreateAccessKey"
            ]
        }
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results_before_exclusion)

    def test_excluded_actions_scan_policy_file_v2(self):
        """test_excluded_actions_scan_policy_file_v2: Test the scan_policy command when we have excluded actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "iam:CreateAccessKey"
                    ],
                    "Resource": "*"
                },
            ]
        }
        expected_results_after_exclusion = []
        exclusions_cfg_custom = {
            "users": ["MyRole"],
            "groups": ["obama"],
            "roles": ["admin"],
            "exclude-actions": [
                "s3:GetObject",
                "iam:CreateAccessKey"
            ]
        }
        exclusions = Exclusions(exclusions_cfg_custom)
        results = scan_policy(test_policy, "test", exclusions)
        print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertListEqual(results, expected_results_after_exclusion)
