# Glossary

### Impact

The impact the risk would have on an organization if such a vulnerability were successfully exploited is rated according to criteria listed below. Note that these ratings are based on NIST 800-30 impact definitions.

* **Critical**: The issue causes multiple severe or catastrophic effects on operations, assets or other organizations.
* **High**: Causes produces severe degradation in mission capability to the point that the organization is not able to perform primary functions or results in damage to organizational assets.
* **Medium**: Trigger degradation in mission capability to an extent the application is able to perform its primary functions, but their effectiveness is reduced and there may be damage to the organization's assets.
* **Low**: Results in limited degradation in mission capability; the organization is able to perform its primary functions, but their effectiveness is noticeably reduced and may result in minor damage to the organization's assets.


### Privilege Escalation

These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by [Spencer Gietzen](https://twitter.com/SpenGietz) at Rhino Security Labs. Remediation Guidance can be found [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/).

### Resource Exposure

Resource Exposure actions allow modification of Permissions to [resource-based policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html) or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify [AWS Resource Access Manager](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html).

### Infrastructure Modification

Infrastructure Modification describes IAM actions with "modify" capabilities, and can therefore lead to [Resource Hijacking](https://attack.mitre.org/techniques/T1496/), unauthorized creation of Infrastructure, Backdoor creation, and/or modification of existing resources which can result in downtime.

### Data Exfiltration

Policies with Data leak potential allow certain read-only IAM actions without resource constraints, such as `s3:GetObject`, `ssm:GetParameter*`, or `secretsmanager:GetSecretValue`. Unrestricted `s3:GetObject` permissions has a long history of customer data leaks. `ssm:GetParameter*` and `secretsmanager:GetSecretValue` are both used to access secrets. `rds:CopyDBSnapshot` and `rds:CreateDBSnapshot` can be used to exfiltrate RDS database contents.
