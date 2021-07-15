"""Runs aws iam get-authorization-details on all accounts specified in the aws credentials file, and stores them in
account-alias.json """
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

import boto3
import click
from botocore.config import Config
from cloudsplaining import set_log_level

logger = logging.getLogger(__name__)


@click.command(
    short_help="Runs aws iam get-authorization-details on all accounts specified in the aws credentials "
    "file, and stores them in account-alias.json"
)
@click.option(
    "--profile",
    "-p",
    type=str,
    required=False,
    help="Specify 'all' to authenticate to AWS and analyze *all* existing IAM policies. Specify a non-default "
    "profile here. Defaults to the 'default' profile.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=True),
    default=Path.cwd(),
    help="Path to store the output. Defaults to current directory.",
)
@click.option(
    "--include-non-default-policy-versions",
    is_flag=True,
    default=False,
    help="When downloading AWS managed policy documents, also include the non-default policy versions."
    " Note that this will dramatically increase the size of the downloaded file.",
)
@click.option("--verbose", "-v", "verbosity", count=True)
def download(
    profile: str, output: str, include_non_default_policy_versions: bool, verbosity: int
) -> int:
    """
    Runs aws iam get-authorization-details on all accounts specified in the aws credentials file, and stores them in
    account-alias.json
    """
    set_log_level(verbosity)

    default_region = "us-east-1"
    session_data = {"region_name": default_region}

    if profile:
        session_data["profile_name"] = profile
        output_filename = Path(output) / f"{profile}.json"
    else:
        output_filename = Path("default.json")

    results = get_account_authorization_details(
        session_data, include_non_default_policy_versions
    )

    output_filename.write_text(json.dumps(results, indent=4, default=str))
    print(f"Saved results to {output_filename}")
    return 1


def get_account_authorization_details(
    session_data: Dict[str, str], include_non_default_policy_versions: bool
) -> Dict[str, List[Any]]:
    """Runs aws-iam-get-account-authorization-details"""
    session = boto3.Session(**session_data)
    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    iam_client = session.client("iam", config=config)

    results: Dict[str, List[Any]] = {
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
    return results
