##### Understanding Context

It's essential to understand the context behind the findings that the report generates. Understanding the context behind the findings aids the assessor in triaging the results accurately.

This report generates findings on Policies that do not leverage resource constraints and identifies some attributes to help prioritize which ones to address - such as Privilege Escalation, Resource Exposure, and Data Exfiltration. These results help you to identify your IAM threat landscape and reduce blast radius. In the event of credential compromise, you can prevent an attacker from exploiting the risks mentioned above, in addition to preventing mass deletion, destruction, or modification of existing infrastructure.

However, this tool does not attempt to understand the context behind everything in your AWS account. It's possible to understand the context behind some of these things programmatically - whether the policy is applied to an instance profile, whether the policy is attached, whether inline IAM policies are in use, and whether or not AWS Managed Policies are in use. **Only you know the context behind the design of your AWS infrastructure and the IAM strategy**.


For example, an AWS Lambda policy used as a simple service checking the configuration of AWS infrastructure might be a good use case for resource constraints. Conversely, perhaps you applied the AdministratorAccess AWS-managed policy to an Instance Profile so that an EC2 instance can run Terraform to provision AWS resources via Infrastructure as Code. In the second example, the role is extremely permissive **by design** - and a tool can't automatically understand that context.


As such, the tool aims to:

* Map out your risk landscape of IAM identity-based policies, enumerating the potential risks for a full IAM threat model
* Identify where you can reduce the blast radius in the case of credentials compromise
* Help you prioritize which ones to remediate
* Provide a straightforward workflow to remediate
* Provide a sufficient exclusions mechanism to programmatically define where deviations from resource constraints are by design

##### Assessment Recap

To recap: you've followed these steps to generate this report:

* Downloaded the Account Authorization details JSON file</li>
  * `cloudsplaining download --profile default --output default-account-details.json`
* Generated your custom exclusions file</li>
  * `cloudsplaining create-exclusions-file --output-file exclusions.yml`
* Generated the report
  `cloudsplaining scan --input-file default-account-details.json --exclusions-file exclusions.yml`
* This generates (1) The single-file HTML report and the raw JSON data file

##### Triaging workflow

An assessor can follow this general workflow:

*   Open a ticket in your organization's project management tool of choice (for example, JIRA or Salesforce) in the AWS account owner's project
*   Attach the HTML report, JSON Data file, and CSV worksheet
*   Ask the service/account owner team to fill out the Triage worksheet

When you ask the service/account owner team to fill out the Triage CSV worksheet, you can use some text like the following:

> As part of our security assessment, our team ran Cloudsplaining on your AWS account. Cloudsplaining maps out the IAM risk landscape in a report, identifies where resource ARN constraints are not in use, and identifies other risks in IAM policies like Privilege Escalation, Data Exfiltration, and Resource Exposure/Permissions management. Remediating these issues, where applicable, will help to limit the blast radius in the case of compromised AWS credentials.
> We request that you review the HTML report and fill out the "Justification" field in the Triage worksheet. Based on the corresponding details in the HTML report, provide either (1) A justification on why the result is a False Positive, or (2) Identify that it is a legitimate finding.

##### Triaging considerations

When triaging your results, consider some of the factors listed below as you identify False Positives vs. legitimate findings. **There are some scenarios where `"Resource": "*"` access is by design and is therefore a false positive. This section covers some of the common scenarios.**

**Infrastructure Creation roles**:

 IAM roles that create infrastructure via Infrastructure as Code Technologies (for example, Terraform or CloudFormation) require high permission levels to provision AWS infrastructure. These will usually be false positives. When you see these instances, make sure that these roles are adequately protected. For instance, make sure that roles within the AWS account are not able to assume this role or affect its configuration in any way. Additionally, consider restricting the trust policy so that a set of explicitly stated IAM principals are the only ones who can assume that role. Take special care to audit instances of `sts:AssumeRole` within this AWS account.

**System roles vs. User Roles**: System roles - IAM Roles applied to compute services, such as EC2 Instance Profiles, ECS Task Execution roles, or Lambda Task Execution roles - should almost always leverage resource ARN constraints for actions that perform "Write" actions. Exceptions to this could include Infrastructure provisioning or other edge cases.

Conversely, user roles will almost always be used against `*` resources for the sake of convenience, innovation, and avoiding overly restrictive limitations. In the user role scenario, consider:

