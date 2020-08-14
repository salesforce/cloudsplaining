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


expected_user_detail_policy_results_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "files",
        "scanning",
        "test_user_detail_results.json",
    )
)
with open(expected_user_detail_policy_results_file) as f:
    contents = f.read()
    expected_user_detail_policy_results = json.loads(contents)


class TestUserDetail(unittest.TestCase):
    def test_user_detail_attached_managed_policies(self):
        user_detail_json_input = auth_details_json["UserDetailList"][2]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))

        all_group_details_json = auth_details_json["GroupDetailList"]
        all_group_details = GroupDetailList(all_group_details_json, policy_details)

        user_detail = UserDetail(user_detail_json_input, policy_details, all_group_details)
        expected_result = expected_user_detail_policy_results
        results = user_detail.json
        # print(json.dumps(results))
        self.assertDictEqual(results, expected_result)
