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

    def test_checkov_gh_990_condition_restricted_action(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "RestrictedWithConditions",
                "Effect": "Allow",
                "Action": "s3:GetObject",
                "Resource": "*",
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": "192.0.2.0/24"
                    },
                    "NotIpAddress": {
                        "aws:SourceIp": "192.0.2.188/32"
                    }
                }
            }]
        }
        exclusions_cfg_custom = {}
        results = scan_policy(test_policy, exclusions_cfg_custom)
        print(json.dumps(results, indent=4))
        self.assertListEqual(results.get("InfrastructureModification"), [])
        self.assertListEqual(results.get("DataExfiltration"), [])
        self.assertListEqual(results.get("ServicesAffected"), [])

        test_policy_without_condition = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "Unrestricted",
                "Effect": "Allow",
                "Action": "s3:GetObject",
                "Resource": "*",
            }]
        }
        results = scan_policy(test_policy_without_condition, exclusions_cfg_custom)
        print(json.dumps(results, indent=4))
        self.assertListEqual(results.get("InfrastructureModification"), [])
        self.assertListEqual(results.get("DataExfiltration"), ["s3:GetObject"])
        self.assertListEqual(results.get("ServicesAffected"), ["s3"])

    def test_gh_254_all_risky_actions_scan_policy(self):
        policy_with_resource_constraints = {
            "Version": "2012-10-17",
            "Statement": [
                # Privilege Escalation
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:UpdateAssumeRolePolicy",
                        "sts:AssumeRole"
                    ],
                    "Resource": "arn:aws:iam::111122223333:role/MyRole"
                },
                # Data Exfiltration
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                    ],
                    "Resource": "arn:aws:s3:::mybucket/*"
                },
                # Resource Expsoure
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutBucketAcl",
                    ],
                    "Resource": "arn:aws:s3:::mybucket"
                },
                # Credentials Exposure
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:UpdateAccessKey",
                    ],
                    "Resource": "arn:aws:iam::111122223333:user/MyUser"
                },
                # Infrastructure Modification
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                    ],
                    "Resource": "arn:aws:ec2:us-east-1:111122223333:security-group/sg-12345678"
                }
            ]
        }
        results = scan_policy(policy_with_resource_constraints, flag_resource_arn_statements=True, flag_conditional_statements=True)
        expected_results = {
            "ServiceWildcard": [],
            "ServicesAffected": [
                "ec2",
                "iam",
                "s3",
                "sts"
            ],
            "PrivilegeEscalation": [
                {
                    "type": "UpdateRolePolicyToAssumeIt",
                    "actions": [
                        "iam:updateassumerolepolicy",
                        "sts:assumerole"
                    ]
                }
            ],
            "ResourceExposure": [
                "iam:UpdateAssumeRolePolicy",
                "s3:PutBucketAcl",
                "iam:UpdateAccessKey"
            ],
            "DataExfiltration": [
                "s3:GetObject"
            ],
            "CredentialsExposure": [
                "iam:UpdateAccessKey",
                "sts:AssumeRole"
            ],
            "InfrastructureModification": [
                "ec2:AuthorizeSecurityGroupIngress",
                "iam:UpdateAccessKey",
                "iam:UpdateAssumeRolePolicy",
                "s3:GetObject",
                "s3:PutBucketAcl",
                "sts:AssumeRole"
            ]
        }

        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)
