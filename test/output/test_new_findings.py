import unittest
import json
from cloudsplaining.output.new_findings import (
    UserFinding,
    GroupFinding,
    RoleFinding,
    PolicyFinding,
    NewFinding,
    NewFindings
)
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.scan.assume_role_policy_document import AssumeRolePolicyDocument
from cloudsplaining.shared.exclusions import Exclusions


class TestNewFindings(unittest.TestCase):
    def test_new_findings(self):
        """output.new_findings.NewFindings"""
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
        # Let's just re-use the same policy for users groups and roles
        user_finding = UserFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:user/SomeUser",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            group_membership=["admin"],
            exclusions=exclusions
        )
        group_finding = GroupFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/SomeGroup",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            members=["obama"],
            exclusions=exclusions
        )
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
        role_finding = RoleFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:role/SomeRole",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            assume_role_policy_document=assume_role_policy_document,
            exclusions=exclusions
        )
        policy_finding = PolicyFinding(
            policy_name="AWSLambdaFullAccess",
            arn="arn:aws:iam::aws:policy/AWSLambdaFullAccess",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            exclusions=exclusions
        )
        all_findings = NewFindings(exclusions)
        all_findings.add_user_finding(user_finding)
        result = all_findings.users[0]
        expected_user_result = {
            "AccountID": "123456789012",
            "ManagedBy": "Customer",
            "Name": "SomeUser",
            "PolicyName": "MyPolicy",
            "Type": "User",
            "Arn": "arn:aws:iam::123456789012:user/SomeUser",
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
            "AssumeRolePolicyDocument": None,
            "AssumableByComputeService": [],
            "PrivilegeEscalation": [],
            "DataExfiltrationActions": [
                "s3:GetObject"
            ],
            "PermissionsManagementActions": []
        }
        self.assertDictEqual(result.json, expected_user_result)

        all_findings.add_group_finding(group_finding)
        all_findings.add_role_finding(role_finding)
        all_findings.add_policy_finding(policy_finding)
        print(len(all_findings))
        self.assertEqual(len(all_findings), 4)
        results = all_findings.json
        expected_results = [
            {
                "AccountID": "N/A",
                "ManagedBy": "AWS",
                "Name": "AWSLambdaFullAccess",
                "PolicyName": "AWSLambdaFullAccess",
                "Type": "Policy",
                "Arn": "arn:aws:iam::aws:policy/AWSLambdaFullAccess",
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
                "AssumeRolePolicyDocument": None,
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [
                    "s3:GetObject"
                ],
                "PermissionsManagementActions": []
            },
            {
                "AccountID": "123456789012",
                "ManagedBy": "Customer",
                "Name": "SomeUser",
                "PolicyName": "MyPolicy",
                "Type": "User",
                "Arn": "arn:aws:iam::123456789012:user/SomeUser",
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
                "AssumeRolePolicyDocument": None,
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [
                    "s3:GetObject"
                ],
                "PermissionsManagementActions": []
            },
            {
                "AccountID": "123456789012",
                "ManagedBy": "Customer",
                "Name": "SomeGroup",
                "PolicyName": "MyPolicy",
                "Type": "Group",
                "Arn": "arn:aws:iam::123456789012:group/SomeGroup",
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
                "AssumeRolePolicyDocument": None,
                "AssumableByComputeService": [],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [
                    "s3:GetObject"
                ],
                "PermissionsManagementActions": []
            },
            {
                "AccountID": "123456789012",
                "ManagedBy": "Customer",
                "Name": "SomeRole",
                "PolicyName": "MyPolicy",
                "Type": "Role",
                "Arn": "arn:aws:iam::123456789012:role/SomeRole",
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
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "sts:AssumeRole"
                            ],
                            "Principal": {
                                "Service": "ecs-tasks.amazonaws.com",
                                "AWS": "arn:aws:iam::012345678910:root"
                            }
                        }
                    ]
                },
                "AssumableByComputeService": [
                    "ecs-tasks"
                ],
                "PrivilegeEscalation": [],
                "DataExfiltrationActions": [
                    "s3:GetObject"
                ],
                "PermissionsManagementActions": []
            }
        ]
        # print(json.dumps(all_findings.json, indent=4))
        self.assertListEqual(results, expected_results)


