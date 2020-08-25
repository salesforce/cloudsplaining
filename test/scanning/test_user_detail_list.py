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
          "inline_policies": {
            "4d5d2bf1baaf66fd24b21397410fd0eb30ab5758d69fc365b1862dd9a5be5eb8": "InsecureUserPolicy"
          },
          "inline_policies_count": 1,
          "groups": {
            "biden": {
              "arn": "arn:aws:iam::012345678901:group/biden",
              "create_date": "2017-05-15 17:33:36+00:00",
              "id": "aaaaaaaaabbbbbbbccccccc",
              "inline_policies": {
                "9dfb8b36ce6c68a741355e7a2ab5ee62a47755f8f25d68e4fa6f87dabc036986": "InlinePolicyForBidenGroup"
              },
              "inline_policies_count": 1,
              "path": "/",
              "managed_policies_count": 1,
              "managed_policies": {
                "ANPAI3R4QMOG6Q5A4VWVG": "AmazonRDSFullAccess"
              }
            }
          },
          "path": "/",
          "managed_policies_count": 1,
          "managed_policies": {
            "ANPAI6E2CYYMI4XI7AA5K": "AWSLambdaFullAccess"
          }
        }

        results = user_detail.json
        # print(json.dumps(results))
        # self.maxDiff = None
        self.assertDictEqual(results, expected_result)
