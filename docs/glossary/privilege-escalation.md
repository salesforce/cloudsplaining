"Privilege Escalation" refers to combinations of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/).

These can be categorized into 5 general privilege escalation methods:

1. IAM Permissions on other Users   
2. Permissions on Policies
3. Updating an AssumeRole Policy
4. `iam:PassRole:*`  
5. Privilege Escalation using AWS Services

## IAM Permissions on other Users
  
1. *Creating a new user access key for a different user: *An attacker with the `iam:CreateAccessKey` permission on other users can create an access key ID and secret access key belonging to another user in the AWS environment, if they don’t already have two sets associated with them (which best practice says they shouldn’t).
2. *Creating a new login profile for an IAM user*: An attacker with the `iam:CreateLoginProfile` permission on other users can create a password to use to login to the AWS console on any user that does not already have a login profile setup.
3. *Updating an existing login profile for an IAM user*: An attacker with the `iam:UpdateLoginProfile` permission on other users can change the password used to login to the AWS console on any user that already has a login profile setup.
4. *Adding a user to an Admin group*: An attacker with the `iam:AddUserToGroup` permission can use it to add themselves to an existing IAM Group in the AWS account.


## Permissions on Policies

1. *Creating a new policy version to define custom permissions*: An attacker with the `iam:CreatePolicyVersion` permission can create a new version of an IAM policy that they have access to. This allows them to define their own custom permissions.
2. *Setting the default policy version to an existing version*: An attacker with the `iam:SetDefaultPolicyVersion` permission may be able to escalate privileges through existing policy versions that are not currently in use.
3. *Attaching a higher-privileged policy to a _user_ that they have access to*: An attacker with the `iam:AttachUserPolicy` permission can escalate privileges by attaching a policy to a user that they have access to, adding the permissions of that policy to the attacker.
4. *Attaching a higher-privileged policy to a _group_ that they have access to*: An attacker with the `iam:AttachGroupPolicy` permission can escalate privileges by attaching a policy to a group that they are a part of, adding the permissions of that policy to the attacker.
5. *Attaching a higher-privileged policy to a _role_ that they have access to*: An attacker with the `iam:AttachRolePolicy` permission can escalate privileges by attaching a policy to a role that they have access to, adding the permissions of that policy to the attacker.
6. *Creating/updating an inline policy for a _user_*: An attacker with the `iam:PutUserPolicy` permission can escalate privileges by creating or updating an inline policy for a user that they have access to, adding the permissions of that policy to the attacker.
7. *Creating/updating an inline policy for a _group_*: An attacker with the `iam:PutGroupPolicy` permission can escalate privileges by creating or updating an inline policy for a group that they are a part of, adding the permissions of that policy to the attacker.
8. *Creating/updating an inline policy for a _role_*: An attacker with the `iam:PutRolePolicy` permission can escalate privileges by creating or updating an inline policy for a role that they have access to, adding the permissions of that policy to the attacker.


## Updating an AssumeRole Policy 

1. *Updating the AssumeRolePolicyDocument of a role*: An attacker with the `iam:UpdateAssumeRolePolicy` and `sts:AssumeRole` permissions would be able to change the assume role policy document of any existing role to allow them to assume that role.


## `iam:PassRole:*`

1. *Creating an EC2 instance with an existing instance profile: *An attacker with the `iam:PassRole` and `ec2:RunInstances` permissions can create a new EC2 instance that they will have operating system access to and pass an existing EC2 instance profile/service role to it.
2. *Passing a new role to a Lambda function, then invoking it*: A user with the `iam:PassRole`, `lambda:CreateFunction`, and `lambda:InvokeFunction` permissions can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice. 
3. *Passing a role to a new Lambda function, then triggering it with DynamoDB*: A user with the `iam:PassRole`, `lambda:CreateFunction`, and `lambda:CreateEventSourceMapping` (and possibly `dynamodb:PutItem` and `dynamodb:CreateTable`) permissions, but without the `lambda:InvokeFunction` permission, can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice.
4. *Updating the code of an existing privileged Lambda function*: An attacker with the `lambda:UpdateFunctionCode` permission could update the code in an existing Lambda function with an IAM role attached so that it would import the relevant AWS library in that programming language and use it to perform actions on behalf of that role.
5. *Passing a role to CloudFormation*: An attacker with the `iam:PassRole` and `cloudformation:CreateStack` permissions would be able to escalate privileges by creating a CloudFormation template that will perform actions and create resources using the permissions of the role that was passed when creating a CloudFormation stack.
6. *Passing a role to Data Pipeline*: An attacker with the `iam:PassRole`, `datapipeline:CreatePipeline`, and `datapipeline:PutPipelineDefinition` permissions would be able to escalate privileges by creating a pipeline and updating it to run an arbitrary AWS CLI command or create other resources, either once or on an interval with the permissions of the role that was passed in.
7. *Passing a role to a Glue Development Endpoint*: An attacker with the `iam:PassRole` and `glue:CreateDevEndpoint` permissions could create a new AWS Glue development endpoint and pass an existing service role to it. 

## Privilege Escalation using AWS Services

1. *Updating an existing Glue Dev Endpoint*: An attacker with the `glue:UpdateDevEndpoint` permission would be able to update the associated SSH public key of an existing Glue development endpoint, to then SSH into it and have access to the permissions the attached role has access to.
