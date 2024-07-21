import os
import json
import unittest
from cloudsplaining.scan.authorization_details import AuthorizationDetails
from cloudsplaining.shared.exclusions import Exclusions


def get_authorization_details_with_example_policy(policy_document_dict: dict) -> dict:
    """Returns an Authorization details JSON with an example policy as the single policy"""

    authz_details = {
        "UserDetailList": [
            {
                "Path": "/",
                "UserName": "Captain",
                "UserId": "Captain",
                "Arn": "arn:aws:iam::111122223333:user/Captain",
                "CreateDate": "2019-12-18 19:10:08+00:00",
                "GroupList": [],
                "AttachedManagedPolicies": [
                    {"PolicyName": "SomePolicy", "PolicyArn": "arn:aws:iam::111122223333:policy/SomePolicy"}
                ],
                "Tags": [],
            }
        ],
        "GroupDetailList": [],
        "RoleDetailList": [],
        "Policies": [
            {
                "PolicyName": "SomePolicy",
                "PolicyId": "SomePolicy",
                "Arn": "arn:aws:iam::111122223333:policy/SomePolicy",
                "Path": "/",
                "DefaultVersionId": "v9",
                "AttachmentCount": 1,
                "PermissionsBoundaryUsageCount": 0,
                "IsAttachable": True,
                "CreateDate": "2020-01-29 21:24:20+00:00",
                "UpdateDate": "2020-01-29 23:23:12+00:00",
                "PolicyVersionList": [
                    {
                        "Document": policy_document_dict,
                        "VersionId": "v9",
                        "IsDefaultVersion": True,
                        "CreateDate": "2020-01-29 23:23:12+00:00",
                    }
                ],
            }
        ],
    }
    return authz_details


class TestAuthorizationFileDetails(unittest.TestCase):
    def setUp(self) -> None:
        self.policy_with_resource_constraints = {
            "Version": "2012-10-17",
            "Statement": [
                # Privilege Escalation
                {
                    "Effect": "Allow",
                    "Action": ["iam:UpdateAssumeRolePolicy", "sts:AssumeRole"],
                    "Resource": "arn:aws:iam::111122223333:role/MyRole",
                },
                # Data Exfiltration
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                    ],
                    "Resource": "arn:aws:s3:::mybucket/*",
                },
                # Resource Expsoure
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutBucketAcl",
                    ],
                    "Resource": "arn:aws:s3:::mybucket",
                },
                # Credentials Exposure
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:UpdateAccessKey",
                    ],
                    "Resource": "arn:aws:iam::111122223333:user/MyUser",
                },
                # Infrastructure Modification
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                    ],
                    "Resource": "arn:aws:ec2:us-east-1:111122223333:security-group/sg-12345678",
                },
            ],
        }
        self.authz_json = get_authorization_details_with_example_policy(
            policy_document_dict=self.policy_with_resource_constraints
        )

    def test_authorization_details_with_resource_constraints(self):
        """Case: Authorization details with resource constraints, WITHOUT --flag-all-risky-actions"""
        authz_details = AuthorizationDetails(auth_json=self.authz_json)
        self.assertListEqual(authz_details.policies.policy_details[0].policy_document.credentials_exposure, [])
        self.assertListEqual(authz_details.policies.policy_details[0].policy_document.allows_privilege_escalation, [])
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.allows_data_exfiltration_actions, []
        )
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.permissions_management_without_constraints, []
        )
        self.assertListEqual(authz_details.policies.policy_details[0].policy_document.infrastructure_modification, [])

    def test_authorization_details_flag_all_risky_actions(self):
        """Case: Authorization details with resource constraints, WITH --flag-all-risky-actions"""
        authz_details = AuthorizationDetails(
            auth_json=self.authz_json, flag_resource_arn_statements=True, flag_conditional_statements=True
        )
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.credentials_exposure,
            ["iam:UpdateAccessKey", "sts:AssumeRole"],
        )
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.allows_privilege_escalation,
            [{"type": "UpdateRolePolicyToAssumeIt", "actions": ["iam:updateassumerolepolicy", "sts:assumerole"]}],
        )
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.allows_data_exfiltration_actions, ["s3:GetObject"]
        )
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.permissions_management_without_constraints,
            ["iam:UpdateAssumeRolePolicy", "s3:PutBucketAcl", "iam:UpdateAccessKey"],
        )
        self.assertListEqual(
            authz_details.policies.policy_details[0].policy_document.infrastructure_modification,
            [
                "ec2:AuthorizeSecurityGroupIngress",
                "iam:UpdateAccessKey",
                "iam:UpdateAssumeRolePolicy",
                "s3:GetObject",
                "s3:PutBucketAcl",
                "sts:AssumeRole",
            ],
        )
