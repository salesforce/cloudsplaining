import os
import unittest
import json
from cloudsplaining.scan.group_details import GroupDetailList
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails
from cloudsplaining.scan.user_details import UserDetail

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


class TestUserDetail(unittest.TestCase):
    def test_user_detail_attached_managed_policies(self):
        user_detail_json_input = auth_details_json["UserDetailList"][2]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))

        all_group_details_json = auth_details_json["GroupDetailList"]
        all_group_details = GroupDetailList(all_group_details_json, policy_details)

        user_detail = UserDetail(user_detail_json_input, policy_details, all_group_details)
        expected_result = {
            "arn": "arn:aws:iam::012345678901:user/biden",
            "create_date": "2019-12-18 19:10:08+00:00",
            "id": "biden",
            "name": "biden",
            "inline_policies": {
                "354d81e1788639707f707738fb4c630cb7c5d23614cc467ff9a469a670049e3f": "InsecureUserPolicy"
            },
            "groups": {
                "biden": {
                    "arn": "arn:aws:iam::012345678901:group/biden",
                    "name": "biden",
                    "create_date": "2017-05-15 17:33:36+00:00",
                    "id": "aaaaaaaaabbbbbbbccccccc",
                    "inline_policies": {
                        "e8bca32ff7d1f7990d71c64d95a04b7caa5aad5791f06f69db59653228c6853d": "InlinePolicyForBidenGroup"
                    },
                    "path": "/",
                    "customer_managed_policies": {},
                    "aws_managed_policies": {
                        "ANPAI3R4QMOG6Q5A4VWVG": "AmazonRDSFullAccess"
                    },
                    "is_excluded": False
                }
            },
            "path": "/",
            "customer_managed_policies": {},
            "aws_managed_policies": {
                "ANPAI6E2CYYMI4XI7AA5K": "AWSLambdaFullAccess"
            },
            "is_excluded": False
        }
        results = user_detail.json
        # print(json.dumps(results, indent=4))
        # self.maxDiff = None
        self.assertDictEqual(results, expected_result)
