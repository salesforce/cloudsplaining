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
        expected_finding_json = {
            "AccountID": "123456789012",
            "ManagedBy": "Customer",
            "PolicyName": "MyPolicy",
            "Type": "Group",
            "Arn": "arn:aws:iam::123456789012:group/SNSNotifications",
            "ActionsCount": 1,
            "ServicesCount": 1,
            "Services": [
                "s3"
            ],
            "Actions": [
                "s3:GetObject"
            ],
            "PolicyDocument": {
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
            },
            "AssumableByComputeService": [],
            "AssumeRolePolicyDocument": None,
            "PrivilegeEscalation": [],
            "DataExfiltrationActions": [
                "s3:GetObject"
            ],
            "PermissionsManagementActions": [],
            "WriteActions": [],
            "TaggingActions": []
        }
        # print(json.dumps(finding.json, indent=4))
        self.assertDictEqual(finding.json, expected_finding_json)

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
        # print(finding.role_assumable_by_compute_services)
        self.assertListEqual(finding.role_assumable_by_compute_services, ["ecs-tasks"])

    def test_findings_for_roles_assumable_by_compute_services_empty(self):
        """output.findings.role_assumable_by_compute_services"""
        trust_policy_from_non_compute_service = {
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
        assume_role_policy_document = AssumeRolePolicyDocument(trust_policy_from_non_compute_service)

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
        # print(json.dumps(finding.assume_role_policy_document_json, indent=4))
        self.assertDictEqual(finding.assume_role_policy_document_json, trust_policy_from_non_compute_service)
