This policy is leveraged by IAM Roles that can be assumed by AWS Compute Services (such as EC2, ECS, EKS, or Lambda).

Attaching highly permissive policies to Compute Roles can present greater risk than doing so for User Roles. For example, if the AdministrativeAccess Policy is attached to an EC2 Instance Profile on an EC2 instance that is exposed to the internet, any attacker that compromises the privileged EC2 instance would have full administrative access over the account.

Flagging these roles is particularly useful to penetration testers (or attackers) under certain scenarios. For example, if an attacker obtains privileges to execute `ssm:SendCommand` and there are privileged EC2 instances with the SSM agent installed, they can effectively have the privileges of those EC2 instances.

The policy can be leveraged by the following compute services:
