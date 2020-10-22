If your IAM policy **does** require access to those actions, you should provide an explanation. Example requirements include:
* **User Role**: This IAM Policy is used by an IAM Role that requires access to `*` resources because human users assume this role. We have restricted the access levels appropriate to what the user needs.
* **Infrastructure Provisioning role**: This IAM Policy is used by roles that deploy infrastructure using CloudFormation or Terraform and need administrative access by design.
* **Conditions logic is in use**: The Policy has access to `*` resources, but the statement enforces least privilege via IAM condition statements.

While other edge cases and justifications exist, the above items are the most common justifications. For information on Common False Positive Scenarios, see [the documentation here](https://cloudsplaining.readthedocs.io/en/latest/report/triage/#common-false-positive-scenarios).
