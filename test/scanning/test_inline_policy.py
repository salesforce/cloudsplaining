import os
import unittest
import json
from cloudsplaining.scan.inline_policy import InlinePolicy

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


class TestInlinePolicyDetail(unittest.TestCase):
    def test_inline_policies(self):
        inline_policy_detail = {
          "PolicyName": "InlinePolicyForBidenGroup",
          "PolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                  "s3:GetObject",
                  "s3:PutObjectAcl"
                ],
                "Resource": "*"
              }
            ]
          }
        }
        inline_policy = InlinePolicy(inline_policy_detail)
        results = inline_policy.json
        # print(json.dumps(results))

        expected_policy_details_results_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "scanning",
                "test_inline_policy_results.json",
            )
        )
        with open(expected_policy_details_results_file) as f:
            contents = f.read()
            expected_results = json.loads(contents)

        self.assertDictEqual(results, expected_results)
