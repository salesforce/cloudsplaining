import os
import unittest
import json
from cloudsplaining.scan.authorization_details import AuthorizationDetails

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

example_data_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "files",
        "new_data_file.json",
    )
)
with open(example_data_file) as f:
    contents = f.read()
    expected_data_file = json.loads(contents)


class TestNewDataFilePolicyDetail(unittest.TestCase):
    def test_new_principal_policy_mapping(self):
        authorization_details = AuthorizationDetails(auth_details_json)
        results = authorization_details.results
        # print(json.dumps(results))
        self.assertDictEqual(expected_data_file, results)
