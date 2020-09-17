import unittest
import json
from cloudsplaining.output.policy_finding import PolicyFinding
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.exclusions import Exclusions


class TestPolicyFinding(unittest.TestCase):
    def test_policy_finding_for_data_exfiltration(self):
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
        # (1) If the user is a member of an excluded group, return True

        exclusions_cfg = dict(
            users=["obama"],
            groups=["exclude-group"],
            roles=["MyRole"],
            policies=["exclude-policy"]
        )
        exclusions = Exclusions(exclusions_cfg)
        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["s3"],
            "PrivilegeEscalation": [],
            "ResourceExposure": [],
            "DataExfiltration": [
                "s3:GetObject"
            ],
            "ServiceWildcard": [],
            "CredentialsExposure": [],
            "InfrastructureModification": [],
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

    def test_policy_finding_for_resource_exposure(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObjectAcl"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)

        exclusions_cfg = dict()
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["s3"],
            "PrivilegeEscalation": [],
            "ResourceExposure": ["s3:PutObjectAcl"],
            "DataExfiltration": [],
            "ServiceWildcard": [],
            "CredentialsExposure": [],
            "InfrastructureModification": ["s3:PutObjectAcl"],
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

    def test_policy_finding_for_privilege_escalation(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreatePolicyVersion"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)

        exclusions_cfg = dict()
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["iam"],
            "PrivilegeEscalation": [
                {
                    "type": "CreateNewPolicyVersion",
                    "actions": ["iam:createpolicyversion"],
                }
            ],
            "ResourceExposure": ["iam:CreatePolicyVersion"],
            "DataExfiltration": [],
            "ServiceWildcard": [],
            "CredentialsExposure": [],
            "InfrastructureModification": ["iam:CreatePolicyVersion"],
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

    def test_finding_actions_excluded(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        # "s3:GetObject",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        # (1) EXCLUDE actions
        exclusions_cfg = {
            "exclude-actions": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        }
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": [],
            "PrivilegeEscalation": [],
            "ResourceExposure": [],
            "DataExfiltration": [],
            "ServiceWildcard": [],
            "CredentialsExposure": [],
            "InfrastructureModification": [],
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

        # (2) When they are not excluded, make sure they show up in results
        exclusions_cfg = {}
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": [
                "logs"
            ],
            "PrivilegeEscalation": [],
            "ResourceExposure": [],
            "DataExfiltration": [],
            "ServiceWildcard": [],
            "CredentialsExposure": [],
            "InfrastructureModification": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)
