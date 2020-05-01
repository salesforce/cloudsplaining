import os
import unittest
import json
from cloudsplaining.scan.principals import Principal, PrincipalTypeDetails

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


# class TestPrincipalTypeDetails(unittest.TestCase):
#
#     def test_principal_type_details(self):
#         raw_role_detail_list = auth_details_json.get("RoleDetailList")
#         role_detail_list = PrincipalTypeDetails(raw_role_detail_list)


class TestPrincipal(unittest.TestCase):
    def test_principal(self):

        principal_detail = auth_details_json["UserDetailList"][1]
        user_principal = Principal(principal_detail)
        result = user_principal.policy_list[0]["PolicyDocument"].json
        expected_result = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:PutObjectAcl",
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "*"
                    ]
                }
            ]
        }
        self.assertDictEqual(result, expected_result)
        result = user_principal.policy_list[0]["PolicyName"]
        expected_result = "InsecureUserPolicy"
        self.assertEqual(result, expected_result)

    def test_principal_attributes(self):
        """scan.principals.Principal: Testing Principal simple attributes"""
        principal_detail = auth_details_json["UserDetailList"][1]
        user_principal = Principal(principal_detail)
        self.assertEqual(user_principal.name, "userwithlotsofpermissions")
        self.assertEqual(user_principal.principal_type, "User")

    def test_account_id(self):
        """scan.principals.Principal.account_id"""
        principal_detail = auth_details_json["UserDetailList"][1]
        user_principal = Principal(principal_detail)
        self.assertEqual(user_principal.account_id, "012345678901")


class TestPrincipalTrustPolicies(unittest.TestCase):
    def test_principal_assume_role(self):
        """scan.principals.Principal.assume_role_from_compute"""
        principal_detail = auth_details_json["RoleDetailList"][2]
        # print(json.dumps(principal_detail, indent=4))
        role_principal = Principal(principal_detail)
        print(json.dumps(role_principal.assume_role_policy_document, indent=4))
