
<div id="definition-impact"><h6>Impact</h6></div>

The impact the risk would have on an organization if such a vulnerability were successfully exploited is rated according to criteria listed below. Note that these ratings are based on NIST 800-30 impact definitions.

* **Critical**: The issue causes multiple severe or catastrophic effects on operations, assets or other organizations.
* **High**: Causes produces severe degradation in mission capability to the point that the organization is not able to perform primary functions or results in damage to organizational assets.
* **Medium**: Trigger degradation in mission capability to an extent the application is able to perform its primary functions, but their effectiveness is reduced and there may be damage to the organization's assets.
* **Low**: Results in limited degradation in mission capability; the organization is able to perform its primary functions, but their effectiveness is noticeably reduced and may result in minor damage to the organization's assets.


<div id="definition-privilege-escalation"><h6>Privilege Escalation</h6></div>

These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by [Spencer Gietzen](https://twitter.com/SpenGietz) at Rhino Security Labs. Remediation Guidance can be found [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/).


<div id="definition-resource-exposure"><h6>Resource Exposure</h6></div>

Resource Exposure actions allow modification of Permissions to [resource-based policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html) or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify [AWS Resource Access Manager](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html).


<div id="definition-infrastructure-modification"><h6>Infrastructure Modification</h6></div>

Infrastructure Modification describes IAM actions with "modify" capabilities, and can therefore lead to [Resource Hijacking](https://attack.mitre.org/techniques/T1496/), unauthorized creation of Infrastructure, Backdoor creation, and/or modification of existing resources which can result in downtime.

<div id="definition-data-exfiltration"><h6>Data Exfiltration</h6></div>

Policies with Data leak potential allow certain read-only IAM actions without resource constraints, such as `s3:GetObject`, `ssm:GetParameter*`, or `secretsmanager:GetSecretValue`. Unrestricted `s3:GetObject` permissions has a long history of customer data leaks. `ssm:GetParameter*` and `secretsmanager:GetSecretValue` are both used to access secrets. `rds:CopyDBSnapshot` and `rds:CreateDBSnapshot` can be used to exfiltrate RDS database contents.

<div id="definition-roles-assumable-by-compute-services"><h6>Roles Assumable by Compute Services</h6></div>

IAM Roles can be assumed by AWS Compute Services (such as EC2, ECS, EKS, or Lambda) can present greater risk than user-defined roles, especially if the AWS Compute service is on an instance that is directly or indirectly exposed to the internet. Flagging these roles is particularly useful to penetration testers (or attackers) under certain scenarios. For example, if an attacker obtains privileges to execute [ssm:SendCommand](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_SendCommand.html) and there are privileged EC2 instances with the SSM agent installed, they can effectively have the privileges of those EC2 instances. Remote Code Execution via AWS Systems Manager Agent was already a known escalation/exploitation path, but Cloudsplaining can make the process of identifying theses cases easier.

<div id="definition-trust-policy"><h6>Trust Policy</h6></div>

A JSON policy document in which you define the principals that you trust to assume the role. A role trust policy is a required resource-based policy that is attached to a role in IAM. The principals that you can specify in the trust policy include users, roles, accounts, and services.

This definition was taken from the AWS Documentation [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html#term_trust-policy).


<div id="definition-principal"><h6>Principal</h6></div>

An entity in AWS that can perform actions and access resources. A principal can be an AWS account root user, an IAM user, or a role.

<div id="definition-role"><h6>Role</h6></div>

An IAM identity that you can create in your account that has specific permissions. An IAM role has some similarities to an IAM user. Roles and users are both AWS identities with permissions policies that determine what the identity can and cannot do in AWS. However, instead of being uniquely associated with one person, a role is intended to be assumable by anyone who needs it. Also, a role does not have standard long-term credentials such as a password or access keys associated with it. Instead, when you assume a role, it provides you with temporary security credentials for your role session.

We are particularly interested in roles used for **compute services** - i.e., Compute Service Roles.

This definition was taken from the AWS Documentation [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html#iam-term-role).

<div id="definition-managed-policy"><h6>Managed Policy</h6></div>

There are two types of Managed Policies: AWS-managed policies and Customer-managed policies. They are described below.

Criteria for selecting Managed Policies versus Inline policies can be found in the AWS documentation [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#choosing-managed-or-inline).

<div id="definition-customer-managed-policy"><h6>Customer-managed policy</h6></div>

AWS documentation on Customer-managed policies can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#customer-managed-policies).

The following diagram illustrates customer managed policies. Each policy is an entity in IAM with its own Amazon Resource Name (ARN) that includes the policy name. Notice that the same policy can be attached to multiple principal entities—for example, the same DynamoDB-books-app policy is attached to two different IAM roles.

![Customer-managed policy diagram](https://docs.aws.amazon.com/IAM/latest/UserGuide/images/policies-customer-managed-policies.diagram.png)

<div id="definition-aws-managed-policy"><h6>AWS-managed policy</h6></div>

An AWS managed policy is a standalone policy that is created and administered by AWS. Standalone policy means that the policy has its own Amazon Resource Name (ARN) that includes the policy name. For example, arn:aws:iam::aws:policy/IAMReadOnlyAccess is an AWS managed policy.

AWS documentation on AWS-managed policies can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#aws-managed-policies).

The following diagram (taken from the AWS documentation) illustrates AWS managed policies. The diagram shows three AWS managed policies: AdministratorAccess, PowerUserAccess, and AWSCloudTrailReadOnlyAccess. Notice that a single AWS managed policy can be attached to principal entities in different AWS accounts, and to different principal entities in a single AWS account.

![AWS-managed policy diagram](https://docs.aws.amazon.com/IAM/latest/UserGuide/images/policies-aws-managed-policies.diagram.png)

<div id="definition-inline-policy"><h6>Inline Policy</h6></div>

An inline policy is a policy that's embedded in an IAM identity (a user, group, or role). That is, the policy is an inherent part of the identity. You can create a policy and embed it in a identity, either when you create the identity or later.

AWS documentation on inline policies can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#inline-policies).

The following diagram illustrates inline policies. Each policy is an inherent part of the user, group, or role. Notice that two roles include the same policy (the DynamoDB-books-app policy), but they are not sharing a single policy; each role has its own copy of the policy.

![Inline policy diagram](https://docs.aws.amazon.com/IAM/latest/UserGuide/images/policies-inline-policies.diagram.png)

Inline policies are useful if you want to maintain a strict one-to-one relationship between a policy and the identity that it's applied to. For example, you want to be sure that the permissions in a policy are not inadvertently assigned to an identity other than the one they're intended for. When you use an inline policy, the permissions in the policy cannot be inadvertently attached to the wrong identity. In addition, when you use the AWS Management Console to delete that identity, the policies embedded in the identity are deleted as well. That's because they are part of the principal entity.
