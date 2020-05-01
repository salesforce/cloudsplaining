import unittest
import json
from cloudsplaining.output.findings import Finding
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.scan.assume_role_policy_document import AssumeRolePolicyDocument

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

    def test_findings_for_roles_assumable_by_compute_services_ecs_tasks(self):
        """output.findings.role_assumable_by_compute_services: ecs-tasks"""
        trust_policy_from_compute_service_ecs_tasks = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sts:AssumeRole"
                    ],
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com",
                        "AWS": "arn:aws:iam::012345678910:root",
                    }
                }
            ]
        }
        assume_role_policy_document = AssumeRolePolicyDocument(trust_policy_from_compute_service_ecs_tasks)

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
            arn="arn:aws:iam::123456789012:role/TestComputeService",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            assume_role_policy_document=assume_role_policy_document
        )
        print(finding.role_assumable_by_compute_services)
        self.assertListEqual(finding.role_assumable_by_compute_services, ["ecs-tasks"])

    def test_findings_for_roles_assumable_by_compute_services_empty(self):
        """output.findings.role_assumable_by_compute_services"""
        trust_policy_from_compute_service_ecs_tasks = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sts:AssumeRole"
                    ],
                    "Principal": {
                        "Service": ["yolo.amazonaws.com"]
                    }
                }
            ]
        }
        assume_role_policy_document = AssumeRolePolicyDocument(trust_policy_from_compute_service_ecs_tasks)

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
            arn="arn:aws:iam::123456789012:role/TestComputeService",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            assume_role_policy_document=assume_role_policy_document
        )
        self.assertListEqual(finding.role_assumable_by_compute_services, [])
