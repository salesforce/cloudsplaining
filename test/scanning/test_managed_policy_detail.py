import os
import unittest
import json
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


class TestManagedPolicyDetail(unittest.TestCase):
    def test_managed_policies(self):
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
        results = policy_details.json
        print(json.dumps(results))

        expected_policy_details_results_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "scanning",
                "test_managed_policy_details.json",
            )
        )
        with open(expected_policy_details_results_file) as f:
            contents = f.read()
            expected_results = json.loads(contents)

        self.assertDictEqual(results, expected_results)
