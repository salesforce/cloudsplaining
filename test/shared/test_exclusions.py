import unittest
import os
import json
from cloudsplaining.shared.exclusions import is_name_excluded, Exclusions
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
        exclusions = Exclusions(exclusions_cfg)
        self.assertTrue(user_principal_detail.is_principal_excluded(exclusions))
        self.assertTrue(group_principal_detail.is_principal_excluded(exclusions))
        self.assertTrue(role_principal_detail.is_principal_excluded(exclusions))

        # Testing these with mismatched categories
        exclusions_cfg = dict(
            users=["MyRole"],
            groups=["obama"],
            roles=["admin"]
        )
        exclusions = Exclusions(exclusions_cfg)
        self.assertFalse(user_principal_detail.is_principal_excluded(exclusions))
        self.assertFalse(group_principal_detail.is_principal_excluded(exclusions))
        self.assertFalse(role_principal_detail.is_principal_excluded(exclusions))

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
        expected_results = {
            "groups": {},
            "users": {},
            "roles": {
                "LALALALALAALALA": {
                    "arn": "arn:aws:iam::115657980943:role/aws-service-role/cloudwatch-crossaccount.amazonaws.com/AWSServiceRoleForCloudWatchCrossAccount",
                    "assume_role_policy": {
                        "PolicyDocument": {
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
                        }
                    },
                    "create_date": "2019-11-07 20:21:23+00:00",
                    "id": "LALALALALAALALA",
                    "name": "AWSServiceRoleForCloudWatchCrossAccount",
                    "inline_policies": {},
                    "instance_profiles": [],
                    "instances_count": 0,
                    "path": "/aws-service-role/cloudwatch-crossaccount.amazonaws.com/",
                    "customer_managed_policies": {},
                    "aws_managed_policies": {
                        "LALALALALAALALA": "CloudWatch-CrossAccountAccess"
                    },
                    "is_excluded": False
                }
            },
            "aws_managed_policies": {
                "LALALALALAALALA": {
                    "PolicyName": "CloudWatch-CrossAccountAccess",
                    "PolicyId": "LALALALALAALALA",
                    "Arn": "arn:aws:iam::aws:policy/aws-service-role/CloudWatch-CrossAccountAccess",
                    "Path": "/aws-service-role/",
                    "DefaultVersionId": "v1",
                    "AttachmentCount": 1,
                    "IsAttachable": True,
                    "CreateDate": "2019-07-23 09:59:27+00:00",
                    "UpdateDate": "2019-07-23 09:59:27+00:00",
                    "PolicyVersionList": [
                        {
                            "Document": {
                                "Version": "2012-10-17",
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
                    ],
                    "PrivilegeEscalation": [
                        {
                            "type": "CreateAccessKey",
                            "actions": [
                                "iam:createaccesskey"
                            ]
                        },
                        {
                            "type": "CreateLoginProfile",
                            "actions": [
                                "iam:createloginprofile"
                            ]
                        },
                        {
                            "type": "UpdateLoginProfile",
                            "actions": [
                                "iam:updateloginprofile"
                            ]
                        },
                        {
                            "type": "CreateNewPolicyVersion",
                            "actions": [
                                "iam:createpolicyversion"
                            ]
                        },
                        {
                            "type": "SetExistingDefaultPolicyVersion",
                            "actions": [
                                "iam:setdefaultpolicyversion"
                            ]
                        },
                        {
                            "type": "AttachUserPolicy",
                            "actions": [
                                "iam:attachuserpolicy"
                            ]
                        },
                        {
                            "type": "AttachGroupPolicy",
                            "actions": [
                                "iam:attachgrouppolicy"
                            ]
                        },
                        {
                            "type": "PutUserPolicy",
                            "actions": [
                                "iam:putuserpolicy"
                            ]
                        },
                        {
                            "type": "PutGroupPolicy",
                            "actions": [
                                "iam:putgrouppolicy"
                            ]
                        },
                        {
                            "type": "AddUserToGroup",
                            "actions": [
                                "iam:addusertogroup"
                            ]
                        }
                    ],
                    "DataExfiltration": [],
                    "ResourceExposure": [
                        "iam:AddClientIDToOpenIDConnectProvider",
                        "iam:AddRoleToInstanceProfile",
                        "iam:AddUserToGroup",
                        "iam:AttachGroupPolicy",
                        "iam:AttachRolePolicy",
                        "iam:AttachUserPolicy",
                        "iam:ChangePassword",
                        "iam:CreateAccessKey",
                        "iam:CreateAccountAlias",
                        "iam:CreateGroup",
                        "iam:CreateInstanceProfile",
                        "iam:CreateLoginProfile",
                        "iam:CreateOpenIDConnectProvider",
                        "iam:CreatePolicy",
                        "iam:CreatePolicyVersion",
                        "iam:CreateRole",
                        "iam:CreateSAMLProvider",
                        "iam:CreateServiceLinkedRole",
                        "iam:CreateServiceSpecificCredential",
                        "iam:CreateUser",
                        "iam:CreateVirtualMFADevice",
                        "iam:DeactivateMFADevice",
                        "iam:DeleteAccessKey",
                        "iam:DeleteAccountAlias",
                        "iam:DeleteAccountPasswordPolicy",
                        "iam:DeleteGroup",
                        "iam:DeleteGroupPolicy",
                        "iam:DeleteInstanceProfile",
                        "iam:DeleteLoginProfile",
                        "iam:DeleteOpenIDConnectProvider",
                        "iam:DeletePolicy",
                        "iam:DeletePolicyVersion",
                        "iam:DeleteRole",
                        "iam:DeleteRolePermissionsBoundary",
                        "iam:DeleteRolePolicy",
                        "iam:DeleteSAMLProvider",
                        "iam:DeleteSSHPublicKey",
                        "iam:DeleteServerCertificate",
                        "iam:DeleteServiceLinkedRole",
                        "iam:DeleteServiceSpecificCredential",
                        "iam:DeleteSigningCertificate",
                        "iam:DeleteUser",
                        "iam:DeleteUserPermissionsBoundary",
                        "iam:DeleteUserPolicy",
                        "iam:DeleteVirtualMFADevice",
                        "iam:DetachGroupPolicy",
                        "iam:DetachRolePolicy",
                        "iam:DetachUserPolicy",
                        "iam:EnableMFADevice",
                        "iam:PassRole",
                        "iam:PutGroupPolicy",
                        "iam:PutRolePermissionsBoundary",
                        "iam:PutRolePolicy",
                        "iam:PutUserPermissionsBoundary",
                        "iam:PutUserPolicy",
                        "iam:RemoveClientIDFromOpenIDConnectProvider",
                        "iam:RemoveRoleFromInstanceProfile",
                        "iam:RemoveUserFromGroup",
                        "iam:ResetServiceSpecificCredential",
                        "iam:ResyncMFADevice",
                        "iam:SetDefaultPolicyVersion",
                        "iam:SetSecurityTokenServicePreferences",
                        "iam:UpdateAccessKey",
                        "iam:UpdateAccountPasswordPolicy",
                        "iam:UpdateAssumeRolePolicy",
                        "iam:UpdateGroup",
                        "iam:UpdateLoginProfile",
                        "iam:UpdateOpenIDConnectProviderThumbprint",
                        "iam:UpdateRole",
                        "iam:UpdateRoleDescription",
                        "iam:UpdateSAMLProvider",
                        "iam:UpdateSSHPublicKey",
                        "iam:UpdateServerCertificate",
                        "iam:UpdateServiceSpecificCredential",
                        "iam:UpdateSigningCertificate",
                        "iam:UpdateUser",
                        "iam:UploadSSHPublicKey",
                        "iam:UploadServerCertificate",
                        "iam:UploadSigningCertificate"
                    ],
                    "InfrastructureModification": [
                        "iam:AddClientIDToOpenIDConnectProvider",
                        "iam:AddRoleToInstanceProfile",
                        "iam:AddUserToGroup",
                        "iam:AttachGroupPolicy",
                        "iam:AttachRolePolicy",
                        "iam:AttachUserPolicy",
                        "iam:ChangePassword",
                        "iam:CreateAccessKey",
                        "iam:CreateGroup",
                        "iam:CreateInstanceProfile",
                        "iam:CreateLoginProfile",
                        "iam:CreateOpenIDConnectProvider",
                        "iam:CreatePolicy",
                        "iam:CreatePolicyVersion",
                        "iam:CreateRole",
                        "iam:CreateSAMLProvider",
                        "iam:CreateServiceLinkedRole",
                        "iam:CreateServiceSpecificCredential",
                        "iam:CreateUser",
                        "iam:CreateVirtualMFADevice",
                        "iam:DeactivateMFADevice",
                        "iam:DeleteAccessKey",
                        "iam:DeleteGroup",
                        "iam:DeleteGroupPolicy",
                        "iam:DeleteInstanceProfile",
                        "iam:DeleteLoginProfile",
                        "iam:DeleteOpenIDConnectProvider",
                        "iam:DeletePolicy",
                        "iam:DeletePolicyVersion",
                        "iam:DeleteRole",
                        "iam:DeleteRolePermissionsBoundary",
                        "iam:DeleteRolePolicy",
                        "iam:DeleteSAMLProvider",
                        "iam:DeleteSSHPublicKey",
                        "iam:DeleteServerCertificate",
                        "iam:DeleteServiceLinkedRole",
                        "iam:DeleteServiceSpecificCredential",
                        "iam:DeleteSigningCertificate",
                        "iam:DeleteUser",
                        "iam:DeleteUserPermissionsBoundary",
                        "iam:DeleteUserPolicy",
                        "iam:DeleteVirtualMFADevice",
                        "iam:DetachGroupPolicy",
                        "iam:DetachRolePolicy",
                        "iam:DetachUserPolicy",
                        "iam:EnableMFADevice",
                        "iam:PassRole",
                        "iam:PutGroupPolicy",
                        "iam:PutRolePermissionsBoundary",
                        "iam:PutRolePolicy",
                        "iam:PutUserPermissionsBoundary",
                        "iam:PutUserPolicy",
                        "iam:RemoveClientIDFromOpenIDConnectProvider",
                        "iam:RemoveRoleFromInstanceProfile",
                        "iam:RemoveUserFromGroup",
                        "iam:ResetServiceSpecificCredential",
                        "iam:ResyncMFADevice",
                        "iam:SetDefaultPolicyVersion",
                        "iam:TagRole",
                        "iam:TagUser",
                        "iam:UntagRole",
                        "iam:UntagUser",
                        "iam:UpdateAccessKey",
                        "iam:UpdateAssumeRolePolicy",
                        "iam:UpdateGroup",
                        "iam:UpdateLoginProfile",
                        "iam:UpdateOpenIDConnectProviderThumbprint",
                        "iam:UpdateRole",
                        "iam:UpdateRoleDescription",
                        "iam:UpdateSAMLProvider",
                        "iam:UpdateSSHPublicKey",
                        "iam:UpdateServerCertificate",
                        "iam:UpdateServiceSpecificCredential",
                        "iam:UpdateSigningCertificate",
                        "iam:UpdateUser",
                        "iam:UploadSSHPublicKey",
                        "iam:UploadServerCertificate",
                        "iam:UploadSigningCertificate"
                    ],
                    "is_excluded": False
                }
            },
            "customer_managed_policies": {},
            "inline_policies": {},
            "exclusions": {
                "policies": [
                    "aws-service-role*"
                ]
            }
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)
