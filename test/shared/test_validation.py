import unittest
from cloudsplaining.shared.validation import check_authorization_details_schema
import os
import json


class FindExcessiveWildcardsTestCase(unittest.TestCase):
    def test_check_authorization_details_schema(self):
        """test_scanning.validate.check_authorization_details_schema"""
        example_authz_details_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "example-authz-details.json",
            )
        )
        with open(example_authz_details_file, "r") as json_file:
            cfg = json.load(json_file)
            decision = check_authorization_details_schema(cfg)
        self.assertTrue(decision)
