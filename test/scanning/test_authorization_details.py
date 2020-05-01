from cloudsplaining.scan.authorization_details import AuthorizationDetails
import os
import json
import unittest

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
            "UserDetailList": [],
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
                "Arn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
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
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [],
                "PermissionsManagementActions": [],
                "WriteActions": [
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart"
                ],
                "TaggingActions": []
            },
            {
                "AccountID": "012345678901",
                "ManagedBy": "Customer",
                "PolicyName": "PolicyForTestingOverrides",
                "Arn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
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
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [
                    "s3:GetObject"
                ],
                "PermissionsManagementActions": [],
                "WriteActions": [
                    "s3:PutObject"
                ],
                "TaggingActions": []
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
        self.assertListEqual(authorization_details.groups, ['GOAT'])
        self.assertListEqual(authorization_details.roles, ['GOAT', 'MyOtherRole'])



