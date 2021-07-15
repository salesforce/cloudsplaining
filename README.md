Cloudsplaining
--------------

Cloudsplaining is an AWS IAM Security Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report.

[![Tests](https://github.com/salesforce/cloudsplaining/workflows/Test/badge.svg)](https://github.com/salesforce/cloudsplaining/actions?query=workflow%3ATest)
[![Documentation Status](https://readthedocs.org/projects/cloudsplaining/badge/?version=latest)](https://cloudsplaining.readthedocs.io/en/latest/?badge=latest)
[![Join the chat at https://gitter.im/cloudsplaining](https://badges.gitter.im/cloudsplaining.svg)](https://gitter.im/cloudsplaining?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/kmcquade3.svg?style=social&label=Follow%20the%20author)](https://twitter.com/kmcquade3)
[![Downloads](https://pepy.tech/badge/cloudsplaining)](https://pepy.tech/project/cloudsplaining)

* [Example report](https://opensource.salesforce.com/cloudsplaining/)

> ![](https://github.com/salesforce/cloudsplaining/raw/master/docs/_images/cloudsplaining-report.gif)

## Documentation

For full documentation, please visit the [project on ReadTheDocs](https://cloudsplaining.readthedocs.io/en/latest/).

* [Installation](#installation)
* [Cheatsheet](#cheatsheet)
* [Example report](https://opensource.salesforce.com/cloudsplaining/)

## Overview

Cloudsplaining identifies violations of least privilege in AWS IAM policies and generates a pretty HTML report with a triage worksheet. It can scan all the policies in your AWS account or it can scan a single policy file.

It helps to identify IAM actions that do not leverage resource constraints. It also helps prioritize the remediation process by flagging IAM policies that present the following risks to the AWS account in question without restriction:
* Data Exfiltration (`s3:GetObject`, `ssm:GetParameter`, `secretsmanager:GetSecretValue`)
* Infrastructure Modification
* Resource Exposure (the ability to modify resource-based policies)
* Privilege Escalation (based on Rhino Security Labs research)

Cloudsplaining also identifies IAM Roles that can be assumed by AWS Compute Services (such as EC2, ECS, EKS, or Lambda), as they can present greater risk than user-defined roles - especially if the AWS Compute service is on an instance that is directly or indirectly exposed to the internet. Flagging these roles is particularly useful to penetration testers (or attackers) under certain scenarios. For example, if an attacker obtains privileges to execute [ssm:SendCommand](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_SendCommand.html) and there are privileged EC2 instances with the SSM agent installed, they can effectively have the privileges of those EC2 instances. Remote Code Execution via AWS Systems Manager Agent was already a known escalation/exploitation path, but Cloudsplaining can make the process of identifying theses cases easier. See the [sample report](https://opensource.salesforce.com/cloudsplaining/#executive-summary) for some examples.

You can also specify a custom exclusions file to filter out results that are False Positives for various reasons. For example, User Policies are permissive by design, whereas System roles are generally more restrictive. You might also have exclusions that are specific to your organization's multi-account strategy or AWS application architecture.


## Motivation

[Policy Sentry](https://engineering.salesforce.com/salesforce-cloud-security-automating-least-privilege-in-aws-iam-with-policy-sentry-b04fe457b8dc) revealed to us that it is possible to finally write IAM policies according to least privilege in a scalable manner. Before Policy Sentry was released, it was too easy to find IAM policy documents that lacked resource constraints. Consider the policy below, which allows the IAM principal (a role or user) to run `s3:PutObject` on any S3 bucket in the AWS account:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}
```

This is bad. Ideally, access should be restricted according to resource ARNs, like so:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

Policy Sentry [makes it really easy to do this](https://github.com/salesforce/policy_sentry/#policy-sentry). Once Infrastructure as Code developers or AWS Administrators gain familiarity with the tool (which is quite easy to use), we've found that adoption starts very quickly. **However**, if you've been using AWS, there is probably a very large backlog of IAM policies that could use an uplift. If you have hundreds of AWS accounts with dozens of policies in each, how can we lock down those AWS accounts by programmatically identifying the policies that should be fixed?

That's why we wrote Cloudsplaining.

Cloudsplaining identifies violations of least privilege in AWS IAM policies and generates a pretty HTML report with a triage worksheet. It can scan all the policies in your AWS account or it can scan a single policy file.

## Installation

#### Homebrew

```bash
brew tap salesforce/cloudsplaining https://github.com/salesforce/cloudsplaining
brew install cloudsplaining
```

#### Pip3

```bash
pip3 install --user cloudsplaining
```

* Now you should be able to execute `cloudsplaining` from command line by running `cloudsplaining --help`.

#### Shell completion

To enable Bash completion, put this in your `.bashrc`:

```bash
eval "$(_CLOUDSPLAINING_COMPLETE=source cloudsplaining)"
```

To enable ZSH completion, put this in your .zshrc:

```bash
eval "$(_CLOUDSPLAINING_COMPLETE=source_zsh cloudsplaining)"
```

### Scanning a single IAM policy

You can also scan a single policy file to identify risks instead of an entire account.

```bash
cloudsplaining scan-policy-file --input-file examples/policies/explicit-actions.json
```

The output will include a finding description and a list of the IAM actions that do not leverage resource constraints.

The output will resemble the following:

```console
Issue found: Data Exfiltration
Actions: s3:GetObject

Issue found: Resource Exposure
Actions: ecr:DeleteRepositoryPolicy, ecr:SetRepositoryPolicy, s3:BypassGovernanceRetention, s3:DeleteAccessPointPolicy, s3:DeleteBucketPolicy, s3:ObjectOwnerOverrideToBucketOwner, s3:PutAccessPointPolicy, s3:PutAccountPublicAccessBlock, s3:PutBucketAcl, s3:PutBucketPolicy, s3:PutBucketPublicAccessBlock, s3:PutObjectAcl, s3:PutObjectVersionAcl

Issue found: Unrestricted Infrastructure Modification
Actions: ecr:BatchDeleteImage, ecr:CompleteLayerUpload, ecr:CreateRepository, ecr:DeleteLifecyclePolicy, ecr:DeleteRepository, ecr:DeleteRepositoryPolicy, ecr:InitiateLayerUpload, ecr:PutImage, ecr:PutImageScanningConfiguration, ecr:PutImageTagMutability, ecr:PutLifecyclePolicy, ecr:SetRepositoryPolicy, ecr:StartImageScan, ecr:StartLifecyclePolicyPreview, ecr:TagResource, ecr:UntagResource, ecr:UploadLayerPart, s3:AbortMultipartUpload, s3:BypassGovernanceRetention, s3:CreateAccessPoint, s3:CreateBucket, s3:DeleteAccessPoint, s3:DeleteAccessPointPolicy, s3:DeleteBucket, s3:DeleteBucketPolicy, s3:DeleteBucketWebsite, s3:DeleteObject, s3:DeleteObjectTagging, s3:DeleteObjectVersion, s3:DeleteObjectVersionTagging, s3:GetObject, s3:ObjectOwnerOverrideToBucketOwner, s3:PutAccelerateConfiguration, s3:PutAccessPointPolicy, s3:PutAnalyticsConfiguration, s3:PutBucketAcl, s3:PutBucketCORS, s3:PutBucketLogging, s3:PutBucketNotification, s3:PutBucketObjectLockConfiguration, s3:PutBucketPolicy, s3:PutBucketPublicAccessBlock, s3:PutBucketRequestPayment, s3:PutBucketTagging, s3:PutBucketVersioning, s3:PutBucketWebsite, s3:PutEncryptionConfiguration, s3:PutInventoryConfiguration, s3:PutLifecycleConfiguration, s3:PutMetricsConfiguration, s3:PutObject, s3:PutObjectAcl, s3:PutObjectLegalHold, s3:PutObjectRetention, s3:PutObjectTagging, s3:PutObjectVersionAcl, s3:PutObjectVersionTagging, s3:PutReplicationConfiguration, s3:ReplicateDelete, s3:ReplicateObject, s3:ReplicateTags, s3:RestoreObject, s3:UpdateJobPriority, s3:UpdateJobStatus

```

### Scanning an entire AWS Account

#### Downloading Account Authorization Details

We can scan an entire AWS account and generate reports. To do this, we leverage the AWS IAM [get-account-authorization-details](https://docs.aws.amazon.com/cli/latest/reference/iam/get-account-authorization-details.html) API call, which downloads a large JSON file (around 100KB per account) that contains all of the IAM details for the account. This includes data on users, groups, roles, customer-managed policies, and AWS-managed policies.

* You must have AWS credentials configured that can be used by the CLI.

* You must have the privileges to run [iam:GetAccountAuthorizationDetails](https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetAccountAuthorizationDetails.html). The `arn:aws:iam::aws:policy/SecurityAudit` policy includes this, as do many others that allow Read access to the IAM Service.

* To download the account authorization details, ensure you are authenticated to AWS, then run `cloudsplaining`'s `download` command:

```bash
cloudsplaining download
```

* If you prefer to use your `~/.aws/credentials` file instead of environment variables, you can specify the profile name:

```bash
cloudsplaining download --profile myprofile
```

It will download a JSON file in your current directory that contains your account authorization detail information.

#### Create Exclusions file

Cloudsplaining tool does not attempt to understand the context behind everything in your AWS account. It's possible to understand the context behind some of these things programmatically - whether the policy is applied to an instance profile, whether the policy is attached, whether inline IAM policies are in use, and whether or not AWS Managed Policies are in use. **Only you know the context behind the design of your AWS infrastructure and the IAM strategy**.

As such, it's important to eliminate False Positives that are context-dependent. You can do this with an exclusions file. We've included a command that will generate an exclusions file for you so you don't have to remember the required format.

You can create an exclusions template via the following command:

```bash
cloudsplaining create-exclusions-file
```

This will generate a file in your current directory titled `exclusions.yml`.

Now when you run the `scan` command, you can use the exclusions file like this:

```bash
cloudsplaining scan --exclusions-file exclusions.yml --input-file examples/files/example.json --output examples/files/
```

For more information on the structure of the exclusions file, see [Filtering False Positives](#filtering-false-positives)

#### Scanning the Authorization Details file

Now that we've downloaded the account authorization file, we can scan *all* of the AWS IAM policies with `cloudsplaining`.

Run the following command:

```bash
cloudsplaining scan --exclusions-file exclusions.yml --input-file examples/files/example.json --output examples/files/
```

It will create an HTML report like [this](https://opensource.salesforce.com/cloudsplaining/):

> ![](docs/_images/cloudsplaining-report.gif)


It will also create a raw JSON data file:

* `default-iam-results.json`: This contains the raw JSON output of the report. You can use this data file for operating on the scan results for various purposes. For example, you could write a Python script that parses this data and opens up automated JIRA issues or Salesforce Work Items. An example entry is shown below. The full example can be viewed at [examples/files/iam-results-example.json](examples/files/iam-results-example.json)

```json
{
    "example-authz-details": [
        {
            "AccountID": "012345678901",
            "ManagedBy": "Customer",
            "PolicyName": "InsecureUserPolicy",
            "Arn": "arn:aws:iam::012345678901:user/userwithlotsofpermissions",
            "ActionsCount": 2,
            "ServicesCount": 1,
            "Actions": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Services": [
                "s3"
            ]
        }
    ]
}
```


See the [examples/files](examples/files) folder for sample output.

#### Filtering False Positives

Resource constraints are best practice - especially for system roles/instance profiles - but sometimes, these are by design. For example, consider a situation where a custom IAM policy is used on an instance profile for an EC2 instance that provisions Terraform. *In this case, broad permissions are design requirements* - so we don't want to include these in the results.

You can create an exclusions template via the following command:

```bash
cloudsplaining create-exclusions-file
```

This will generate a file in your current directory titled `exclusions.yml`.

The default exclusions file looks like this:

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

* Make any additions or modifications that you want.
  * Under `policies`, list the path of policy names that you want to exclude.
  * If you want to exclude a role titled `MyRole`, list `MyRole` or `MyR*` in the `roles` list.
  * You can follow the same approach for `users` and `groups` list.

Now when you run the `scan` command, you can use the exclusions file like this:

```bash
cloudsplaining scan --exclusions-file exclusions.yml --input-file examples/files/example.json --output examples/files/
```

### Scanning Multiple AWS Accounts

If your IAM user or IAM role has `sts:AssumeRole` permissions to a common IAM role across multiple AWS accounts, you can use the `scan-multi-account` command.

This diagram depicts how the process works:

![Diagram for scanning multiple AWS accounts with Cloudsplaining](docs/_images/scan-multiple-accounts.png)


> Note: If you are new to setting up cross-account access, check out [the official AWS Tutorial on Delegating access across AWS accounts using IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html). That can help you set up the architecture above.


* First, you'll need to create the multi-account config file. Run the following command:

```bash
cloudsplaining create-multi-account-config-file \ 
    -o multi-account-config.yml
```

* This will generate a file called `multi-account-config.yml` with the following contents:

```yaml
accounts:
  default_account: 123456789012
  prod: 123456789013
  test: 123456789014
```

> Note: Observe how the format of the file above includes `account_name: accountID`. Edit the file contents to match your desired account name and account ID. Include as many account IDs as you like.


For the next step, let's say that:
 * We have a role in the target accounts that is called `CommonSecurityRole`. 
* The credentials for your IAM user are under the AWS Credentials profile called `scanning-user`.
* That user has `sts:AssumeRole` permissions to assume the `CommonSecurityRole` in all your target accounts specified in the YAML file we created previously.
* You want to save the output to an S3 bucket called `my-results-bucket`

Using the data above, you can run the following command:

```bash
cloudsplaining scan-multi-account \
    -c multi-account-config.yml \
    --profile scanning-user \
    --role-name CommonSecurityRole \ 
    --output-bucket my-results-bucket
```

> Note that if you run the above without the `--profile` flag, it will execute in the standard [AWS Credentials order of precedence](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html#credentials-default) (i.e., Environment variables, credentials profiles, ECS container credentials, then finally EC2 Instance Profile credentials). 


## Cheatsheet

```bash
# Download authorization details
cloudsplaining download
# Download from a specific AWS profile
cloudsplaining download --profile someprofile

# Scan Authorization details
cloudsplaining scan --input-file default.json
# Scan Authorization details with custom exclusions
cloudsplaining scan --input-file default.json --exclusions-file exclusions.yml

# Scan Policy Files
cloudsplaining scan-policy-file --input-file examples/policies/wildcards.json
cloudsplaining scan-policy-file --input-file examples/policies/wildcards.json  --exclusions-file examples/example-exclusions.yml

# Scan Multiple Accounts
# Generate the multi account config file
cloudsplaining create-multi-account-config-file -o accounts.yml
cloudsplaining scan-multi-account -c accounts.yml -r TargetRole --output-directory ./
```

## FAQ

**Will it scan all policies by default?**

No, it will only scan policies that are attached to IAM principals.

**Will the download command download all policy versions?**

Not by default. If you want to do this, specify the `--include-non-default-policy-versions` flag. Note that the `scan` tool does not currently operate on non-default versions.

**I followed the installation instructions but can't execute the program via command line at all. What do I do?**

This is likely an issue with your PATH. Your PATH environment variable is not considering the binary packages installed by `pip3`. On a Mac, you can likely fix this by entering the command below, depending on the versions you have installed. YMMV.

```bash
export PATH=$HOME/Library/Python/3.7/bin/:$PATH
```

**I followed the installation instructions, but I am receiving a `ModuleNotFoundError` that says `No module named policy_sentry.analysis.expand`. What should I do?**

Try upgrading to the latest version of Cloudsplaining. This error was fixed in version 0.0.10.

## References

* [Policy Sentry](https://github.com/salesforce/policy_sentry/) by [Kinnaird McQuade](https://twitter.com/kmcquade3) at Salesforce
* [Parliament](https://github.com/duo-labs/parliament/) by [Scott Piper](https://twitter.com/0xdabbad00) at [Summit Route](http://summitroute.com/) and Duo Labs.
* [AWS Privilege Escalation Methods](https://github.com/RhinoSecurityLabs/AWS-IAM-Privilege-Escalation) by [Spencer Gietzen](https://twitter.com/SpenGietz) at Rhino Security Labs
* [Understanding Access Level Summaries within Policy Summaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_understand-policy-summary-access-level-summaries.html)
* [Leveraging next-generation blockchain-based AI across multiple service meshes to transparently automate multi-cloud IAM wizardry :mage_man:](http://kmcquade.com/rick.html)
