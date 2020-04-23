"""Runs aws iam get-authorization-details on all accounts specified in the aws credentials file, and stores them in
account-alias.json """
import os
import json
import logging
import configparser
from pathlib import Path
import boto3
import click
import click_log
from botocore.config import Config

logger = logging.getLogger()
click_log.basic_config(logger)


@click.command(
    short_help="Runs aws iam get-authorization-details on all accounts specified in the aws credentials "
    "file, and stores them in account-alias.json"
)
@click.option(
    "--profile",
    type=str,
    default="default",
    required=True,
    help="Specify 'all' to authenticate to AWS and analyze *all* existing IAM policies. Specify a non-default "
    "profile here. Defaults to the 'default' profile.",
)
@click.option(
    "--output",
    type=click.Path(exists=True),
    default=Path.cwd(),
    help="Path to store the output. Defaults to current directory.",
)
@click.option(
    "--credentials-file",
    type=click.Path(exists=True),
    help="Path to the AWS credentials file.",
    default=str(Path.home()) + "/.aws/credentials",
)
@click.option(
    "--include-non-default-policy-versions",
    is_flag=True,
    default=False,
    help="When downloading AWS managed policy documents, also include the non-default policy versions."
    " Note that this will dramatically increase the size of the downloaded file.",
)
@click_log.simple_verbosity_option(logger)
def download_authorization_details(
    profile, output, credentials_file, include_non_default_policy_versions
):
    """
    Runs aws iam get-authorization-details on all accounts specified in the aws credentials file, and stores them in
    account-alias.json
    """
    # Just default profile
    if profile == "default":
        profiles = ["default"]
        print("profile: default")
    # Get all profiles
    elif profile == "all":
        profiles = get_list_of_aws_profiles(credentials_file)
        print("profile: all profiles")
        print(profiles)
    else:
        credentials_file_profiles = get_list_of_aws_profiles(credentials_file)
        # If it exists in ~/.aws/credentials,
        if profile in credentials_file_profiles:
            print(f"profile: {profile}")
            profiles = [profile]
        else:
            raise Exception(
                "The profile %s is not in the ~/.aws/credentials file", profile
            )
    for profile in profiles:
        print("Running get_account_authorization_details for profile: ", profile)
        get_account_authorization_details(
            profile, output, include_non_default_policy_versions
        )


def get_account_authorization_details(
    profile, output, include_non_default_policy_versions=False
):
    """
    Run aws iam get-account-authorization-details and store locally.

    :param profile: Name of the profile in the AWS Credentials file
    :param output: The path of a directory to store the results.
    :param include_non_default_policy_versions: When downloading AWS managed policy documents, also include the non-default policy versions. Note that this will dramatically increase the size of the downloaded file.
    :return:
    """
    def get_session_via_environment_variables():
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        if aws_access_key_id and aws_secret_access_key and aws_session_token:
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
            )
            return session
        else:
            return False

    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    if get_session_via_environment_variables():
        print("AWS Credentials found in Environment variables.")
        boto3_session = get_session_via_environment_variables()
    else:
        boto3_session = boto3.Session(profile_name=profile)

    iam_client = boto3_session.client("iam", config=config)

    results = {
        "UserDetailList": [],
        "GroupDetailList": [],
        "RoleDetailList": [],
        "Policies": [],
    }
    paginator = iam_client.get_paginator("get_account_authorization_details")
    for page in paginator.paginate(Filter=["User"]):
        # Always add inline user policies
        results["UserDetailList"].extend(page["UserDetailList"])
    for page in paginator.paginate(Filter=["Group"]):
        results["GroupDetailList"].extend(page["GroupDetailList"])
    for page in paginator.paginate(Filter=["Role"]):
        results["RoleDetailList"].extend(page["RoleDetailList"])
        # Ignore Service Linked Roles
        for policy in page["Policies"]:
            if policy["Path"] != "/service-role/":
                results["RoleDetailList"].append(policy)
    for page in paginator.paginate(Filter=["LocalManagedPolicy"]):
        # Add customer-managed policies IF they are attached to IAM principals
        for policy in page["Policies"]:
            if policy["AttachmentCount"] > 0:
                results["Policies"].append(policy)
    for page in paginator.paginate(Filter=["AWSManagedPolicy"]):
        # Add customer-managed policies IF they are attached to IAM principals
        for policy in page["Policies"]:
            if policy["AttachmentCount"] > 0:
                if include_non_default_policy_versions:
                    results["Policies"].append(policy)
                else:
                    policy_version_list = []
                    for policy_version in policy.get("PolicyVersionList"):
                        if policy_version.get("VersionId") == policy.get(
                            "DefaultVersionId"
                        ):
                            policy_version_list.append(policy_version)
                            break
                    entry = {
                        "PolicyName": policy.get("PolicyName"),
                        "PolicyId": policy.get("PolicyId"),
                        "Arn": policy.get("Arn"),
                        "Path": policy.get("Path"),
                        "DefaultVersionId": policy.get("DefaultVersionId"),
                        "AttachmentCount": policy.get("AttachmentCount"),
                        "PermissionsBoundaryUsageCount": policy.get(
                            "PermissionsBoundaryUsageCount"
                        ),
                        "IsAttachable": policy.get("IsAttachable"),
                        "CreateDate": policy.get("CreateDate"),
                        "UpdateDate": policy.get("UpdateDate"),
                        "PolicyVersionList": policy_version_list,
                    }
                    results["Policies"].append(entry)

    filename = os.path.join(output, f"{profile}.json")
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "w") as file:
        json.dump(results, file, indent=4, default=str)
        print(f"Saved results to {filename}")
    return 1


def get_list_of_aws_profiles(credentials_file):
    """Get a list of profiles from the AWS Credentials file"""
    config = configparser.RawConfigParser()
    config.read(credentials_file)
    sections = config.sections()
    legitimate_sections = []
    for section in sections:
        # https://github.com/broamski/aws-mfa#credentials-file-setup
        broamski_suffix = "-long-term"
        # pylint: disable=no-else-continue
        if section.endswith(broamski_suffix):
            # skip it if it's not a real profile we want to evaluate
            continue
        else:
            legitimate_sections.append(section)
    return legitimate_sections


def login(profile_name, service="iam"):
    """Log in to AWS and return a boto3 session."""
    default_region = os.environ.get("AWS_REGION", "us-east-1")
    session_data = {"region_name": default_region}
    if profile_name:
        session_data["profile_name"] = profile_name

    session = boto3.Session(**session_data)

    # Return the service requested by the function - either sts or iam
    if service:
        this_session = session.client(service)
    # By default return IAM
    else:
        this_session = session.client("iam")
    return this_session
