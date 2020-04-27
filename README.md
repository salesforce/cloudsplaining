cloudsplaining
--------------

`cloudsplaining` identifies violations of least privilege in AWS IAM policies.

![](docs/images/cloudsplaining-report.gif)


## Overview

Policy Sentry revealed to us that it is possible to finally write IAM policies according to least privilege.

Before Policy Sentry was released, it was too easy to find IAM policy documents that lacked resource constraints. Consider the policy below,  which allows the IAM principal (a role or user) to run GetObject from any S3 bucket in the AWS account:

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

Cloudsplaining identifies violations of least privilege in AWS IAM policies. It can scan all the policies in your AWS account or it can scan a single policy file.

## Installation

* Download the Tarball from the Releases page in this repository

* Navigate to the directory where you downloaded the Tarball in your Terminal.

* Install it with pip3

```bash
pip3 install --user cloudsplaining-0.0.3.tar.gz
```

* Now you should be able to execute `cloudsplaining` from command line by running `cloudsplaining --help`.

### Scanning a policy file

Let's start with scanning a single policy file.

```bash
cloudsplaining scan-policy-file --file examples/policies/explicit-actions.json
```

The output will include a finding description and a list of the IAM actions that do not leverage resource constraints.

By default, `cloudsplaining` only scans for Modify-level actions - that is, actions at the `Write` and `Permissions management` access levels. If the policy under question has a read-only action without resource constraints - such as `s3:GetObject` - it will not flag that action unless you provide the `--all-access-levels` argument, as shown below.

```bash
cloudsplaining scan-policy-file --file examples/policies/explicit-actions.json --all-access-levels
```

The output will resemble the following:

```console
...
	['ecr:BatchCheckLayerAvailability', 'ecr:BatchGetImage', 'ecr:CompleteLayerUpload', 'ecr:DescribeImages', 'ecr:DescribeRepositories', 'ecr:GetDownloadUrlForLayer', 'ecr:GetRepositoryPolicy', 'ecr:InitiateLayerUpload', 'ecr:ListImages', 'ecr:PutImage', 'ecr:UploadLayerPart']
```


### Scanning an entire AWS Account

#### Downloading Account Authorization Details

We can also scan an entire AWS account and generate reports. To do this, we leverage the AWS IAM [get-account-authorization-details](https://docs.aws.amazon.com/cli/latest/reference/iam/get-account-authorization-details.html) API call, which downloads a large JSON file (around 100KB per account) that contains all of the IAM details for the account. This includes data on users, groups, roles, customer-managed policies, and AWS-managed policies.

To do this, you can leverage `cloudsplaining`'s `download-authorization-details` command:

```bash
cloudsplaining download-authorization-details --profile default
```

It will download a file titled `default.json` in your current directory.

#### Create Exclusions file


```bash
TODO: Exclusions file
```

#### Scanning the Authorization Details file

Now that we've downloaded the account authorization file, we can scan *all* of the AWS IAM policies with `cloudsplaining`.

Run the following command:

```bash
cloudsplaining scan --file default.json --exclusions-file private/my-exclusions-file.yml
```

It will create an HTML report like this:

> ![Cloudsplaining report](examples/files/iam-report-example.html "Example report")


It will also create a raw JSON data file:

* `default-iam-results.json`: This contains the raw JSON output of the report. You can use this data file for operating on the scan results for various purposes. For example, you could write a Python script that parses this data and opens up automated JIRA issues or Salesforce Work Items. An example entry is shown below. The full example can be viewed at [examples/output/example-authz-details-results.json](examples/output/example-authz-details-results.json)

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

To exclude this, create a YAML file that we will use to list out exclusions. The default exclusions file contains these contents:

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
# By default, it includes Actions that could lead to Data Leaks
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

* Copy that file into your own `exclusions.yml` file.
* Make any additions or modifications that you want.
  * Under `policies`, list the path of policy names that you want to exclude.
  * If you want to exclude a role titled `MyRole`, list `MyRole` or `MyR*` in the `roles` list.
  * You can follow the same approach for `users` and `groups` list.

* Now, run the scan while considering the exclusions.

```bash
cloudsplaining scan --file default.json --exclusions-file exclusions.yml
```

* You can also skip the scans on AWS managed policies if you like. Note that by default, AWS managed policies that are attached to IAM principals are scanned.

```bash
cloudsplaining scan --file default.json --exclusions-file exclusions.yml --skip-aws-managed
```

Note that the `scan` command usually takes about 2 minutes per account, given the size of the authorization details file. It's faster if you skip the AWS managed policies, but it will still take about 30 seconds.

## Cheat sheet

```bash
# Download authorization details
cloudsplaining download-authorization-details --profile default
# Download authorization details for **all** of your AWS profiles
cloudsplaining download-authorization-details --profile all

# Scan Authorization details
cloudsplaining scan --file default.json
# Scan Authorization details with custom exclusions
cloudsplaining scan --file default.json --exclusions-file exclusions.yml
# Scan authorization details, but ignore AWS Managed Policies
cloudsplaining scan --file default.json --skip-aws-managed

# Scan Policy Files
scan-policy-file --file examples/wildcards.json
scan-policy-file --file examples/wildcards.json  --exclusions-file examples/example-exclusions.yml
```

## FAQ

* Will it scan all policies by default?

No, it will only scan policies that are attached to IAM principals.

* Will the download command download all policy versions?

Not by default. If you want to do this, specify the `--include-non-default-policy-versions` flag. Note that the `scan` tool does not currently operate on non-default versions.

* I followed the installation instructions but can't execute the program via command line. What do I do?

This is likely an issue with your PATH. Your PATH environment variable is not considering the binary packages installed by `pip3`. On a Mac, you can likely fix this by entering the command below, depending on the versions you have installed. YMMV.

```bash
export PATH=$HOME/Library/Python/3.7/bin/:$PATH
```

## Roadmap

* Insert a read-only actions list in the exclusions file where you can list read-only actions that you care about, while still using the default modify-only behavior.

## References

* [Understanding Access Level Summaries within Policy Summaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_understand-policy-summary-access-level-summaries.html)
