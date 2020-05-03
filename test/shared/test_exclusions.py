import unittest
import os
import json
from cloudsplaining.shared.exclusions import is_name_excluded
from cloudsplaining.scan.authorization_details import AuthorizationDetails
from cloudsplaining.scan.principal_detail import PrincipalDetail


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

    def test_is_principal_excluded(self):
        """scan.principals.Principal.is_principal_excluded"""
        example_authz_details_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "example-authz-details.json",
            )
        )
        with open(example_authz_details_file) as f:
            contents = f.read()
            auth_details_json = json.loads(contents)
        user_principal_detail = PrincipalDetail(auth_details_json["UserDetailList"][0])
        group_principal_detail = PrincipalDetail(auth_details_json["GroupDetailList"][0])
        role_principal_detail = PrincipalDetail(auth_details_json["RoleDetailList"][0])
        exclusions_cfg = {
            "users": [
                "obama"
            ],
            "groups": [
                "admin"
            ],
            "roles": [
                "MyRole",
            ],
        }
        self.assertTrue(user_principal_detail.is_principal_excluded(exclusions_cfg))
        self.assertTrue(group_principal_detail.is_principal_excluded(exclusions_cfg))
        self.assertTrue(role_principal_detail.is_principal_excluded(exclusions_cfg))

        # Testing these with mismatched categories
        exclusions_cfg = {
            "users": [
                "MyRole"
            ],
            "groups": [
                "obama"
            ],
            "roles": [
                "admin",
            ],
        }
        self.assertFalse(user_principal_detail.is_principal_excluded(exclusions_cfg))
        self.assertFalse(group_principal_detail.is_principal_excluded(exclusions_cfg))
        self.assertFalse(role_principal_detail.is_principal_excluded(exclusions_cfg))

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
        authorization_details = AuthorizationDetails(authz_file)
        results = authorization_details.missing_resource_constraints(exclusions_cfg)
        expected_results = []
        # print(json.dumps(results, indent=4))
        self.assertListEqual(results, expected_results)
