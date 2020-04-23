<div name="definition-privilege-escalation" id="definition-privilege-escalation"><h6>Privilege Escalation</h6></div>

These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by [Spencer Gietzen](https://twitter.com/SpenGietz) at Rhino Security Labs. Remediation Guidance can be found [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/).


<div name="definition-resource-exposure" id="definition-resource-exposure"><h6>Resource Exposure</h6></div>

Resource Exposure actions allow modification of Permissions to [resource-based policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html) or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify [AWS Resource Access Manager](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html).


<div name="definition-infrastructure-modification" id="definition-infrastructure-modification"><h6>Infrastructure Modification</h6></div>

Infrastructure Modification describes IAM actions with "modify" capabilities, and can therefore lead to [Resource Hijacking](https://attack.mitre.org/techniques/T1496/), unauthorized creation of Infrastructure, Backdoor creation, and/or modification of existing resources which can result in downtime.

<div name="definition-data-exfiltration" id="definition-data-exfiltration"><h6>Data Exfiltration</h6></div>

Policies with Data leak potential allow certain read-only IAM actions without resource constraints, such as `s3:GetObject`, `ssm:GetParameter*`, or `secretsmanager:GetSecretValue`. Unrestricted `s3:GetObject` permissions has a long history of customer data leaks. `ssm:GetParameter*` and `secretsmanager:GetSecretValue` are both used to access secrets. `rds:CopyDBSnapshot` and `rds:CreateDBSnapshot` can be used to exfiltrate RDS database contents.