class TestNewFinding(unittest.TestCase):
    def test_principal_findings(self):
        """output.new_findings.UserFinding"""
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
            groups=["admin"],
            roles=["MyRole"],
            policies=["AWSLambdaFullAccess"]
        )
        exclusions = Exclusions(exclusions_cfg)
        user_finding = UserFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:user/SomeUser",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            group_membership=["admin"],
            exclusions=exclusions
        )
        result = user_finding.is_excluded(exclusions)
        expected_result = ["admin"]
        self.assertListEqual(result, expected_result)

        # (2) If the user is explicitly excluded, return True
        exclusions = Exclusions(exclusions_cfg)
        user_finding = UserFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:user/obama",  # Obama is excluded
            actions=["s3:GetObject"],
            policy_document=policy_document,
            group_membership=["not-excluded-group"],
            exclusions=exclusions
        )
        result = user_finding.is_excluded(exclusions)
        expected_result = ["obama"]
        self.assertListEqual(result, expected_result)

        # (3) If the policy attached is excluded
        user_finding = UserFinding(
            policy_name="AWSLambdaFullAccess",
            arn="arn:aws:iam::123456789012:user/not-excluded-user",  # Obama is excluded
            actions=["s3:GetObject"],
            policy_document=policy_document,
            group_membership=["not-excluded-group"],
            exclusions=exclusions
        )
        result = user_finding.is_excluded(exclusions)
        expected_result = ["AWSLambdaFullAccess"]
        self.assertListEqual(result, expected_result)

    def test_group_membership_finding(self):
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

        exclusions_cfg = dict(
            users=["obama"],
            groups=["admin"],
            roles=["MyRole"],
            policies=["AWSLambdaFullAccess"]
        )
        exclusions = Exclusions(exclusions_cfg)
        group_finding = GroupFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/GroupShouldBeEmpty",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            exclusions=exclusions,
            members=["obama"]
        )
        result = group_finding.is_excluded(exclusions)
        self.assertListEqual(result, [])
        group_finding = GroupFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/GroupShouldBeEmpty",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            exclusions=exclusions,
            members=["yolo"]
        )
        self.assertFalse(group_finding.is_excluded(exclusions))




    def test_policy_action_exclusion_findings(self):
        print()

    def test_policy_name_finding(self):
        """output.new_findings.PolicyFinding"""
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
        exclusions_cfg = dict(
            users=["obama"],
            groups=["admin"],
            roles=["MyRole"],
            policies=["AWSLambdaFullAccess"]
        )
        exclusions = Exclusions(exclusions_cfg)
        # (1) If the policy attached is excluded
        policy_finding = PolicyFinding(
            policy_name="AWSLambdaFullAccess",
            arn="arn:aws:iam::aws:policy/AWSLambdaFullAccess",  # Obama is excluded
            actions=["s3:GetObject"],
            policy_document=policy_document,
            exclusions=exclusions
        )
        result = policy_finding.is_excluded(exclusions)
        expected_result = ["AWSLambdaFullAccess"]
        self.assertListEqual(result, expected_result)

        # (2) Non-exclusion
        exclusions_cfg = dict(
            users=["obama"],
            groups=["admin"],
            roles=["MyRole"],
            policies=["someOtherName"]
        )
        exclusions = Exclusions(exclusions_cfg)
        result = policy_finding.is_excluded(exclusions)
        expected_result = False
        self.assertEqual(result, expected_result)

    def test_finding_attributes(self):
        """scan.findings.new_finding"""
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
        finding = NewFinding(
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
            "Name": "SNSNotifications",
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
        }
        # print(json.dumps(finding.json, indent=4))
        self.maxDiff = None
        self.assertDictEqual(finding.json, expected_finding_json)

    def test_finding_actions_excluded(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
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
            "users": ["obama"],
            "groups": ["admin"],
            "roles": ["MyRole"],
            "policies": ["someOtherName"],
            "exclude-actions": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        }
        exclusions = Exclusions(exclusions_cfg)
        finding = NewFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/SNSNotifications",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            exclusions=exclusions
        )
        # print(finding.actions)
        self.assertListEqual(finding.actions, ["s3:GetObject"])

    def test_finding_actions_included(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "ec2:DescribeInstances",  # This is a bad thing to include, but just for the hell of it
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        # (2) INCLUDE actions
        exclusions_cfg = {
            "users": ["obama"],
            "groups": ["admin"],
            "roles": ["MyRole"],
            "policies": ["someOtherName"],
            "include-actions": [
                "ec2:DescribeInstances"
            ],
            "exclude-actions": [
                "s3:GetObject",
            ],
        }
        exclusions = Exclusions(exclusions_cfg)
        finding = NewFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/SNSNotifications",
            actions=["s3:GetObject", "ec2:DescribeInstances"],
            policy_document=policy_document,
            exclusions=exclusions
        )
        # print(finding.actions)
        expected_results = [
            "ec2:DescribeInstances",
        ]
        self.assertListEqual(finding.actions, expected_results)
        group_finding = GroupFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:group/SNSNotifications",
            actions=["s3:GetObject", "ec2:DescribeInstances"],
            policy_document=policy_document,
            exclusions=exclusions
        )
        self.assertListEqual(group_finding.actions, expected_results)

    def test_findings_for_roles_assumable_by_compute_services_ecs_tasks_new(self):
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
        finding = NewFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:role/TestComputeService",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            assume_role_policy_document=assume_role_policy_document
        )
        # print(finding.role_assumable_by_compute_services)
        self.assertListEqual(finding.role_assumable_by_compute_services, ["ecs-tasks"])

        role_finding = RoleFinding(
            policy_name="MyPolicy",
            arn="arn:aws:iam::123456789012:role/TestComputeService",
            actions=["s3:GetObject"],
            policy_document=policy_document,
            assume_role_policy_document=assume_role_policy_document
        )
        self.assertListEqual(role_finding.role_assumable_by_compute_services, ["ecs-tasks"])
