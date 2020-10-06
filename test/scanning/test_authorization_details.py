import os
import json
import unittest
from cloudsplaining.scan.authorization_details import AuthorizationDetails
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


# class TestAuthorizationFileDetails(unittest.TestCase):
#     def test_authorization_file_details_missing_constraints(self):
#         authz_file = {
#             "UserDetailList": [
#                 {
#                   "Path": "/",
#                   "UserName": "BlakeBortles",
#                   "UserId": "BlakeBortles",
#                   "Arn": "arn:aws:iam::012345678901:user/BlakeBortles",
#                   "CreateDate": "2019-12-18 19:10:08+00:00",
#                   "GroupList": [
#                     "GOAT"
#                   ],
#                   "AttachedManagedPolicies": [
#                         {
#                             "PolicyArn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
#                             "PolicyName": "PolicyForTestingOverrides"
#                         },{
#                             "PolicyArn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
#                             "PolicyName": "NotYourPolicy"
#                         }
#                   ],
#                   "Tags": []
#                 }
#             ],
#             "GroupDetailList": [],
#             "RoleDetailList": [],
#             "Policies": [
#                 {
#                     "PolicyName": "NotYourPolicy",
#                     "PolicyId": "YAAAAASSQUEEEN",
#                     "Arn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
#                     "Path": "/",
#                     "DefaultVersionId": "v9",
#                     "AttachmentCount": 1,
#                     "PermissionsBoundaryUsageCount": 0,
#                     "IsAttachable": True,
#                     "CreateDate": "2020-01-29 21:24:20+00:00",
#                     "UpdateDate": "2020-01-29 23:23:12+00:00",
#                     "PolicyVersionList": [
#                         {
#                             "Document": {
#                                 "Version": "2012-10-17",
#                                 "Statement": [
#                                     {
#                                         "Sid": "VisualEditor0",
#                                         "Effect": "Allow",
#                                         "Action": [
#                                             "ecr:GetAuthorizationToken",
#                                             "ecr:UploadLayerPart",
#                                             "ecr:CompleteLayerUpload",
#                                             "ecr:PutImage"
#                                         ],
#                                         "Resource": [
#                                             "*"
#                                         ]
#                                     }
#                                 ]
#                             },
#                             "VersionId": "v9",
#                             "IsDefaultVersion": True,
#                             "CreateDate": "2020-01-29 23:23:12+00:00"
#                         }
#                     ]
#                 },
#                 {
#                     "PolicyName": "PolicyForTestingOverrides",
#                     "PolicyId": "PolicyForTestingOverrides",
#                     "Arn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
#                     "Path": "/",
#                     "DefaultVersionId": "v9",
#                     "AttachmentCount": 1,
#                     "PermissionsBoundaryUsageCount": 0,
#                     "IsAttachable": True,
#                     "CreateDate": "2020-01-29 21:24:20+00:00",
#                     "UpdateDate": "2020-01-29 23:23:12+00:00",
#                     "PolicyVersionList": [
#                         {
#                             "Document": {
#                                 "Version": "2012-10-17",
#                                 "Statement": [
#                                     {
#                                         "Sid": "VisualEditor0",
#                                         "Effect": "Allow",
#                                         "Action": [
#                                             "s3:CreateBucket"
#                                         ],
#                                         "Resource": [
#                                             "arn:aws:s3:::mybucket"
#                                         ]
#                                     },
#                                     {
#                                         "Sid": "VisualEditor1",
#                                         "Effect": "Allow",
#                                         "Action": [
#                                             "s3:PutObject",
#                                             "s3:GetObject"
#                                         ],
#                                         "Resource": [
#                                             "*"
#                                         ]
#                                     }
#                                 ]
#                             },
#                             "VersionId": "v9",
#                             "IsDefaultVersion": True,
#                             "CreateDate": "2020-01-29 23:23:12+00:00"
#                         }
#                     ]
#                 }
#             ]
#         }
#         authorization_details = AuthorizationDetails(authz_file)
#         results = authorization_details.results
#         expected_results = {
#             "groups": {},
#             "users": {
#                 "BlakeBortles": {
#                     "arn": "arn:aws:iam::012345678901:user/BlakeBortles",
#                     "create_date": "2019-12-18 19:10:08+00:00",
#                     "id": "BlakeBortles",
#                     "name": "BlakeBortles",
#                     "inline_policies": {},
#                     "groups": {},
#                     "path": "/",
#                     "customer_managed_policies": {
#                         "PolicyForTestingOverrides": "PolicyForTestingOverrides",
#                         "YAAAAASSQUEEEN": "NotYourPolicy"
#                     },
#                     "aws_managed_policies": {},
#                     "is_excluded": False
#                 }
#             },
#             "roles": {},
#             "aws_managed_policies": {},
#             "customer_managed_policies": {
#                 "YAAAAASSQUEEEN": {
#                     "PolicyName": "NotYourPolicy",
#                     "PolicyId": "YAAAAASSQUEEEN",
#                     "Arn": "arn:aws:iam::012345678901:policy/NotYourPolicy",
#                     "Path": "/",
#                     "DefaultVersionId": "v9",
#                     "AttachmentCount": 1,
#                     "IsAttachable": True,
#                     "CreateDate": "2020-01-29 21:24:20+00:00",
#                     "UpdateDate": "2020-01-29 23:23:12+00:00",
#                     "PolicyVersionList": [
#                         {
#                             "Document": {
#                                 "Version": "2012-10-17",
#                                 "Statement": [
#                                     {
#                                         "Sid": "VisualEditor0",
#                                         "Effect": "Allow",
#                                         "Action": [
#                                             "ecr:GetAuthorizationToken",
#                                             "ecr:UploadLayerPart",
#                                             "ecr:CompleteLayerUpload",
#                                             "ecr:PutImage"
#                                         ],
#                                         "Resource": [
#                                             "*"
#                                         ]
#                                     }
#                                 ]
#                             },
#                             "VersionId": "v9",
#                             "IsDefaultVersion": True,
#                             "CreateDate": "2020-01-29 23:23:12+00:00"
#                         }
#                     ],
#                     "PrivilegeEscalation": [],
#                     "DataExfiltration": [],
#                     "ResourceExposure": [],
#                     "ServiceWildcard": [],
#                     "CredentialsExposure": [
#                         "ecr:GetAuthorizationToken"
#                     ],
#                     "InfrastructureModification": [
#                         "ecr:CompleteLayerUpload",
#                         "ecr:PutImage",
#                         "ecr:UploadLayerPart"
#                     ],
#                     "is_excluded": False
#                 },
#                 "PolicyForTestingOverrides": {
#                     "PolicyName": "PolicyForTestingOverrides",
#                     "PolicyId": "PolicyForTestingOverrides",
#                     "Arn": "arn:aws:iam::012345678901:policy/PolicyForTestingOverrides",
#                     "Path": "/",
#                     "DefaultVersionId": "v9",
#                     "AttachmentCount": 1,
#                     "IsAttachable": True,
#                     "CreateDate": "2020-01-29 21:24:20+00:00",
#                     "UpdateDate": "2020-01-29 23:23:12+00:00",
#                     "PolicyVersionList": [
#                         {
#                             "Document": {
#                                 "Version": "2012-10-17",
#                                 "Statement": [
#                                     {
#                                         "Sid": "VisualEditor0",
#                                         "Effect": "Allow",
#                                         "Action": [
#                                             "s3:CreateBucket"
#                                         ],
#                                         "Resource": [
#                                             "arn:aws:s3:::mybucket"
#                                         ]
#                                     },
#                                     {
#                                         "Sid": "VisualEditor1",
#                                         "Effect": "Allow",
#                                         "Action": [
#                                             "s3:PutObject",
#                                             "s3:GetObject"
#                                         ],
#                                         "Resource": [
#                                             "*"
#                                         ]
#                                     }
#                                 ]
#                             },
#                             "VersionId": "v9",
#                             "IsDefaultVersion": True,
#                             "CreateDate": "2020-01-29 23:23:12+00:00"
#                         }
#                     ],
#                     "PrivilegeEscalation": [],
#                     "DataExfiltration": [
#                         "s3:GetObject"
#                     ],
#                     "ResourceExposure": [],
#                     "ServiceWildcard": [],
#                     "CredentialsExposure": [],
#                     "InfrastructureModification": [
#                         "s3:GetObject",
#                         "s3:PutObject"
#                     ],
#                     "is_excluded": False
#                 }
#             },
#             "inline_policies": {},
#             "exclusions": {
#                 "policies": [
#                     "AWSServiceRoleFor*",
#                     "*ServiceRolePolicy",
#                     "*ServiceLinkedRolePolicy",
#                     "AdministratorAccess",
#                     "service-role*",
#                     "aws-service-role*",
#                     "/service-role*",
#                     "/aws-service-role*",
#                     "MyRole"
#                 ],
#                 "roles": [
#                     "service-role*",
#                     "aws-service-role*"
#                 ],
#                 "users": [
#                     ""
#                 ],
#                 "groups": [
#                     ""
#                 ],
#                 "include-actions": [
#                     "s3:GetObject",
#                     "ssm:GetParameter",
#                     "ssm:GetParameters",
#                     "ssm:GetParametersByPath",
#                     "secretsmanager:GetSecretValue",
#                     "rds:CopyDBSnapshot",
#                     "rds:CreateDBSnapshot"
#                 ],
#                 "exclude-actions": [
#                     ""
#                 ]
#             }
#         }
#
#         # print(json.dumps(results, indent=4))
#         self.maxDiff = None
#         self.assertDictEqual(results, expected_results)
