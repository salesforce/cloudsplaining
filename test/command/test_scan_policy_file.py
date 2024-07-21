import unittest
import os
import json
from cloudsplaining.command.scan_policy_file import scan_policy
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions


class PolicyFileTestCase(unittest.TestCase):
    def test_policy_file(self):
        example_policy = {
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
                        "ecr:InitiateLayerUpload",
                        "ecr:UploadLayerPart",
                        "ecr:CompleteLayerUpload",
                        "ecr:PutImage",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "AllowManageOwnAccessKeys",
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateAccessKey",
                        "iam:DeleteAccessKey",
                        "iam:ListAccessKeys",
                        "iam:UpdateAccessKey",
                    ],
                    "Resource": "arn:aws:iam::*:user/${aws:username}",
                },
            ],
        }
        expected_results = {
            "ServicesAffected": ["ecr"],
            "PrivilegeEscalation": {
                "severity": "high",
                "description": '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>',
                "findings": [],
            },
            "ResourceExposure": {
                "severity": "high",
                "description": '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>',
                "findings": [],
            },
            "DataExfiltration": {
                "severity": "medium",
                "description": '<div style="text-align:left"><p>Policies with Data Exfiltration potential allow certain read-only IAM actions without resource constraints, such as <code>s3:GetObject</code>, <code>ssm:GetParameter*</code>, or <code>secretsmanager:GetSecretValue</code>. <br> <ul> <li>Unrestricted <code>s3:GetObject</code> permissions has a long history of customer data leaks.</li> <li><code>ssm:GetParameter*</code> and <code>secretsmanager:GetSecretValue</code> are both used to access secrets.</li> <li><code>rds:CopyDBSnapshot</code> and <code>rds:CreateDBSnapshot</code> can be used to exfiltrate RDS database contents.</li> </ul></p></div>',
                "findings": [],
            },
            "ServiceWildcard": {
                "severity": "medium",
                "description": '<p>"Service Wildcard" is the unofficial way of referring to IAM policy statements that grant access to ALL actions under a service - like s3:*. Prioritizing the remediation of policies with this characteristic can help to efficiently reduce the total count of issues in the Cloudsplaining report.</p>',
                "findings": [],
            },
            "CredentialsExposure": {
                "severity": "high",
                "description": "<p>Credentials Exposure actions return credentials as part of the API response , such as ecr:GetAuthorizationToken, iam:UpdateAccessKey, and others. The full list is maintained here: https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a</p>",
                "findings": ["ecr:GetAuthorizationToken"],
            },
            "InfrastructureModification": {
                "severity": "low",
                "description": "",
                "findings": [
                    "ecr:CompleteLayerUpload",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart",
                ],
            },
        }
        results = scan_policy(example_policy)
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results)

    def test_excluded_actions_scan_policy_file(self):
        """Test the scan_policy command when we have excluded actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["s3:GetObject", "iam:CreateAccessKey"], "Resource": "*"},
            ],
        }
        results = scan_policy(test_policy)
        expected_results = {
            "ServicesAffected": ["iam", "s3"],
            "PrivilegeEscalation": {
                "severity": "high",
                "description": '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>',
                "findings": [{"type": "CreateAccessKey", "actions": ["iam:createaccesskey"]}],
            },
            "ResourceExposure": {
                "severity": "high",
                "description": '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>',
                "findings": ["iam:CreateAccessKey"],
            },
            "DataExfiltration": {
                "severity": "medium",
                "description": '<div style="text-align:left"><p>Policies with Data Exfiltration potential allow certain read-only IAM actions without resource constraints, such as <code>s3:GetObject</code>, <code>ssm:GetParameter*</code>, or <code>secretsmanager:GetSecretValue</code>. <br> <ul> <li>Unrestricted <code>s3:GetObject</code> permissions has a long history of customer data leaks.</li> <li><code>ssm:GetParameter*</code> and <code>secretsmanager:GetSecretValue</code> are both used to access secrets.</li> <li><code>rds:CopyDBSnapshot</code> and <code>rds:CreateDBSnapshot</code> can be used to exfiltrate RDS database contents.</li> </ul></p></div>',
                "findings": ["s3:GetObject"],
            },
            "ServiceWildcard": {
                "severity": "medium",
                "description": '<p>"Service Wildcard" is the unofficial way of referring to IAM policy statements that grant access to ALL actions under a service - like s3:*. Prioritizing the remediation of policies with this characteristic can help to efficiently reduce the total count of issues in the Cloudsplaining report.</p>',
                "findings": [],
            },
            "CredentialsExposure": {
                "severity": "high",
                "description": "<p>Credentials Exposure actions return credentials as part of the API response , such as ecr:GetAuthorizationToken, iam:UpdateAccessKey, and others. The full list is maintained here: https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a</p>",
                "findings": ["iam:CreateAccessKey"],
            },
            "InfrastructureModification": {
                "severity": "low",
                "description": "",
                "findings": ["iam:CreateAccessKey", "s3:GetObject"],
            },
        }
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results)

    def test_excluded_actions_scan_policy_file_v2(self):
        """test_excluded_actions_scan_policy_file_v2: Test the scan_policy command when we have excluded actions"""
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["s3:GetObject", "iam:CreateAccessKey"], "Resource": "*"},
            ],
        }
        expected_results = {
            "ServiceWildcard": {
                "severity": "medium",
                "description": '<p>"Service Wildcard" is the unofficial way of referring to IAM policy statements that grant access to ALL actions under a service - like s3:*. Prioritizing the remediation of policies with this characteristic can help to efficiently reduce the total count of issues in the Cloudsplaining report.</p>',
                "findings": [],
            },
            "ServicesAffected": ["iam", "s3"],
            "PrivilegeEscalation": {
                "severity": "high",
                "description": '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>',
                "findings": [{"type": "CreateAccessKey", "actions": ["iam:createaccesskey"]}],
            },
            "ResourceExposure": {
                "severity": "high",
                "description": '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>',
                "findings": ["iam:CreateAccessKey"],
            },
            "DataExfiltration": {
                "severity": "medium",
                "description": '<div style="text-align:left"><p>Policies with Data Exfiltration potential allow certain read-only IAM actions without resource constraints, such as <code>s3:GetObject</code>, <code>ssm:GetParameter*</code>, or <code>secretsmanager:GetSecretValue</code>. <br> <ul> <li>Unrestricted <code>s3:GetObject</code> permissions has a long history of customer data leaks.</li> <li><code>ssm:GetParameter*</code> and <code>secretsmanager:GetSecretValue</code> are both used to access secrets.</li> <li><code>rds:CopyDBSnapshot</code> and <code>rds:CreateDBSnapshot</code> can be used to exfiltrate RDS database contents.</li> </ul></p></div>',
                "findings": ["s3:GetObject"],
            },
            "CredentialsExposure": {
                "severity": "high",
                "description": "<p>Credentials Exposure actions return credentials as part of the API response , such as ecr:GetAuthorizationToken, iam:UpdateAccessKey, and others. The full list is maintained here: https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a</p>",
                "findings": ["iam:CreateAccessKey"],
            },
            "InfrastructureModification": {"severity": "low", "description": "", "findings": ["iam:CreateAccessKey"]},
        }
        exclusions_cfg_custom = {}
        results = scan_policy(test_policy, exclusions_cfg_custom)
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(results, expected_results)

    def test_gh_109_full_access_policy(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "*", "Resource": "*"},
            ],
        }
        exclusions_cfg_custom = {}
        results = scan_policy(test_policy, exclusions_cfg_custom)
        self.assertTrue(len(results.get("ServiceWildcard")["findings"]) > 150)
        self.assertTrue(len(results.get("ServicesAffected")) > 150)

        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["*"], "Resource": ["*"]},
            ],
        }
        results = scan_policy(test_policy, exclusions_cfg_custom)
        # print(json.dumps(results, indent=4))
        self.assertTrue(len(results.get("ServiceWildcard")["findings"]) > 150)
        self.assertTrue(len(results.get("ServicesAffected")) > 150)

    def test_checkov_gh_990_condition_restricted_action(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "RestrictedWithConditions",
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "*",
                    "Condition": {
                        "IpAddress": {"aws:SourceIp": "192.0.2.0/24"},
                        "NotIpAddress": {"aws:SourceIp": "192.0.2.188/32"},
                    },
                }
            ],
        }
        exclusions_cfg_custom = {}
        results = scan_policy(test_policy, exclusions_cfg_custom)
        print(json.dumps(results, indent=4))
        self.assertListEqual(results.get("InfrastructureModification")["findings"], [])
        self.assertListEqual(results.get("DataExfiltration")["findings"], [])
        self.assertListEqual(results.get("ServicesAffected"), [])

        test_policy_without_condition = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Unrestricted",
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "*",
                }
            ],
        }
        results = scan_policy(test_policy_without_condition, exclusions_cfg_custom)
        print(json.dumps(results, indent=4))
        self.assertListEqual(results.get("InfrastructureModification")["findings"], [])
        self.assertListEqual(results.get("DataExfiltration")["findings"], ["s3:GetObject"])
        self.assertListEqual(results.get("ServicesAffected"), ["s3"])

    def test_gh_254_all_risky_actions_scan_policy(self):
        policy_with_resource_constraints = {
            "Version": "2012-10-17",
            "Statement": [
                # Privilege Escalation
                {
                    "Effect": "Allow",
                    "Action": ["iam:UpdateAssumeRolePolicy", "sts:AssumeRole"],
                    "Resource": "arn:aws:iam::111122223333:role/MyRole",
                },
                # Data Exfiltration
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                    ],
                    "Resource": "arn:aws:s3:::mybucket/*",
                },
                # Resource Expsoure
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutBucketAcl",
                    ],
                    "Resource": "arn:aws:s3:::mybucket",
                },
                # Credentials Exposure
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:UpdateAccessKey",
                    ],
                    "Resource": "arn:aws:iam::111122223333:user/MyUser",
                },
                # Infrastructure Modification
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                    ],
                    "Resource": "arn:aws:ec2:us-east-1:111122223333:security-group/sg-12345678",
                },
            ],
        }
        results = scan_policy(
            policy_with_resource_constraints, flag_resource_arn_statements=True, flag_conditional_statements=True
        )
        expected_results = {
            "ServiceWildcard": {
                "severity": "medium",
                "description": '<p>"Service Wildcard" is the unofficial way of referring to IAM policy statements that grant access to ALL actions under a service - like s3:*. Prioritizing the remediation of policies with this characteristic can help to efficiently reduce the total count of issues in the Cloudsplaining report.</p>',
                "findings": [],
            },
            "ServicesAffected": ["ec2", "iam", "s3", "sts"],
            "PrivilegeEscalation": {
                "severity": "high",
                "description": '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>',
                "findings": [
                    {"type": "UpdateRolePolicyToAssumeIt", "actions": ["iam:updateassumerolepolicy", "sts:assumerole"]}
                ],
            },
            "ResourceExposure": {
                "severity": "high",
                "description": '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>',
                "findings": ["iam:UpdateAssumeRolePolicy", "s3:PutBucketAcl", "iam:UpdateAccessKey"],
            },
            "DataExfiltration": {
                "severity": "medium",
                "description": '<div style="text-align:left"><p>Policies with Data Exfiltration potential allow certain read-only IAM actions without resource constraints, such as <code>s3:GetObject</code>, <code>ssm:GetParameter*</code>, or <code>secretsmanager:GetSecretValue</code>. <br> <ul> <li>Unrestricted <code>s3:GetObject</code> permissions has a long history of customer data leaks.</li> <li><code>ssm:GetParameter*</code> and <code>secretsmanager:GetSecretValue</code> are both used to access secrets.</li> <li><code>rds:CopyDBSnapshot</code> and <code>rds:CreateDBSnapshot</code> can be used to exfiltrate RDS database contents.</li> </ul></p></div>',
                "findings": ["s3:GetObject"],
            },
            "CredentialsExposure": {
                "severity": "high",
                "description": "<p>Credentials Exposure actions return credentials as part of the API response , such as ecr:GetAuthorizationToken, iam:UpdateAccessKey, and others. The full list is maintained here: https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a</p>",
                "findings": ["iam:UpdateAccessKey", "sts:AssumeRole"],
            },
            "InfrastructureModification": {
                "severity": "low",
                "description": "",
                "findings": [
                    "ec2:AuthorizeSecurityGroupIngress",
                    "iam:UpdateAccessKey",
                    "iam:UpdateAssumeRolePolicy",
                    "s3:GetObject",
                    "s3:PutBucketAcl",
                    "sts:AssumeRole",
                ],
            },
        }

        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)
