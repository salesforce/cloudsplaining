import unittest
import json
from cloudsplaining.output.policy_finding import PolicyFinding
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.exclusions import Exclusions


class TestPolicyFinding(unittest.TestCase):
    def test_policy_finding_for_data_exfiltration(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": "*"}],
        }
        policy_document = PolicyDocument(test_policy)
        # (1) If the user is a member of an excluded group, return True

        exclusions_cfg = dict(users=["obama"], groups=["exclude-group"], roles=["MyRole"], policies=["exclude-policy"])
        exclusions = Exclusions(exclusions_cfg)
        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["s3"],
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
                "findings": [],
            },
            "InfrastructureModification": {"severity": "low", "description": "", "findings": []},
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

    def test_policy_finding_for_resource_exposure(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["s3:PutObjectAcl"], "Resource": "*"}],
        }
        policy_document = PolicyDocument(test_policy)

        exclusions_cfg = dict()
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["s3"],
            "PrivilegeEscalation": {
                "severity": "high",
                "description": '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>',
                "findings": [],
            },
            "ResourceExposure": {
                "severity": "high",
                "description": '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>',
                "findings": ["s3:PutObjectAcl"],
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
                "findings": [],
            },
            "InfrastructureModification": {"severity": "low", "description": "", "findings": ["s3:PutObjectAcl"]},
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

    def test_policy_finding_for_privilege_escalation(self):
        test_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["iam:CreatePolicyVersion"], "Resource": "*"}],
        }
        policy_document = PolicyDocument(test_policy)

        exclusions_cfg = dict()
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["iam"],
            "PrivilegeEscalation": {
                "severity": "high",
                "description": '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>',
                "findings": [
                    {
                        "type": "CreateNewPolicyVersion",
                        "actions": ["iam:createpolicyversion"],
                    }
                ],
            },
            "ResourceExposure": {
                "severity": "high",
                "description": '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>',
                "findings": ["iam:CreatePolicyVersion"],
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
                "findings": [],
            },
            "InfrastructureModification": {
                "severity": "low",
                "description": "",
                "findings": ["iam:CreatePolicyVersion"],
            },
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
                        "logs:PutLogEvents",
                    ],
                    "Resource": "*",
                }
            ],
        }
        policy_document = PolicyDocument(test_policy)
        # (1) EXCLUDE actions
        exclusions_cfg = {"exclude-actions": ["logs:CreateLogStream", "logs:PutLogEvents"]}
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": [],
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
                "findings": [],
            },
            "InfrastructureModification": {"severity": "low", "description": "", "findings": []},
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)

        # (2) When they are not excluded, make sure they show up in results
        exclusions_cfg = {}
        exclusions = Exclusions(exclusions_cfg)

        policy_finding = PolicyFinding(policy_document, exclusions)
        results = policy_finding.results
        expected_results = {
            "ServicesAffected": ["logs"],
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
                "findings": [],
            },
            "InfrastructureModification": {
                "severity": "low",
                "description": "",
                "findings": ["logs:CreateLogStream", "logs:PutLogEvents"],
            },
        }
        # print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_results)
