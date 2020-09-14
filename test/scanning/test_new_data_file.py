import os
import unittest
import json
from cloudsplaining.scan.authorization_details import AuthorizationDetails

example_authz_details_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
        "examples",
        "files",
        "example.json",
    )
)
# print(example_authz_details_file)
with open(example_authz_details_file, "r") as json_file:
    cfg = json.load(json_file)

example_data_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "files",
        "new_data_file.json",
    )
)
with open(example_data_file, 'r') as json_file:
    expected_data_file = json.load(json_file)


class TestNewDataFilePolicyDetail(unittest.TestCase):
    def test_new_principal_policy_mapping(self):
        authorization_details = AuthorizationDetails(cfg)
        results = authorization_details.results()
        # print(json.dumps(results))
        self.assertDictEqual(expected_data_file, results)
