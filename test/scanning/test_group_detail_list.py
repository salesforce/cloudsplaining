import os
import unittest
import json
from cloudsplaining.scan.group_details import GroupDetail, GroupDetailList
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails

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


class TestGroupDetail(unittest.TestCase):
    def test_group_detail_attached_managed_policies(self):
        group_detail_json_input = auth_details_json["GroupDetailList"][1]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))

        group_detail = GroupDetail(group_detail_json_input, policy_details)
        results = group_detail.json

        expected_group_detail_policy_results_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "scanning",
                "test_group_detail_results.json",
            )
        )
        with open(expected_group_detail_policy_results_file) as f:
            contents = f.read()
            expected_group_detail_policy_results = json.loads(contents)
        # print(json.dumps(results))
        self.maxDiff = None
        self.assertDictEqual(results, expected_group_detail_policy_results)

        # Get the list of allowed actions
        results = group_detail.all_allowed_actions
        # print(json.dumps(results, indent=4))
        # print(len(results))
        self.assertTrue(len(results) > 100)

    def test_group_detail_list_allowed_actions_lookup(self):
        group_details_json_input = auth_details_json["GroupDetailList"]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
        group_detail_list = GroupDetailList(group_details_json_input, policy_details)
        # print(group_detail_list.group_names)
        actions = group_detail_list.get_all_allowed_actions_for_group('biden')
        self.assertTrue("s3:GetObject" in actions)
        # privileges = group_detail_list.get_all_iam_statements_for_group('biden')
