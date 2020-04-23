import unittest
import os
import json
from cloudsplaining.command.scan_policy_file import scan_policy
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG


class PolicyFileTestCase(unittest.TestCase):
    def test_policy_file(self):
        policy_test_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "test_policy_file.json",
            )
        )

        # print(expected_results_file)
        with open(policy_test_file) as json_file:
            example_policy = json.load(json_file)
        expected_results = [
            'ecr:CompleteLayerUpload',
            'ecr:InitiateLayerUpload',
            'ecr:PutImage',
            'ecr:UploadLayerPart'
        ]
        all_access_levels = False
        result = scan_policy(example_policy, DEFAULT_EXCLUSIONS_CONFIG, all_access_levels)
        self.assertListEqual(result, expected_results)
