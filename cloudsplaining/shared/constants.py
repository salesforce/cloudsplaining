"""Some useful variables to import from various parts of this program."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import os
import logging
import yaml
from cloudsplaining.shared.validation import check_exclusions_schema

logger = logging.getLogger(__name__)


PACKAGE_DIR = str(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)
EXCLUSIONS_FILE = str(os.path.join(PACKAGE_DIR, "shared", "default-exclusions.yml"))

if EXCLUSIONS_FILE:
    with open(EXCLUSIONS_FILE, "r") as yaml_file:
        try:
            DEFAULT_EXCLUSIONS_CONFIG = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            logger.critical(exc)
    check_exclusions_schema(DEFAULT_EXCLUSIONS_CONFIG)

EXCLUSIONS_TEMPLATE = """# Policy names to exclude from evaluation
# Suggestion: Add policies here that are known to be overly permissive by design, after you run the initial report.
policies:
  - "AWSServiceRoleFor*"
  - "*ServiceRolePolicy"
  - "*ServiceLinkedRolePolicy"
  - "AdministratorAccess" # Otherwise, this will take a long time
  - "service-role*"
  - "aws-service-role*"
# Don't evaluate these roles, users, or groups as part of the evaluation
roles:
  - "service-role*"
  - "aws-service-role*"
users:
  - ""
groups:
  - ""
# Read-only actions to include in the results, such as s3:GetObject
# By default, it includes Actions that could lead to Data Exfiltration
include-actions:
  - "s3:GetObject"
  - "ssm:GetParameter"
  - "ssm:GetParameters"
  - "ssm:GetParametersByPath"
  - "secretsmanager:GetSecretValue"
# Write actions to include from the results, such as kms:Decrypt
exclude-actions:
  - ""
"""

MULTI_ACCOUNT_CONFIG_TEMPLATE = """accounts:
  default_account: 123456789012
  prod: 123456789013
  test: 123456789014
"""

# These are some high-priority, read-only IAM actions that could lead to a data leak if
# used on certain data storage resources.
# These are not meant to cover every possibility - just high priority ones.
# For now, we have included s3, SSM Parameter Store, and Secrets Manager.
# Feel free to open up a GitHub issue if you have suggestions.
READ_ONLY_DATA_EXFILTRATION_ACTIONS = [
    "s3:GetObject",
    "ssm:GetParameter",
    "ssm:GetParameters",
    "ssm:GetParametersByPath",
    "secretsmanager:GetSecretValue",
]

PRIVILEGE_ESCALATION_METHODS = {
    # 1. IAM Permissions on Other Users
    "CreateAccessKey": ["iam:createaccesskey"],
    "CreateLoginProfile": ["iam:createloginprofile"],
    "UpdateLoginProfile": ["iam:updateloginprofile"],
    "AddUserToGroup": ["iam:addusertogroup"],
    # 2. Permissions on Policies
    "CreateNewPolicyVersion": ["iam:createpolicyversion"],
    "SetExistingDefaultPolicyVersion": ["iam:setdefaultpolicyversion"],
    "AttachUserPolicy": ["iam:attachuserpolicy"],
    "AttachGroupPolicy": ["iam:attachgrouppolicy"],
    "AttachRolePolicy": ["iam:attachrolepolicy", "sts:assumerole"],
    "PutUserPolicy": ["iam:putuserpolicy"],
    "PutGroupPolicy": ["iam:putgrouppolicy"],
    "PutRolePolicy": ["iam:putrolepolicy", "sts:assumerole"],
    # 3. Updating an AssumeRolePolicy
    "UpdateRolePolicyToAssumeIt": ["iam:updateassumerolepolicy", "sts:assumerole"],
    # 4. iam:PassRole:*
    "CreateEC2WithExistingIP": ["iam:passrole", "ec2:runinstances"],
    "PassExistingRoleToNewLambdaThenInvoke": [
        "iam:passrole",
        "lambda:createfunction",
        "lambda:invokefunction",
    ],
    "PassExistingRoleToNewLambdaThenTriggerWithNewDynamo": [
        "iam:passrole",
        "lambda:createfunction",
        "lambda:createeventsourcemapping",
        "dynamodb:createtable",
        "dynamodb:putitem",
    ],
    "PassExistingRoleToNewLambdaThenTriggerWithExistingDynamo": [
        "iam:passrole",
        "lambda:createfunction",
        "lambda:createeventsourcemapping",
    ],
    "PassExistingRoleToNewGlueDevEndpoint": [
        "iam:passrole",
        "glue:createdevendpoint",
    ],
    "PassExistingRoleToCloudFormation": [
        "iam:passrole",
        "cloudformation:createstack",
    ],
    "PassExistingRoleToNewDataPipeline": [
        "iam:passrole",
        "datapipeline:createpipeline",
    ],
    # 5. Privilege Escalation Using AWS Services
    "UpdateExistingGlueDevEndpoint": ["glue:updatedevendpoint"],
    "EditExistingLambdaFunctionWithRole": ["lambda:updatefunctioncode"],
}

SERVICE_PREFIXES_WITH_COMPUTE_ROLES = ["ec2", "eks", "ecs-tasks", "lambda"]

# AWS API calls that return credentials
# https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a
ACTIONS_THAT_RETURN_CREDENTIALS = [
    "chime:createapikey",
    "codepipeline:pollforjobs",
    "cognito-identity:getopenidtoken",
    "cognito-identity:getopenidtokenfordeveloperidentity",
    "cognito-identity:getcredentialsforidentity",
    "cognito-idp:getsigningcertificate",
    "connect:getfederationtoken",
    "connect:getfederationtokens",
    "ec2:getpassworddata",
    "ecr:getauthorizationtoken",
    "gamelift:requestuploadcredentials",
    "gamelift:GetInstanceAccess",
    "iam:createaccesskey",
    "iam:createloginprofile",
    "iam:createservicespecificcredential",
    "iam:resetservicespecificcredential",
    "iam:updateaccesskey",
    "lightsail:getinstanceaccessdetails",
    "lightsail:downloaddefaultkeypair",
    "lightsail:getrelationaldatabasemasteruserpassword",
    "mediapackage:rotatechannelcredentials",
    "mediapackage:rotateingestendpointcredentials",
    "rds-db:connect",
    "redshift:getclustercredentials",
    "sso:getrolecredentials",
    "sts:assumerole",
    "sts:assumerolewithsaml",
    "sts:assumerolewithwebidentity",
    "sts:getfederationtoken",
    "sts:getsessiontoken",
]
