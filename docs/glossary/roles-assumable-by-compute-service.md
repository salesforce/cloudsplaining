## Roles Assumable by Compute Services

IAM Roles can be assumed by AWS Compute Services (such as EC2, ECS, EKS, or Lambda) can present greater risk than user-defined roles, especially if the AWS Compute service is on an instance that is directly or indirectly exposed to the internet. Flagging these roles is particularly useful to penetration testers (or attackers) under certain scenarios. 

For example, if an attacker obtains privileges to execute `ssm:SendCommand` and there are privileged EC2 instances with the SSM agent installed, they can effectively have the privileges of those EC2 instances. Remote Code Execution via AWS Systems Manager Agent was already a known escalation/exploitation path, but Cloudsplaining can make the process of identifying theses cases easier.

