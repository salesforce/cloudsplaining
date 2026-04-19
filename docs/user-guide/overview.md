# Overview

[Cloudsplaining](https://github.com/salesforce/cloudsplaining) identifies violations of least privilege in AWS IAM policies and generates a pretty HTML report. It can scan all the policies in your AWS account, across multiple AWS accounts, or it can scan a single policy file.

It helps to identify IAM actions that do not leverage resource constraints and thus can present the following risks to the AWS account in question without restriction:
* [Data Exfiltration](../glossary/data-exfiltration.md) (`s3:GetObject`, `ssm:GetParameter`, `secretsmanager:GetSecretValue`)
* [Infrastructure Modification](../glossary/infrastructure-modification.md)
* [Resource Exposure](../glossary/resource-exposure.md) (the ability to modify resource-based policies)
* [Privilege Escalation](../glossary/privilege-escalation.md) (based on Rhino Security Labs research)
* [Credentials Exposure](../glossary/credentials-exposure.md)

You can also specify a custom exclusions file to filter out results that are False Positives for various reasons. For example, User Policies are permissive by design, whereas System roles are generally more restrictive. You might also have exclusions that are specific to your organization's multi-account strategy or AWS application architecture.

## Commands

* Download the Account Authorization details JSON file
    - `cloudsplaining download --profile default --output default-account-details.json`
* Generate your custom exclusions file
    - `cloudsplaining create-exclusions-file --output-file exclusions.yml`
* Scan the Account Authorization details
    - `cloudsplaining scan --input-file default-account-details.json --exclusions-file exclusions.yml`
    - This generates two files: (1) The single-file HTML report, and (2) The raw JSON data file
