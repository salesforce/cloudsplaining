import os
import json
import unittest
from cloudsplaining.scan.authorization_details import AuthorizationDetails, PrincipalPolicyMapping, PrincipalPolicyMappingEntry
from cloudsplaining.shared.exclusions import Exclusions

# Example test file v2
example_authz_details_for_overrides_complete_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "files",
        "example_authz_details_for_overrides_complete.json",
    )
)

with open(example_authz_details_for_overrides_complete_file) as f:
    contents = f.read()
    example_authz_details_for_overrides_complete = json.loads(contents)


example_authz_v2_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "files",
        "example_authz_v2.json",
    )
)

with open(example_authz_v2_file) as f_2:
    contents_2 = f_2.read()
    example_authz_v2 = json.loads(contents_2)


class TestAuthorizationFileDetails(unittest.TestCase):
    def test_authorization_file_details_missing_constraints(self):
        authz_file = {
            "UserDetailList": [
                {
                  "Path": "/",
                  "UserName": "BlakeBortles",
                  "UserId": "BlakeBortles",
                  "Arn": "arn:aws:iam::012345678901:user/BlakeBortles",
                  "CreateDate": "2019-12-18 19:10:08+00:00",
                  "GroupList": [
                    "GOAT"
                  ],
                  "AttachedManagedPolicies": [
                        {
                            "PolicyArn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
                            "PolicyName": "PolicyForTestingOverrides"
                        },{
                            "PolicyArn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
                            "PolicyName": "NotYourPolicy"
                        }
                  ],
                  "Tags": []
                }
            ],
            "GroupDetailList": [],
            "RoleDetailList": [],
            "Policies": [
                {
                    "PolicyName": "NotYourPolicy",
                    "PolicyId": "YAAAAASSQUEEEN",
                    "Arn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
                    "Path": "/",
                    "DefaultVersionId": "v9",
                    "AttachmentCount": 1,
                    "PermissionsBoundaryUsageCount": 0,
                    "IsAttachable": True,
                    "CreateDate": "2020-01-29 21:24:20+00:00",
                    "UpdateDate": "2020-01-29 23:23:12+00:00",
                    "PolicyVersionList": [
                        {
                            "Document": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Sid": "VisualEditor0",
                                        "Effect": "Allow",
                                        "Action": [
                                            "ecr:GetAuthorizationToken",
                                            "ecr:UploadLayerPart",
                                            "ecr:CompleteLayerUpload",
                                            "ecr:PutImage"
                                        ],
                                        "Resource": [
                                            "*"
                                        ]
                                    }
                                ]
                            },
                            "VersionId": "v9",
                            "IsDefaultVersion": True,
                            "CreateDate": "2020-01-29 23:23:12+00:00"
                        }
                    ]
                },
                {
                    "PolicyName": "PolicyForTestingOverrides",
                    "PolicyId": "PolicyForTestingOverrides",
                    "Arn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
                    "Path": "/",
                    "DefaultVersionId": "v9",
                    "AttachmentCount": 1,
                    "PermissionsBoundaryUsageCount": 0,
                    "IsAttachable": True,
                    "CreateDate": "2020-01-29 21:24:20+00:00",
                    "UpdateDate": "2020-01-29 23:23:12+00:00",
                    "PolicyVersionList": [
                        {
                            "Document": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Sid": "VisualEditor0",
                                        "Effect": "Allow",
                                        "Action": [
                                            "s3:CreateBucket"
                                        ],
                                        "Resource": [
                                            "arn:aws:s3:::mybucket"
                                        ]
                                    },
                                    {
                                        "Sid": "VisualEditor1",
                                        "Effect": "Allow",
                                        "Action": [
                                            "s3:PutObject",
                                            "s3:GetObject"
                                        ],
                                        "Resource": [
                                            "*"
                                        ]
                                    }
                                ]
                            },
                            "VersionId": "v9",
                            "IsDefaultVersion": True,
                            "CreateDate": "2020-01-29 23:23:12+00:00"
                        }
                    ]
                }
            ]
        }
        authorization_details = AuthorizationDetails(authz_file)
        results = authorization_details.missing_resource_constraints(modify_only=False)
        expected_results = [
            {
                "AccountID": "012345678901",
                "ManagedBy": "Customer",
                "PolicyName": "NotYourPolicy",
                "Name": "NotYourPolicy",
                "Type": "Policy",
                "Arn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
                "AttachedToPrincipal": None,
                "ActionsCount": 3,
                "ServicesCount": 1,
                "Services": [
                    "ecr"
                ],
                "Actions": [
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart"
                ],
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "VisualEditor0",
                            "Effect": "Allow",
                            "Action": [
                                "ecr:GetAuthorizationToken",
                                "ecr:UploadLayerPart",
                                "ecr:CompleteLayerUpload",
                                "ecr:PutImage"
                            ],
                            "Resource": [
                                "*"
                            ]
                        }
                    ]
                },
                "AssumeRolePolicyDocument": None,
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltration": [],
                "ResourceExposure": []
            },
            {
                "AccountID": "012345678901",
                "ManagedBy": "Customer",
                "PolicyName": "PolicyForTestingOverrides",
                "Type": "Policy",
                "Name": "PolicyForTestingOverrides",
                "Arn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
                "AttachedToPrincipal": None,
                "ActionsCount": 2,
                "ServicesCount": 1,
                "Services": [
                    "s3"
                ],
                "Actions": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "VisualEditor0",
                            "Effect": "Allow",
                            "Action": [
                                "s3:CreateBucket"
                            ],
                            "Resource": [
                                "arn:aws:s3:::mybucket"
                            ]
                        },
                        {
                            "Sid": "VisualEditor1",
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject",
                                "s3:GetObject"
                            ],
                            "Resource": [
                                "*"
                            ]
                        }
                    ]
                },
                "AssumeRolePolicyDocument": None,
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltration": [
                    "s3:GetObject"
                ],
                "ResourceExposure": []
            }
        ]

        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertListEqual(results, expected_results)

    def test_authorization_file_details_missing_constraints_v2(self):
        authorization_details = AuthorizationDetails(example_authz_details_for_overrides_complete)
        result = authorization_details.missing_resource_constraints(modify_only=False)
        expected_results_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "scanning",
                "test_authorization_file_details_missing_constraints_v2.json",
            )
        )

        # print(expected_results_file)
        with open(expected_results_file) as json_file:
            expected_result = json.load(json_file)
        # print(json.dumps(result, indent=4))
        self.maxDiff = None
        self.assertListEqual(result, expected_result)

    def test_authorization_details_attributes(self):
        authorization_details = AuthorizationDetails(example_authz_details_for_overrides_complete)
        self.assertListEqual(authorization_details.aws_managed_policies_in_use, ['AdministratorAccess'])
        self.assertListEqual(authorization_details.users, ['BlakeBortles'])
        self.assertListEqual(authorization_details.groups, ['GOATGroup'])
        self.assertListEqual(authorization_details.roles, ['GOATRole', 'MyOtherRole'])

    def test_principal_policy_mapping(self):
        authorization_details = AuthorizationDetails(example_authz_details_for_overrides_complete)
        expected_results = [
            {
                "Principal": "GOATGroup",
                "Type": "Group",
                "PolicyType": "Managed",
                "ManagedBy": "AWS",
                "PolicyName": "AdministratorAccess",
                "GroupMembership": [
                    "BlakeBortles"
                ]
            },
            {
                "Principal": "GOATGroup",
                "Type": "Group",
                "PolicyType": "Managed",
                "ManagedBy": "Customer",
                "PolicyName": "NotYourPolicy",
                "GroupMembership": [
                    "BlakeBortles"
                ]
            },
            {
                "Principal": "GOATRole",
                "Type": "Role",
                "PolicyType": "Inline",
                "ManagedBy": "Customer",
                "PolicyName": "SsmOnboardingInlinePolicy",
                "GroupMembership": None
            },
            {
                "Principal": "GOATRole",
                "Type": "Role",
                "PolicyType": "Managed",
                "ManagedBy": "AWS",
                "PolicyName": "AdministratorAccess",
                "GroupMembership": None
            },
            {
                "Principal": "GOATRole",
                "Type": "Role",
                "PolicyType": "Managed",
                "ManagedBy": "Customer",
                "PolicyName": "PolicyForTestingOverrides",
                "GroupMembership": None
            },
            {
                "Principal": "MyOtherRole",
                "Type": "Role",
                "PolicyType": "Inline",
                "ManagedBy": "Customer",
                "PolicyName": "InlinePolicyForTestingOverrides",
                "GroupMembership": None
            },
            {
                "Principal": "BlakeBortles",
                "Type": "User",
                "PolicyType": "Managed",
                "ManagedBy": "AWS",
                "PolicyName": "AdministratorAccess",
                "GroupMembership": [
                    "GOATGroup"
                ]
            },
            {
                "Principal": "BlakeBortles",
                "Type": "User",
                "PolicyType": "Managed",
                "ManagedBy": "Customer",
                "PolicyName": "NotYourPolicy",
                "GroupMembership": [
                    "GOATGroup"
                ]
            }
        ]
        # print(json.dumps(authorization_details.principal_policy_mapping, indent=4))
        self.maxDiff = None
        self.assertListEqual(authorization_details.principal_policy_mapping, expected_results)

    def test_user_principal_attached_managed_policies(self):
        # User with attached managed policies
        authz_cfg = {
            "UserDetailList": [
                {
                  "Path": "/",
                  "UserName": "BlakeBortles",
                  "UserId": "BlakeBortles",
                  "Arn": "arn:aws:iam::012345678901:user/BlakeBortles",
                  "CreateDate": "2019-12-18 19:10:08+00:00",
                  "GroupList": [
                    "GOAT"
                  ],
                  "AttachedManagedPolicies": [
                    {
                        "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess",
                        "PolicyName": "AdministratorAccess"
                    }
                    ],
                  "Tags": []
                },
            ],
            "GroupDetailList": [],
            "RoleDetailList": [],
            "Policies": [
                {
                    "PolicyName": "AdministratorAccess",
                    "PolicyId": "ANPAIWMBCKSKIEE64ZLYK",
                    "Arn": "arn:aws:iam::aws:policy/AdministratorAccess",
                    "Path": "/",
                    "DefaultVersionId": "v1",
                    "AttachmentCount": 1,
                    "PermissionsBoundaryUsageCount": None,
                    "IsAttachable": True,
                    "CreateDate": "2015-02-06 18:39:46+00:00",
                    "UpdateDate": "2015-02-06 18:39:46+00:00",
                    "PolicyVersionList": [
                        {
                            "Document": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": "*",
                                        "Resource": "*"
                                    }
                                ]
                            },
                            "VersionId": "v1",
                            "IsDefaultVersion": True,
                            "CreateDate": "2015-02-06 18:39:46+00:00"
                        }
                    ]
                },
            ]
        }
        authorization_details = AuthorizationDetails(authz_cfg)
        expected_result = ["AdministratorAccess"]
        results = authorization_details.aws_managed_policies_in_use
        # print(json.dumps(results, indent=4))
        self.assertListEqual(results, expected_result)


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

    def test_principal_policy_mapping(self):
        principal_policy_mapping = PrincipalPolicyMapping()
        principal_policy_mapping.add_with_detail(
            "Bob", "User", "Inline", "Customer", "MyPolicy", "Group membership"
        )
        result = principal_policy_mapping.json
        # print(json.dumps(result, indent=4))
        expected_result = [
            {
                "Principal": "Bob",
                "Type": "User",
                "PolicyType": "Inline",
                "ManagedBy": "Customer",
                "PolicyName": "MyPolicy",
                "Comment": "Group membership"
            }
        ]
        self.assertListEqual(result, expected_result)

    def test_full_exclusions_case(self):
        principal_policy_mapping = PrincipalPolicyMapping()
        principal_policy_mapping.add_with_detail("AdminUsers", "Group", "Managed", "AWS", "AdministratorAccess", None)
        principal_policy_mapping.add_with_detail("NginxServer", "Role", "Inline", "Customer", "SsmOnboardingInlinePolicy", None)
        principal_policy_mapping.add_with_detail("SsoDeveloperRole", "Role", "Inline", "Customer", "InlinePolicyForTestingOverride", None)
        principal_policy_mapping.add_with_detail("Obama", "User", "Managed", "AWS", "AdministratorAccess", ["AdminUsers"])  # via AdminUsers
        principal_policy_mapping.add_with_detail("Pelosi", "User", "Managed", "Customer", "PowerUserCustom", None)  # Managed policy directly attached to user
        # Note how above there is only one user with AdministratorAccess - Obama.
        # If we exclude obama, we should be able to not include the group
        exclusions_cfg = {
            # We only care about the "Obama" user here.
            "users": ["Obama"],
            "policies": [
                "aws-service-role*"
            ],
            "roles": ["aws-service-role*"],
            "include-actions": ["s3:GetObject"],
            "exclude-actions": ["kms:Decrypt"]
        }
        exclusions = Exclusions(exclusions_cfg)
        results = principal_policy_mapping.get_post_exclusion_principal_policy_mapping(exclusions)
        # print(json.dumps(results.json, indent=4))
        # Obama should not be included in the results
        self.assertTrue(False for entry in results.json if "Obama" in entry["Principal"])
        self.assertTrue(False for entry in results.json if "AdminUsers" in entry["Principal"])
        # The results should not include Obama OR AdministratorAccess
        # Now let's add Biden. The results should now include AdminUsers AND Biden, but NOT Obama
        principal_policy_mapping.add_with_detail("Biden", "User", "Managed", "AWS", "AdministratorAccess", ["AdminUsers"])
        results = principal_policy_mapping.get_post_exclusion_principal_policy_mapping(exclusions)
        # print(json.dumps(results.json, indent=4))
        self.assertTrue(True for entry in results.json if "AdminUsers" in entry["Principal"])
        self.assertTrue(True for entry in results.json if "Biden" in entry["Principal"])
        # Let's just print it out here so it's easy to visualize the results in the test file
        expected_results = [
            {
                "Principal": "AdminUsers",
                "Type": "Group",
                "PolicyType": "Managed",
                "ManagedBy": "AWS",
                "PolicyName": "AdministratorAccess",
                "Comment": None
            },
            {
                "Principal": "NginxServer",
                "Type": "Role",
                "PolicyType": "Inline",
                "ManagedBy": "Customer",
                "PolicyName": "SsmOnboardingInlinePolicy",
                "Comment": None
            },
            {
                "Principal": "SsoDeveloperRole",
                "Type": "Role",
                "PolicyType": "Inline",
                "ManagedBy": "Customer",
                "PolicyName": "InlinePolicyForTestingOverride",
                "Comment": None
            },
            {
                "Principal": "Biden",
                "Type": "User",
                "PolicyType": "Managed",
                "ManagedBy": "AWS",
                "PolicyName": "AdministratorAccess",
                "Comment": [
                    "AdminUsers"
                ]
            }
        ]
        self.assertListEqual(results.json, expected_results)
