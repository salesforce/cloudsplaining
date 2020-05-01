
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
