import unittest
import json
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.exclusions import is_name_excluded, Exclusions


class TestPolicyDocument(unittest.TestCase):
    def test_policy_document_return_json(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:PutImage"
                    ],
                    "Resource": "*"
                },
              {
                    "Sid": "AllowManageOwnAccessKeys",
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateAccessKey"
                    ],
                    "Resource": "arn:aws:iam::*:user/${aws:username}"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        result = policy_document.json
        # That function returns the Policy as JSON
        self.assertEqual(result, test_policy)

    def test_policy_document_return_statement_results(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ssm:GetParameters",
                        "ecr:PutImage"
                    ],
                    "Resource": "*"
                },
              {
                    "Sid": "AllowManageOwnAccessKeys",
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateAccessKey"
                    ],
                    "Resource": "arn:aws:iam::*:user/${aws:username}"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        actions_missing_resource_constraints = []
        # Read only
        for statement in policy_document.statements:
            actions_missing_resource_constraints.extend(
                statement.missing_resource_constraints())
        self.assertEqual(actions_missing_resource_constraints, ['ssm:GetParameters', 'ecr:PutImage'])

        # Modify only
        # modify_actions_missing_resource_constraints = []
        # for statement in policy_document.statements:
        #     modify_actions_missing_resource_constraints.extend(
        #         statement.missing_resource_constraints_for_modify_actions())
        # self.assertEqual(modify_actions_missing_resource_constraints, ['ecr:PutImage'])

        # Modify only but with include-action of ssm:GetParameters
        modify_actions_missing_resource_constraints = []
        for statement in policy_document.statements:
            modify_actions_missing_resource_constraints.extend(
                statement.missing_resource_constraints_for_modify_actions())
        self.assertEqual(modify_actions_missing_resource_constraints, ['ecr:PutImage', 'ssm:GetParameters'])

    def test_policy_document_all_allowed_actions(self):
        """scan.policy_document.all_allowed_actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ssm:GetParameters",
                        "ecr:PutImage"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "AllowManageOwnAccessKeys",
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateAccessKey"
                    ],
                    "Resource": "arn:aws:iam::*:user/${aws:username}"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        result = policy_document.all_allowed_actions

        expected_result = [
            "ecr:PutImage",
            "ssm:GetParameters",
            "iam:CreateAccessKey"
        ]
        self.assertListEqual(result, expected_result)

    def test_allows_privilege_escalation(self):
        """scan.policy_document.allows_privilege_escalation"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:PassRole",
                        "lambda:CreateFunction",
                        "lambda:CreateEventSourceMapping",
                        "dynamodb:CreateTable",
                        "dynamodb:PutItem",
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        results = policy_document.allows_privilege_escalation
        expected_result = [
            {
                "type": "PassExistingRoleToNewLambdaThenTriggerWithNewDynamo",
                "actions": [
                    "iam:passrole",
                    "lambda:createfunction",
                    "lambda:createeventsourcemapping",
                    "dynamodb:createtable",
                    "dynamodb:putitem"
                ]
            },
            {
                "type": "PassExistingRoleToNewLambdaThenTriggerWithExistingDynamo",
                "actions": [
                    "iam:passrole",
                    "lambda:createfunction",
                    "lambda:createeventsourcemapping"
                ]
            }
        ]
        self.assertListEqual(results, expected_result)

    def test_allows_specific_actions(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:PassRole",
                        "ssm:GetParameter",
                        "s3:GetObject",
                        "ssm:GetParameter",
                        "ssm:GetParameters",
                        "ssm:GetParametersByPath",
                        "secretsmanager:GetSecretValue",
                        "s3:PutObject",
                        "ec2:CreateTags"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        results = policy_document.allows_specific_actions_without_constraints(["iam:PassRole"])
        self.assertListEqual(results, ["iam:PassRole"])
        # Input should be case insensitive, but give the pretty CamelCase action name result
        results = policy_document.allows_specific_actions_without_constraints(["iam:passrole"])
        self.assertListEqual(results, ["iam:PassRole"])

        # Verify that it will find the high priority read-only actions that we care about
        high_priority_read_only_actions = [
            "s3:GetObject",
            "ssm:GetParameter",
            "ssm:GetParameters",
            "ssm:GetParametersByPath",
            "secretsmanager:GetSecretValue"
        ]
        results = policy_document.allows_specific_actions_without_constraints(high_priority_read_only_actions)
        self.assertListEqual(results, high_priority_read_only_actions)

        results = policy_document.permissions_management_without_constraints
        self.assertListEqual(results, ["iam:PassRole"])
        results = policy_document.write_actions_without_constraints
        self.assertListEqual(results, ["s3:PutObject"])
        results = policy_document.tagging_actions_without_constraints
        self.assertListEqual(results, ["ec2:CreateTags"])
        results = policy_document.allows_data_exfiltration_actions
        expected_results = high_priority_read_only_actions
        self.assertListEqual(results, expected_results)
        with self.assertRaises(Exception):
            results = policy_document.allows_specific_actions_without_constraints("iam:passrole")


    def test_policy_document_not_action_deny_gh_23(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "DenyAllUsersNotUsingMFA",
                "Effect": "Deny",
                "NotAction": "iam:*",
                "Resource": "*",
                "Condition": {"BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}}
            }]
        }
        policy_document = PolicyDocument(test_policy)
        allowed_actions = []
        for statement in policy_document.statements:
            if not statement.has_resource_constraints:
                if statement.expanded_actions:
                    allowed_actions.extend(statement.expanded_actions)  # pragma: no cover
        self.assertListEqual(allowed_actions, [])
        self.assertListEqual(policy_document.all_allowed_unrestricted_actions, [])
        # print(json.dumps(policy_document.contains_statement_using_not_action, indent=4))
        self.assertListEqual(policy_document.contains_statement_using_not_action, test_policy["Statement"])

    def test_policy_document_contains_statement_using_not_action(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Something",
                    "Effect": "Allow",
                    "NotAction": "iam:*",
                    "Resource": "*",
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)

        results = policy_document.contains_statement_using_not_action
        expected_results = [
            {
                "Sid": "Something",
                "Effect": "Allow",
                "NotAction": "iam:*",
                "Resource": "*"
            }
        ]
        # print(json.dumps(results, indent=4))
        self.assertListEqual(results, expected_results)

    def test_gh_106_excluded_actions_should_not_show_in_results(self):
        """test_gh_106_excluded_actions_should_not_show_in_results: Make sure that autoscaling:SetDesiredCapacity does not show in results when it is excluded"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Something",
                    "Effect": "Allow",
                    "Action": [
                        "autoscaling:SetDesiredCapacity",
                        "autoscaling:TerminateInstanceInAutoScalingGroup",
                        "autoscaling:UpdateAutoScalingGroup"
                    ],
                    "Resource": "*",
                }
            ]
        }
        exclusions_cfg = {
            "policies": [
                "aws-service-role*"
            ],
            "roles": ["aws-service-role*"],
            "users": [""],
            "include-actions": ["s3:GetObject"],
            "exclude-actions": [
                "autoscaling:SetDesiredCapacity",
                "autoscaling:TerminateInstanceInAutoScalingGroup",
                "autoscaling:UpdateAutoScalingGroup"
            ]
        }
        exclusions = Exclusions(exclusions_cfg)
        policy_document = PolicyDocument(test_policy, exclusions)
        print(policy_document.infrastructure_modification)
        self.assertEqual(policy_document.infrastructure_modification, [])

        exclusions_cfg_2 = {
            "policies": [
                "aws-service-role*"
            ],
            "roles": ["aws-service-role*"],
            "users": [""],
            "include-actions": ["s3:GetObject"],
            "exclude-actions": [
                "autoscaling:SetDesiredCapacity",
                "autoscaling:TerminateInstanceInAutoScalingGroup",
            ]
        }
        exclusions_2 = Exclusions(exclusions_cfg_2)
        policy_document_2 = PolicyDocument(test_policy, exclusions_2)
        # Should still include one result
        print(policy_document_2.infrastructure_modification)
        self.assertEqual(policy_document_2.infrastructure_modification, ["autoscaling:UpdateAutoScalingGroup"])
