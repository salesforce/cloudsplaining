import unittest
import os
import json
from cloudsplaining.shared.exclusions import is_name_excluded, Exclusions
from cloudsplaining.scan.authorization_details import AuthorizationDetails


class ExclusionsNewTestCase(unittest.TestCase):
    def test_new_exclusions_approach(self):
        exclusions_cfg = {
            "policies": [
                "aws-service-role*"
            ],
            "roles": ["aws-service-role*"],
            "users": [""],
            "include-actions": ["s3:GetObject"],
            "exclude-actions": ["kms:Decrypt"]
        }
        exclusions = Exclusions(exclusions_cfg)
        test_actions_list = [
            "s3:GetObject",
            "kms:decrypt",
            "ssm:GetParameter",
            "ec2:DescribeInstances"
        ]
        result = exclusions.get_allowed_actions(test_actions_list)
        self.assertListEqual(result, ['s3:GetObject', 'ssm:GetParameter', 'ec2:DescribeInstances'])


class ExclusionsTestCase(unittest.TestCase):
    def test_exclusions_exact_match(self):
        """test_exclusions_exact_match: If there is an exact match in the exclusions list"""
        exclusions_list = [
            "Beyonce"
        ]
        policy_name = "Beyonce"
        result = is_name_excluded(policy_name, exclusions_list)
        self.assertTrue(result)

    def test_exclusions_prefix_match(self):
        """test_exclusions_prefix_match: Test exclusions function with prefix wildcard logic."""
        exclusions_list = [
            "ThePerfectManDoesntExi*"
        ]
        policy_name = "ThePerfectManDoesntExist"
        result = is_name_excluded(policy_name, exclusions_list)
        self.assertTrue(result)

    def test_exclusions_suffix_match(self):
        """test_exclusions_suffix_match: Test exclusions function with suffix wildcard logic."""
        exclusions_list = [
            "*ish"
        ]
        policy_name = "Secure-ish"
        result = is_name_excluded(policy_name, exclusions_list)
        self.assertTrue(result)


class AuthorizationsFileComponentsExclusionsTestCase(unittest.TestCase):

    def test_exclusions_for_service_roles(self):
        """test_exclusions_for_service_roles: Ensuring that exclusions config of service roles are specifically
        skipped, as designed"""
        authz_file = {
            "UserDetailList": [],
            "GroupDetailList": [],
            "RoleDetailList": [
                {
                    "Path": "/aws-service-role/cloudwatch-crossaccount.amazonaws.com/",
                    "RoleName": "AWSServiceRoleForCloudWatchCrossAccount",
                    "RoleId": "LALALALALAALALA",
                    "Arn": "arn:aws:iam::115657980943:role/aws-service-role/cloudwatch-crossaccount.amazonaws.com/AWSServiceRoleForCloudWatchCrossAccount",
                    "CreateDate": "2019-11-07 20:21:23+00:00",
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "cloudwatch-crossaccount.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    },
                    "InstanceProfileList": [],
                    "RolePolicyList": [],
                    "AttachedManagedPolicies": [
                        {
                            "PolicyName": "CloudWatch-CrossAccountAccess",
                            "PolicyArn": "arn:aws:iam::aws:policy/aws-service-role/CloudWatch-CrossAccountAccess"
                        }
                    ]
                },
            ],
            "Policies": [
                {
                    "PolicyName": "CloudWatch-CrossAccountAccess",
                    "PolicyId": "LALALALALAALALA",
                    "Arn": "arn:aws:iam::aws:policy/aws-service-role/CloudWatch-CrossAccountAccess",
                    # "Arn": "arn:aws:iam::aws:policy/Sup",
                    "Path": "/aws-service-role/",
                    "DefaultVersionId": "v1",
                    "AttachmentCount": 1,
                    "PermissionsBoundaryUsageCount": None,
                    "IsAttachable": True,
                    "CreateDate": "2019-07-23 09:59:27+00:00",
                    "UpdateDate": "2019-07-23 09:59:27+00:00",
                    "PolicyVersionList": [
                        {
                            "Document": {
                                "Version": "2012-10-17",
                                # This is fake, I'm just trying to trigger a response
                                "Statement": [
                                    {
                                        "Action": [
                                            "iam:*"
                                        ],
                                        "Resource": [
                                            "*"
                                        ],
                                        "Effect": "Allow"
                                    }
                                ]
                            },
                            "VersionId": "v1",
                            "IsDefaultVersion": True,
                            "CreateDate": "2019-07-23 09:59:27+00:00"
                        }
                    ]
                }
            ]
        }
        exclusions_cfg = {
            "policies": [
                "aws-service-role*"
            ]
        }
        exclusions = Exclusions(exclusions_cfg)
        authorization_details = AuthorizationDetails(authz_file, exclusions)
        results = authorization_details.results

        expected_results = {"groups": {}, "users": {}, "roles": {}, "aws_managed_policies": {}, "customer_managed_policies": {}, "inline_policies": {}, "exclusions": {"policies": ["aws-service-role*"]}}
        self.assertDictEqual(results, expected_results)
