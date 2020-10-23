# `iam:PassRole:*`

## CreateEC2WithExistingIP

#### Description

**Creating an EC2 instance with an existing instance profile: **An attacker with the _iam:PassRole_ and _ec2:RunInstances_ permissions can create a new EC2 instance that they will have operating system access to and pass an existing EC2 instance profile/service role to it.

## PassExistingRoleToNewLambdaThenInvoke

#### Description

**Passing a new role to a Lambda function, then invoking it**: A user with the _iam:PassRole_, _lambda:CreateFunction_, and _lambda:InvokeFunction_ permissions can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice. 

## PassExistingRoleToNewLambdaThenTriggerWithNewDynamo

**Passing a role to a new Lambda function, then triggering it with DynamoDB**: A user with the _iam:PassRole_, _lambda:CreateFunction_, and _lambda:CreateEventSourceMapping_ (and possibly _dynamodb:PutItem_ and _dynamodb:CreateTable_) permissions, but without the _lambda:InvokeFunction_ permission, can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice.

#### Description

## PassExistingRoleToNewLambdaThenTriggerWithExistingDynamo


#### Description

**Passing a role to a new Lambda function, then triggering it with DynamoDB**: A user with the _iam:PassRole_, _lambda:CreateFunction_, and _lambda:CreateEventSourceMapping_ (and possibly _dynamodb:PutItem_ and _dynamodb:CreateTable_) permissions, but without the _lambda:InvokeFunction_ permission, can escalate privileges by passing an existing IAM role to a new Lambda function that includes code to import the relevant AWS library to their programming language of choice, then using it perform actions of their choice.

## EditExistingLambdaFunctionWithRole

**Updating the code of an existing privileged Lambda function**: An attacker with the _lambda:UpdateFunctionCode_ permission could update the code in an existing Lambda function with an IAM role attached so that it would import the relevant AWS library in that programming language and use it to perform actions on behalf of that role.

## PassExistingRoleToNewGlueDevEndpoint

#### Description

**Passing a role to a Glue Development Endpoint**: An attacker with the _iam:PassRole_ and _glue:CreateDevEndpoint_ permissions could create a new AWS Glue development endpoint and pass an existing service role to it. 

## PassExistingRoleToCloudFormation

#### Description

**Passing a role to CloudFormation**: An attacker with the _iam:PassRole_ and _cloudformation:CreateStack_ permissions would be able to escalate privileges by creating a CloudFormation template that will perform actions and create resources using the permissions of the role that was passed when creating a CloudFormation stack.

## PassExistingRoleToNewDataPipeline

#### Description

**Passing a role to Data Pipeline**: An attacker with the _iam:PassRole_, _datapipeline:CreatePipeline_, and _datapipeline:PutPipelineDefinition_ permissions would be able to escalate privileges by creating a pipeline and updating it to run an arbitrary AWS CLI command or create other resources, either once or on an interval with the permissions of the role that was passed in.
