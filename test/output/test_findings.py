import unittest
import json
from cloudsplaining.output.findings import Finding
from cloudsplaining.scan.policy_document import PolicyDocument

class TestFindings(unittest.TestCase):
    def test_finding_attributes(self):
        """scan.findings.finding"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        finding = Finding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/SNSNotifications",
            actions=["s3:GetObject"],
            policy_document=policy_document
        )
        self.assertEqual(finding.account_id, "123456789012")
        self.assertEqual(finding.managed_by, "Customer")
        self.assertEqual(len(finding.services_affected), 1)
        self.assertEqual(len(finding.actions), 1)
        self.assertDictEqual(finding.policy_document.json, policy_document.json)
        print(json.dumps(finding.json, indent=4))
