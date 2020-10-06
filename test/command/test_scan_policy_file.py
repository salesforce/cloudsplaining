import unittest
import os
import json
from cloudsplaining.command.scan_policy_file import scan_policy
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions


class PolicyFileTestCase(unittest.TestCase):
    def test_policy_file(self):
        example_policy = {
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
        }
        expected_results = {
            "ServicesAffected": [
                "ecr"
            ],
            "PrivilegeEscalation": [],
            "ResourceExposure": [],
            "DataExfiltration": [],
            "ServiceWildcard": [],
            "CredentialsExposure": [
                "ecr:GetAuthorizationToken"
            ],
            "InfrastructureModification": [
                "ecr:CompleteLayerUpload",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage",
                "ecr:UploadLayerPart"
            ]
        }
        results = scan_policy(example_policy)
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
        results = scan_policy(test_policy)
        expected_results = {
            "ServicesAffected": [
                "iam",
                "s3"
            ],
            "PrivilegeEscalation": [
                {
                    "type": "CreateAccessKey",
                    "actions": [
                        "iam:createaccesskey"
                    ]
                }
            ],
            "ResourceExposure": [
                "iam:CreateAccessKey"
            ],
            "DataExfiltration": [
                "s3:GetObject"
            ],
            "ServiceWildcard": [],
            "CredentialsExposure": [
                "iam:CreateAccessKey"
            ],
            "InfrastructureModification": [
                "iam:CreateAccessKey",
                "s3:GetObject"
            ]
        }
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results)

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
        expected_results = {
            "ServiceWildcard": [],
            "ServicesAffected": [
                "iam",
                "s3"
            ],
            "PrivilegeEscalation": [
                {
                    "type": "CreateAccessKey",
                    "actions": [
                        "iam:createaccesskey"
                    ]
                }
            ],
            "ResourceExposure": [
                "iam:CreateAccessKey"
            ],
            "DataExfiltration": [
                "s3:GetObject"
            ],
            "CredentialsExposure": [
                "iam:CreateAccessKey"
            ],
            "InfrastructureModification": [
                "iam:CreateAccessKey"
            ]
        }
        exclusions_cfg_custom = {}
        results = scan_policy(test_policy, exclusions_cfg_custom)
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results)

    def test_gh_109_full_access_policy(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                },
            ]
        }
        exclusions_cfg_custom = {}
        results = scan_policy(test_policy, exclusions_cfg_custom)
        self.assertTrue(len(results.get("ServiceWildcard")) > 150)
        self.assertTrue(len(results.get("ServicesAffected")) > 150)

        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["*"],
                    "Resource": ["*"]
                },
            ]
        }
        results = scan_policy(test_policy, exclusions_cfg_custom)
        # print(json.dumps(results, indent=4))
        self.assertTrue(len(results.get("ServiceWildcard")) > 150)
        self.assertTrue(len(results.get("ServicesAffected")) > 150)

