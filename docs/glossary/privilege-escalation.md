# Privilege Escalation Findings

This section of the documentation contains the write-ups of some of the findings - particularly the more specific ones like privilege escalation.

The privilege escalation write-ups are sourced from Rhino Security Labs Research on Privilege escalation [here](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/). 

This catalog is being expanded to track [pathfinding.cloud](https://pathfinding.cloud) (DataDog) — the community source of truth for AWS IAM privilege-escalation paths. The detection logic lives in `PRIVILEGE_ESCALATION_METHODS` in `cloudsplaining/shared/constants.py`, and a gap analysis mapping pathfinding.cloud paths to cloudsplaining's coverage is in [`research/pathfinding-cloud/INTEGRATION-ANALYSIS.md`](https://github.com/salesforce/cloudsplaining/blob/master/research/pathfinding-cloud/INTEGRATION-ANALYSIS.md).

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

**Updating the AssumeRolePolicyDocument of a role**: An attacker with the _iam:UpdateAssumeRolePolicy_ and _sts:AssumeRole_ permissions would be able to change the assume role policy document of any existing role to allow them to assume that role. Cloudsplaining now flags _iam:UpdateAssumeRolePolicy_ on its own (and likewise _iam:AttachRolePolicy_ / _iam:PutRolePolicy_), since the target role may already be assumable by the attacker or by a service ([#580](https://github.com/salesforce/cloudsplaining/issues/580)).

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

## Additional pathfinding.cloud Paths

These privilege-escalation paths come from [pathfinding.cloud](https://pathfinding.cloud) and extend the original Rhino Security Labs set. Each links to its canonical writeup.

### apprunner

- **[PassExistingRoleToNewAppRunnerService](https://pathfinding.cloud/paths/apprunner-001)** — `iam:passrole`, `apprunner:createservice`

### bedrock

- **[PassExistingRoleToNewBedrockCodeInterpreter](https://pathfinding.cloud/paths/bedrock-001)** — `iam:passrole`, `bedrock-agentcore:createcodeinterpreter`, `bedrock-agentcore:startcodeinterpretersession`, `bedrock-agentcore:invokecodeinterpreter`
- **[AccessExistingBedrockCodeInterpreterSession](https://pathfinding.cloud/paths/bedrock-002)** — `bedrock-agentcore:startcodeinterpretersession`, `bedrock-agentcore:invokecodeinterpreter`

### cloudformation

- **[PassExistingRoleToNewCloudFormationStackSet](https://pathfinding.cloud/paths/cloudformation-003)** — `iam:passrole`, `cloudformation:createstackset`, `cloudformation:createstackinstances`
- **[PassRoleToUpdateCloudFormationStackSet](https://pathfinding.cloud/paths/cloudformation-004)** — `iam:passrole`, `cloudformation:updatestackset`
- **[ExecuteCloudFormationChangeSet](https://pathfinding.cloud/paths/cloudformation-005)** — `cloudformation:createchangeset`, `cloudformation:executechangeset`

### codebuild

- **[PassExistingRoleToNewCodeBuildProjectThenBuild](https://pathfinding.cloud/paths/codebuild-001)** — `iam:passrole`, `codebuild:createproject`, `codebuild:startbuild`
- **[PassExistingRoleToNewCodeBuildProjectThenBuildBatch](https://pathfinding.cloud/paths/codebuild-004)** — `iam:passrole`, `codebuild:createproject`, `codebuild:startbuildbatch`

### ec2

- **[ModifyEC2InstanceUserDataThenRestart](https://pathfinding.cloud/paths/ec2-002)** — `ec2:modifyinstanceattribute`, `ec2:stopinstances`, `ec2:startinstances`
- **[PassExistingRoleToNewEC2SpotInstance](https://pathfinding.cloud/paths/ec2-003)** — `iam:passrole`, `ec2:requestspotinstances`
- **[ModifyExistingEC2LaunchTemplate](https://pathfinding.cloud/paths/ec2-004)** — `ec2:createlaunchtemplateversion`, `ec2:modifylaunchtemplate`

### ec2instanceconnect

- **[EC2InstanceConnectSendSSHPublicKey](https://pathfinding.cloud/paths/ec2instanceconnect-003)** — `ec2-instance-connect:sendsshpublickey`, `ec2:describeinstances`

### ecs

- **[PassExistingRoleToNewECSClusterServiceTask](https://pathfinding.cloud/paths/ecs-001)** — `iam:passrole`, `ecs:createcluster`, `ecs:registertaskdefinition`, `ecs:createservice`
- **[PassExistingRoleToNewECSClusterRunTask](https://pathfinding.cloud/paths/ecs-002)** — `iam:passrole`, `ecs:createcluster`, `ecs:registertaskdefinition`, `ecs:runtask`
- **[PassExistingRoleToNewECSService](https://pathfinding.cloud/paths/ecs-003)** — `iam:passrole`, `ecs:registertaskdefinition`, `ecs:createservice`
- **[PassExistingRoleToNewECSTaskViaRunTask](https://pathfinding.cloud/paths/ecs-004)** — `iam:passrole`, `ecs:registertaskdefinition`, `ecs:runtask`
- **[PassExistingRoleToNewECSTaskViaStartTask](https://pathfinding.cloud/paths/ecs-005)** — `iam:passrole`, `ecs:registertaskdefinition`, `ecs:starttask`
- **[ECSExecuteCommandOnRunningTask](https://pathfinding.cloud/paths/ecs-006)** — `ecs:executecommand`, `ecs:describetasks`

### glue

- **[PassExistingRoleToNewGlueJobThenRun](https://pathfinding.cloud/paths/glue-003)** — `iam:passrole`, `glue:createjob`, `glue:startjobrun`
- **[PassExistingRoleToNewGlueJobViaTrigger](https://pathfinding.cloud/paths/glue-004)** — `iam:passrole`, `glue:createjob`, `glue:createtrigger`
- **[PassExistingRoleToUpdatedGlueJobThenRun](https://pathfinding.cloud/paths/glue-005)** — `iam:passrole`, `glue:updatejob`, `glue:startjobrun`
- **[PassExistingRoleToUpdatedGlueJobViaTrigger](https://pathfinding.cloud/paths/glue-006)** — `iam:passrole`, `glue:updatejob`, `glue:createtrigger`

### iam

- **[CreateAndRotateAccessKey](https://pathfinding.cloud/paths/iam-003)** — `iam:createaccesskey`, `iam:deleteaccesskey`
- **[AttachUserPolicyThenCreateAccessKey](https://pathfinding.cloud/paths/iam-015)** — `iam:attachuserpolicy`, `iam:createaccesskey`
- **[CreatePolicyVersionThenAssumeRole](https://pathfinding.cloud/paths/iam-016)** — `iam:createpolicyversion`, `sts:assumerole`
- **[PutUserPolicyThenCreateAccessKey](https://pathfinding.cloud/paths/iam-018)** — `iam:putuserpolicy`, `iam:createaccesskey`
- **[AttachRolePolicyThenUpdateAssumeRolePolicy](https://pathfinding.cloud/paths/iam-019)** — `iam:attachrolepolicy`, `iam:updateassumerolepolicy`
- **[CreatePolicyVersionThenUpdateAssumeRolePolicy](https://pathfinding.cloud/paths/iam-020)** — `iam:createpolicyversion`, `iam:updateassumerolepolicy`
- **[PutRolePolicyThenUpdateAssumeRolePolicy](https://pathfinding.cloud/paths/iam-021)** — `iam:putrolepolicy`, `iam:updateassumerolepolicy`

### lambda

- **[UpdateAndInvokeLambdaFunction](https://pathfinding.cloud/paths/lambda-004)** — `lambda:updatefunctioncode`, `lambda:invokefunction`
- **[UpdateLambdaFunctionAndAddPermission](https://pathfinding.cloud/paths/lambda-005)** — `lambda:updatefunctioncode`, `lambda:addpermission`
- **[PassExistingRoleToNewLambdaThenAddPermission](https://pathfinding.cloud/paths/lambda-006)** — `iam:passrole`, `lambda:createfunction`, `lambda:addpermission`

### sagemaker

- **[PassExistingRoleToNewSageMakerNotebookInstance](https://pathfinding.cloud/paths/sagemaker-001)** — `iam:passrole`, `sagemaker:createnotebookinstance`
- **[PassExistingRoleToNewSageMakerTrainingJob](https://pathfinding.cloud/paths/sagemaker-002)** — `iam:passrole`, `sagemaker:createtrainingjob`
- **[PassExistingRoleToNewSageMakerProcessingJob](https://pathfinding.cloud/paths/sagemaker-003)** — `iam:passrole`, `sagemaker:createprocessingjob`
- **[CreatePresignedSageMakerNotebookUrl](https://pathfinding.cloud/paths/sagemaker-004)** — `sagemaker:createpresignednotebookinstanceurl`
- **[UpdateSageMakerNotebookLifecycleConfig](https://pathfinding.cloud/paths/sagemaker-005)** — `sagemaker:createnotebookinstancelifecycleconfig`, `sagemaker:stopnotebookinstance`, `sagemaker:updatenotebookinstance`, `sagemaker:startnotebookinstance`
