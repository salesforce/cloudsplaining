# Findings

This section of the documentation contains the write-ups of some of the findings - particularly the more specific ones like privilege escalation.

The privilege escalation write-ups are sourced from Rhino Security Labs Research on Privilege escalation [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/). 

We've sorted those into 5 categories, based on Bishop Fox's 5 larger categories of AWS Privilege Escalation, as described [here](https://labs.bishopfox.com/tech-blog/privilege-escalation-in-aws). Those categories are:

1. IAM Permissions on other Users
2. Permissions on Policies
3. Updating an AssumeRole Policy
4. `iam:PassRole:*`
5. Privilege Escalation using AWS Services
