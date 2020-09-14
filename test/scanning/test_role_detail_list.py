import os
import unittest
import json
from cloudsplaining.scan.role_details import RoleDetail
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


class TestRoleDetail(unittest.TestCase):
    def test_role_detail_attached_managed_policies(self):
        role_detail_json_input = auth_details_json["RoleDetailList"][2]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))

        role_detail = RoleDetail(role_detail_json_input, policy_details)
        expected_detail_policy_results_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "scanning",
                "test_role_detail_results.json",
            )
        )
        with open(expected_detail_policy_results_file) as f:
            contents = f.read()
            expected_result = json.loads(contents)

        results = role_detail.json
        # print(json.dumps(results))
        self.maxDiff = None
        self.assertDictEqual(results, expected_result)
