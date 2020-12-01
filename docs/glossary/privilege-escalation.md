# Privilege Escalation Findings

This section of the documentation contains the write-ups of some of the findings - particularly the more specific ones like privilege escalation.

The privilege escalation write-ups are sourced from Rhino Security Labs Research on Privilege escalation [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/). 

We've sorted those into 5 categories, based on Bishop Fox's 5 larger categories of AWS Privilege Escalation, as described [here](https://labs.bishopfox.com/tech-blog/privilege-escalation-in-aws). Those categories are:

1. IAM Permissions on other Users
2. Permissions on Policies
3. Updating an AssumeRole Policy
4. `iam:PassRole:*`
5. Privilege Escalation using AWS Services

## IAM Permissions on Other Users

### CreateAccessKey

**Creating a new user access key for a different user**: An attacker with the _iam:CreateAccessKey_ permission on other users can create an access key ID and secret access key belonging to another user in the AWS environment, if they don’t already have two sets associated with them (which best practice says they shouldn’t).

### CreateLoginProfile

**Creating a new login profile for an IAM user**: An attacker with the _iam:CreateLoginProfile_ permission on other users can create a password to use to login to the AWS console on any user that does not already have a login profile setup.

### UpdateLoginProfile

**Updating an existing login profile for an IAM user**: An attacker with the _iam:UpdateLoginProfile_ permission on other users can change the password used to login to the AWS console on any user that already has a login profile setup.

### AddUserToGroup

**Adding a user to an Admin group**: An attacker with the _iam:AddUserToGroup_ permission can use it to add themselves to an existing IAM Group in the AWS account.

## Permissions on Policies

### CreateNewPolicyVersion

**Creating a new policy version to define custom permissions**: An attacker with the _iam:CreatePolicyVersion_ permission can create a new version of an IAM policy that they have access to. This allows them to define their own custom permissions.

### SetExistingDefaultPolicyVersion

**Setting the default policy version to an existing version**: An attacker with the _iam:SetDefaultPolicyVersion_ permission may be able to escalate privileges through existing policy versions that are not currently in use.

### AttachUserPolicy

**Attaching a higher-privileged policy to a _user_ that they have access to**: An attacker with the _iam:AttachUserPolicy_ permission can escalate privileges by attaching a policy to a user that they have access to, adding the permissions of that policy to the attacker.

### AttachGroupPolicy


**Attaching a higher-privileged policy to a _group_ that they have access to**: An attacker with the _iam:AttachGroupPolicy_ permission can escalate privileges by attaching a policy to a group that they are a part of, adding the permissions of that policy to the attacker.

### AttachRolePolicy

**Attaching a higher-privileged policy to a _role_ that they have access to**: An attacker with the _iam:AttachRolePolicy_ permission can escalate privileges by attaching a policy to a role that they have access to, adding the permissions of that policy to the attacker.

### PutUserPolicy

**Creating/updating an inline policy for a _user_**: An attacker with the _iam:PutUserPolicy_ permission can escalate privileges by creating or updating an inline policy for a user that they have access to, adding the permissions of that policy to the attacker.

### PutGroupPolicy

**Creating/updating an inline policy for a _group_**: An attacker with the _iam:PutGroupPolicy_ permission can escalate privileges by creating or updating an inline policy for a group that they are a part of, adding the permissions of that policy to the attacker.

### PutRolePolicy

**Creating/updating an inline policy for a _role_**: An attacker with the _iam:PutRolePolicy_ permission can escalate privileges by creating or updating an inline policy for a role that they have access to, adding the permissions of that policy to the attacker.

## Updating an AssumeRole Policy

### UpdatingAssumeRolePolicy

**Updating the AssumeRolePolicyDocument of a role**: An attacker with the _iam:UpdateAssumeRolePolicy_ and _sts:AssumeRole_ permissions would be able to change the assume role policy document of any existing role to allow them to assume that role.

## `iam:PassRole`

### CreateEC2WithExistingIP

**Creating an EC2 instance with an existing instance profile**: An attacker with the _iam:PassRole_ and _ec2:RunInstances_ permissions can create a new EC2 instance that they will have operating system access to and pass an existing EC2 instance profile/service role to it.

### PassExistingRoleToNewLambdaThenInvoke

**Passing a new role to a Lambda function, then invoking it**: A user with the _iam:PassRole_, _lambda:CreateFunction_, and _lambda:InvokeFunction_ permissions can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice. 

### PassExistingRoleToNewLambdaThenTriggerWithNewDynamo

**Passing a role to a new Lambda function, then triggering it with DynamoDB**: A user with the _iam:PassRole_, _lambda:CreateFunction_, and _lambda:CreateEventSourceMapping_ (and possibly _dynamodb:PutItem_ and _dynamodb:CreateTable_) permissions, but without the _lambda:InvokeFunction_ permission, can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice.

### PassExistingRoleToNewLambdaThenTriggerWithExistingDynamo

**Passing a role to a new Lambda function, then triggering it with DynamoDB**: A user with the _iam:PassRole_, _lambda:CreateFunction_, and _lambda:CreateEventSourceMapping_ (and possibly _dynamodb:PutItem_ and _dynamodb:CreateTable_) permissions, but without the _lambda:InvokeFunction_ permission, can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice.

### EditExistingLambdaFunctionWithRole

**Updating the code of an existing privileged Lambda function**: An attacker with the _lambda:UpdateFunctionCode_ permission could update the code in an existing Lambda function with an IAM role attached so that it would import the relevant AWS library in that programming language and use it to perform actions on behalf of that role.

### PassExistingRoleToNewGlueDevEndpoint

**Passing a role to a Glue Development Endpoint**: An attacker with the _iam:PassRole_ and _glue:CreateDevEndpoint_ permissions could create a new AWS Glue development endpoint and pass an existing service role to it. 

### PassExistingRoleToCloudFormation

**Passing a role to CloudFormation**: An attacker with the _iam:PassRole_ and _cloudformation:CreateStack_ permissions would be able to escalate privileges by creating a CloudFormation template that will perform actions and create resources using the permissions of the role that was passed when creating a CloudFormation stack.

### PassExistingRoleToNewDataPipeline

**Passing a role to Data Pipeline**: An attacker with the _iam:PassRole_, _datapipeline:CreatePipeline_, and _datapipeline:PutPipelineDefinition_ permissions would be able to escalate privileges by creating a pipeline and updating it to run an arbitrary AWS CLI command or create other resources, either once or on an interval with the permissions of the role that was passed in.

## Privilege Escalation using AWS Services

### UpdateExistingGlueDevEndpoint

**Updating an existing Glue Dev Endpoint**: An attacker with the _glue:UpdateDevEndpoint_ permission would be able to update the associated SSH public key of an existing Glue development endpoint, to then SSH into it and have access to the permissions the attached role has access to.