*   **Design context**: is it appropriate? (For instance, maybe all your user roles don't need `iam:*`)
*   **Environment**: If this is a Dev environment, frequently-used user roles probably allow more permissions for innovation purposes. However, in later environments - especially production - commonly used user roles should be read-only - or the more permissive ones should be for break-glass scenarios only.
*   **Regardless of the context**: there should **always** be security guardrails in place, like [Service Control Policies through AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scp.html) or [IAM Permissions Boundaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html) to prevent against egregious mistakes.

**Organization-specific results**

For example, perhaps you allow kms:Decrypt for * resources (by design) in your organization for one reason or another. Cloudsplaining flags this as a result. However, there are mitigating controls in place. Firstly, you leverage strict resource-based KMS key policies to lock down all KMS keys, explicitly stating individual IAM principals that are allowed to use them. Secondly, you provision all KMS keys with CloudFormation or Terraform, so you are confident that this pattern is consistent across all KMS keys in your AWS accounts. Therefore, `kms:Decrypt` to `*` resources is not a finding you are concerned about. In this case, you decide it is acceptable to exclude `kms:Decrypt` from your results.

##### Common False Positive Scenarios

**Conditions Logic**:

This tool does not evaluate [IAM Conditions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition.html) logic. If your policies use wildcard resources but restrict according to condition keys, then it's possible this is a false positive. However, you might want to double-check the accuracy of the conditions logic in those IAM policies. While IAM conditions can be extremely powerful, implementation is also prone to human error. We suggest leveraging [Parliament by Duo Labs](https://github.com/duo-labs/parliament/) (courtesy of [Scott Piper](https://twitter.com/0xdabbad00)), to lint your policies for accuracy - especially when IAM conditions are in use.

**`logs:CreateLogGroup` and `logs:PutLogEvent`**:

Depending on how your organization approaches CloudWatch Logs Agent configuration, IAM, and CloudWatch Logs Group naming conventions, it is sometimes near-impossible to prevent cross-contamination of logs or Log Injection to the Log Streams from other instance IDs. Cross-Contamination of CloudWatch Logs is an issue of its own that is definitely beyond the scope of this document - but consider this as a potential limitation by AWS when trying to identify a remediation plan.

##### Building the Exclusions File

After you have identified the False Positives, add the False Positive criteria to your custom Cloudsplaining exclusions file. The False Positives generally fall into one of two categories:

*   False positives that will occur across all of your AWS accounts, due to your organization-wide implementation strategy
*   False positives specific to this AWS account


To make the exclusions file, create a YAML file that we will use to list out exclusions with the `create-exclusions-file` command.

```bash
cloudsplaining create-exclusions-file
```

This will generate a file titled `exclusions.yml` in your current directory.

 The default exclusions file contains these contents:

```yaml
# Policy names to exclude from evaluation
# Suggestion: Add policies here that are known to be overly permissive by design, after you run the initial report.
policies:
  - "AWSServiceRoleFor*"
  - "*ServiceRolePolicy"
  - "*ServiceLinkedRolePolicy"
  - "AdministratorAccess" # Otherwise, this will take a long time
  - "service-role*"
  - "aws-service-role*"
# Don't evaluate these roles, users, or groups as part of the evaluation
roles:
  - "service-role*"
  - "aws-service-role*"
users:
  - ""
groups:
  - ""
# Read-only actions to include in the results, such as s3:GetObject
# By default, it includes Actions that could lead to Data Exfiltration
include-actions:
  - "s3:GetObject"
  - "ssm:GetParameter"
  - "ssm:GetParameters"
  - "ssm:GetParametersByPath"
  - "secretsmanager:GetSecretValue"
# Write actions to include from the results, such as kms:Decrypt
exclude-actions:
  - ""
```

Add whatever values you want to the above depending on your organization's context.
  * Under `policies`, list the path of policy names that you want to exclude.
  * If you want to exclude a role titled `MyRole`, list `MyRole` or `MyR*` in the `roles` list.
  * You can follow the same approach for `users` and `groups` list.


* Now, run the scan to generate a *new* Cloudsplaining report  that considers your exclusions criteria. This way, you are working with a report version that consists of True Positives only.

```bash
cloudsplaining scan --input-file default.json --exclusions-file exclusions.yml
```

You can now proceed to the Remediation stage.
