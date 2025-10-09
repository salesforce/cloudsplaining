This report contains the security assessment results from [Cloudsplaining](https://github.com/salesforce/cloudsplaining) - a tool that helps manage your IAM risk landscape by scanning your AWS account and creating a risk-prioritized HTML report.

The report shows the following:


* **High priority risks** in IAM policies, like Privilege Escalation, Resource Exposure, Infrastructure Modification, and Data Exfiltration.
* **Violations of Least Privilege**: Identifies where resource ARN constraints are not used
* **EC2 Instance Profile usage**: If a Compute Service role (like an EC2 instance profile) leverages the policy

* **Policies view:** Shows all policy types ([Customer-Managed Policies](#customer-managed-policy), [Inline Policies](#inline-policy), and [AWS-Managed Policies](#aws-managed-policy)) and their associated findings

* **Principals view**: To view the list of IAM Principals and their associated policies, see the [IAM Principals Tab](#nav-principals).

* **Exclusions**: Considers user-supplied exclusions from the command line arguments. If there are no findings for a particular policy, or if the policy is not attached to any IAM Principals, then the policy is not included. Please refer to the [Exclusions configuration](#exclusions) to see which ones were excluded.

* **Extensive Triaging and Remediation Guidance**: For more information, see the [Prioritization Guidance](#remediation-prioritization) and [Triaging Considerations](#triage-triaging-considerations). Consider using all of the Guidance criteria when reviewing this report as well.

Remediating these issues, where appropriate, will help to limit the blast radius in the case of compromised AWS credentials.
