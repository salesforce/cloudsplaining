# Proposed additions to PRIVILEGE_ESCALATION_METHODS
# Source: DataDog/pathfinding.cloud (39 paths not currently detected as named methods)
# Action lists are exact; method NAMES are proposals (editable).
# NOTE: entries flagged VARIANT overlap a primary technique and will produce a
#       second finding on the same policy -- decide whether to include them.

PRIVILEGE_ESCALATION_METHODS_PATHFINDING_ADDITIONS = {
    # --- new-passrole: iam:PassRole + create NEW resource ---
    "PassExistingRoleToNewAppRunnerService": ["iam:passrole", "apprunner:createservice"],  # apprunner-001
    "PassExistingRoleToNewBedrockCodeInterpreter": ["iam:passrole", "bedrock-agentcore:createcodeinterpreter", "bedrock-agentcore:startcodeinterpretersession", "bedrock-agentcore:invokecodeinterpreter"],  # bedrock-001
    "PassExistingRoleToNewCloudFormationStackSet": ["iam:passrole", "cloudformation:createstackset", "cloudformation:createstackinstances"],  # cloudformation-003
    "PassRoleToUpdateCloudFormationStackSet": ["iam:passrole", "cloudformation:updatestackset"],  # cloudformation-004 -- modifies existing stack set but passes a new role
    "ExecuteCloudFormationChangeSet": ["cloudformation:createchangeset", "cloudformation:executechangeset"],  # cloudformation-005
    "PassExistingRoleToNewCodeBuildProjectThenBuild": ["iam:passrole", "codebuild:createproject", "codebuild:startbuild"],  # codebuild-001
    "PassExistingRoleToNewCodeBuildProjectThenBuildBatch": ["iam:passrole", "codebuild:createproject", "codebuild:startbuildbatch"],  # codebuild-004
    "PassExistingRoleToNewEC2SpotInstance": ["iam:passrole", "ec2:requestspotinstances"],  # ec2-003
    "PassExistingRoleToNewECSClusterServiceTask": ["iam:passrole", "ecs:createcluster", "ecs:registertaskdefinition", "ecs:createservice"],  # ecs-001 -- VARIANT of ecs-003 (adds ecs:CreateCluster) -> overlaps ecs-003
    "PassExistingRoleToNewECSClusterRunTask": ["iam:passrole", "ecs:createcluster", "ecs:registertaskdefinition", "ecs:runtask"],  # ecs-002 -- VARIANT of ecs-004 (adds ecs:CreateCluster) -> overlaps ecs-004
    "PassExistingRoleToNewECSService": ["iam:passrole", "ecs:registertaskdefinition", "ecs:createservice"],  # ecs-003
    "PassExistingRoleToNewECSTaskViaRunTask": ["iam:passrole", "ecs:registertaskdefinition", "ecs:runtask"],  # ecs-004
    "PassExistingRoleToNewECSTaskViaStartTask": ["iam:passrole", "ecs:registertaskdefinition", "ecs:starttask"],  # ecs-005
    "PassExistingRoleToNewGlueJobThenRun": ["iam:passrole", "glue:createjob", "glue:startjobrun"],  # glue-003
    "PassExistingRoleToNewGlueJobViaTrigger": ["iam:passrole", "glue:createjob", "glue:createtrigger"],  # glue-004
    "UpdateExistingGlueJobThenRun": ["iam:passrole", "glue:updatejob", "glue:startjobrun"],  # glue-005
    "UpdateExistingGlueJobViaTrigger": ["iam:passrole", "glue:updatejob", "glue:createtrigger"],  # glue-006
    "PassExistingRoleToNewLambdaThenAddPermission": ["iam:passrole", "lambda:createfunction", "lambda:addpermission"],  # lambda-006
    "PassExistingRoleToNewSageMakerNotebookInstance": ["iam:passrole", "sagemaker:createnotebookinstance"],  # sagemaker-001
    "PassExistingRoleToNewSageMakerTrainingJob": ["iam:passrole", "sagemaker:createtrainingjob"],  # sagemaker-002
    "PassExistingRoleToNewSageMakerProcessingJob": ["iam:passrole", "sagemaker:createprocessingjob"],  # sagemaker-003

    # --- existing-passrole: abuse EXISTING resource that already has a role ---
    "UpdateExistingAppRunnerService": ["apprunner:updateservice"],  # apprunner-002
    "AccessExistingBedrockCodeInterpreter": ["bedrock-agentcore:startcodeinterpretersession", "bedrock-agentcore:invokecodeinterpreter"],  # bedrock-002
    "UpdateExistingCloudFormationStack": ["cloudformation:updatestack"],  # cloudformation-002
    "StartExistingCodeBuildProject": ["codebuild:startbuild"],  # codebuild-002
    "StartExistingCodeBuildProjectBatch": ["codebuild:startbuildbatch"],  # codebuild-003
    "ModifyEC2InstanceUserDataThenRestart": ["ec2:modifyinstanceattribute", "ec2:stopinstances", "ec2:startinstances"],  # ec2-002
    "ModifyExistingEC2LaunchTemplate": ["ec2:createlaunchtemplateversion", "ec2:modifylaunchtemplate"],  # ec2-004
    "EC2InstanceConnectSendSSHPublicKey": ["ec2-instance-connect:sendsshpublickey", "ec2:describeinstances"],  # ec2instanceconnect-003
    "ECSExecuteCommandOnRunningTask": ["ecs:executecommand", "ecs:describetasks"],  # ecs-006
    "CreatePresignedSageMakerNotebookUrl": ["sagemaker:createpresignednotebookinstanceurl"],  # sagemaker-004
    "UpdateSageMakerNotebookLifecycleConfig": ["sagemaker:createnotebookinstancelifecycleconfig", "sagemaker:stopnotebookinstance", "sagemaker:updatenotebookinstance", "sagemaker:startnotebookinstance"],  # sagemaker-005
    "SSMStartSessionOnInstance": ["ssm:startsession"],  # ssm-001
    "SSMSendCommandToInstance": ["ssm:sendcommand"],  # ssm-002

    # --- principal-access: gain access to existing principals / sessions ---
    "UpdateAssumeRolePolicyWithoutAssume": ["iam:updateassumerolepolicy"],  # iam-012 -- cloudsplaining UpdateRolePolicyToAssumeIt bundles sts:assumerole; standalone case
    "AttachRolePolicyThenUpdateAssume": ["iam:attachrolepolicy", "iam:updateassumerolepolicy"],  # iam-019 -- VARIANT of iam-009; superset of AttachRolePolicyWithoutAssume
    "PutRolePolicyThenUpdateAssume": ["iam:putrolepolicy", "iam:updateassumerolepolicy"],  # iam-021 -- VARIANT of iam-005; superset of PutRolePolicyWithoutAssume

    # --- self-escalation: modify own permissions directly ---
    "PutRolePolicyWithoutAssume": ["iam:putrolepolicy"],  # iam-005 -- cloudsplaining PutRolePolicy bundles sts:assumerole; this is the standalone case
    "AttachRolePolicyWithoutAssume": ["iam:attachrolepolicy"],  # iam-009 -- cloudsplaining AttachRolePolicy bundles sts:assumerole; this is the standalone case

}
