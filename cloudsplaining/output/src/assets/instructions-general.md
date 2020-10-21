### What should I do?

* **Review access levels**: Determine whether or not your IAM Policy actually requires access to the actions in this list.
* **Review resource access**: All of the actions in this list do not leverage resource ARN constraints. For example, a lack of resource ARN constraints would be allowing `s3:GetObject` access to `*` resources. Proper usage of resource ARN constraints would include limiting `s3:GetObject` access to a specific S3 object path, like  `aws:s3:::mybucket/*`, 

### Valid Justifications
If your IAM policy **does** require access to those actions, you should provide an explanation. Example requirements include:
* "User Role: This IAM Policy is used by an IAM Role that requires access to `*` resources because human users assume this role. We have restricted the access levels appropriate to what the user needs."
* "Infrastructure Provisioning role: This IAM Policy is used by roles that deploy infrastructure using CloudFormation or Terraform and need administrative access by design."
* "Conditions logic is in use: The Policy has access to `*` resources, but the statement enforces least privilege via IAM condition statements."

While other edge cases and justifications exist, the above items are the most common justifications. For information on Common False Positive Scenarios, see [the documentation here](https://cloudsplaining.readthedocs.io/en/latest/report/triage/#common-false-positive-scenarios).

### How can I validate my results?

1. Use the Parliament web app to validate your policies: https://parliament.summitroute.com/
2. Use the Cloudsplaining `scan-policy-file` command to validate your policies: https://cloudsplaining.readthedocs.io/en/latest/user-guide/scan-policy-file/
