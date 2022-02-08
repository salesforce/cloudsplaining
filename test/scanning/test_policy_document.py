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
        self.assertCountEqual(actions_missing_resource_constraints, ['ssm:GetParameters', 'ecr:PutImage'])

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
        self.assertCountEqual(modify_actions_missing_resource_constraints, ['ecr:PutImage', 'ssm:GetParameters'])

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
        self.assertCountEqual(result, expected_result)

    def test_all_allowed_unrestriced_deny(self):
        """scan.policy_document.all_allowed_unrestricted_actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": "*",
                    "Resource": "*",
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        result = policy_document.all_allowed_unrestricted_actions
        self.assertEqual([],result)

    def test_policy_document_all_allowed_actions_deny(self):
        """scan.policy_document.all_allowed_actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                },
                {
                    "Effect": "Deny",
                    "Action": "aws-portal:*",
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        result = policy_document.all_allowed_actions
        self.assertTrue("aws-portal:ViewBilling" not in result)

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
        self.assertCountEqual(results, high_priority_read_only_actions)

        results = policy_document.permissions_management_without_constraints
        self.assertListEqual(results, ["iam:PassRole"])
        results = policy_document.write_actions_without_constraints
        self.assertListEqual(results, ["s3:PutObject"])
        results = policy_document.tagging_actions_without_constraints
        self.assertListEqual(results, ["ec2:CreateTags"])
        results = policy_document.allows_data_exfiltration_actions
        expected_results = high_priority_read_only_actions
        self.assertCountEqual(results, expected_results)
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

    def test_condition_is_a_restricted_action(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "cloudwatch:PutMetricData",
                "Resource": "*",
                "Condition": {"StringEquals": {"cloudwatch:namespace": "Namespace"}}
            }]
        }
        policy_document = PolicyDocument(test_policy)
        self.assertListEqual(policy_document.all_allowed_unrestrictable_actions, [])
        test_policy_without_condition = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "cloudwatch:PutMetricData",
                "Resource": "*",
            }]
        }
        policy_document_without_condition = PolicyDocument(test_policy_without_condition)
        self.assertListEqual(policy_document_without_condition.all_allowed_unrestrictable_actions, ["cloudwatch:PutMetricData"])

    def test_actions_without_constraints_deny(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": [
                        "iam:UpdateUser",
                        "iam:TagRole",
                        "iam:UntagRole",
                        "s3:PutBucketAcl",
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:CreateBucket"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        results = policy_document.permissions_management_without_constraints
        self.assertListEqual(results, [])

        results = policy_document.write_actions_without_constraints
        self.assertListEqual(results, [])

        results = policy_document.tagging_actions_without_constraints
        self.assertListEqual(results, [])

    def test_gh_190_allow_xray_wildcard_permissions(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "xray:PutTraceSegments",
                        "xray:PutTelemetryRecords"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        results = policy_document.write_actions_without_constraints
        self.assertListEqual(results, [])

    def test_gh_193_AmazonEC2ContainerRegistryReadOnly(self):
        # https://docs.aws.amazon.com/AmazonECR/latest/userguide/ecr_managed_policies.html#AmazonEC2ContainerRegistryReadOnly
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:GetAuthorizationToken",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:GetRepositoryPolicy",
                        "ecr:DescribeRepositories",
                        "ecr:ListImages",
                        "ecr:DescribeImages",
                        "ecr:BatchGetImage",
                        "ecr:GetLifecyclePolicy",
                        "ecr:GetLifecyclePolicyPreview",
                        "ecr:ListTagsForResource",
                        "ecr:DescribeImageScanFindings"
                    ],
                    "Resource": "*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy)
        self.assertTrue("ecr:GetAuthorizationToken" not in policy_document.all_allowed_unrestricted_actions)
        self.assertListEqual(policy_document.write_actions_without_constraints, [])
        self.assertListEqual(policy_document.credentials_exposure, ['ecr:GetAuthorizationToken'])

    def test_gh_254_flag_risky_actions_with_resource_constraints_privilege_escalation(self):
        # Privilege Escalation: https://cloudsplaining.readthedocs.io/en/latest/glossary/privilege-escalation/#updating-an-assumerole-policy
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:UpdateAssumeRolePolicy",
                        "sts:AssumeRole"
                    ],
                    "Resource": "arn:aws:iam::111122223333:role/MyRole"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=True)
        expected_result = [{
            'type': 'UpdateRolePolicyToAssumeIt',
            'actions': ['iam:updateassumerolepolicy', 'sts:assumerole']
        }]
        self.assertDictEqual(policy_document.allows_privilege_escalation[0], expected_result[0])
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=False)
        self.assertListEqual(policy_document.allows_privilege_escalation, [])

    def test_gh_254_flag_risky_actions_with_resource_constraints_resource_exposure(self):
        # Resource Exposure: https://cloudsplaining.readthedocs.io/en/latest/glossary/resource-exposure/
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutBucketAcl",
                    ],
                    "Resource": "arn:aws:s3:::mybucket"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=True)
        self.assertListEqual(policy_document.permissions_management_without_constraints, ["s3:PutBucketAcl"])
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=False)
        self.assertListEqual(policy_document.permissions_management_without_constraints, [])

    def test_gh_254_flag_risky_actions_with_resource_constraints_credentials_exposure(self):
        # Credentials Exposure: https://cloudsplaining.readthedocs.io/en/latest/glossary/credentials-exposure/
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:UpdateAccessKey",
                    ],
                    "Resource": "arn:aws:iam::111122223333:user/MyUser"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=True)
        self.assertListEqual(policy_document.credentials_exposure, ['iam:UpdateAccessKey'])
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=False)
        self.assertListEqual(policy_document.credentials_exposure, [])

    def test_gh_254_flag_risky_actions_with_resource_constraints_data_exfiltration(self):
        # Data Exfiltration: https://cloudsplaining.readthedocs.io/en/latest/glossary/data-exfiltration/
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                    ],
                    "Resource": "arn:aws:s3:::mybucket/*"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=True)
        self.assertListEqual(policy_document.allows_data_exfiltration_actions, ['s3:GetObject'])
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=False)
        self.assertListEqual(policy_document.allows_data_exfiltration_actions, [])

    def test_gh_254_flag_risky_actions_with_resource_constraints_infrastructure_modification(self):
        # Infrastructure Modification: https://cloudsplaining.readthedocs.io/en/latest/glossary/infrastructure-modification/
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                    ],
                    "Resource": "arn:aws:ec2:us-east-1:111122223333:security-group/sg-12345678"
                }
            ]
        }
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=True)
        self.assertListEqual(policy_document.infrastructure_modification, ['ec2:AuthorizeSecurityGroupIngress'])
        policy_document = PolicyDocument(test_policy, flag_resource_arn_statements=False)
        self.assertListEqual(policy_document.infrastructure_modification, [])
