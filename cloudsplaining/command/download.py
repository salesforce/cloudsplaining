"""Runs aws iam get-authorization-details on all accounts specified in the aws credentials file, and stores them in
account-alias.json"""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Any

import boto3
import click
from botocore.config import Config

from cloudsplaining import set_log_level

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient

logger = logging.getLogger(__name__)


@click.command(
    short_help="Runs aws iam get-authorization-details on all accounts specified in the aws credentials "
    "file, and stores them in account-alias.json"
)
@click.option(
    "-p",
    "--profile",
    type=str,
    required=False,
    envvar="AWS_DEFAULT_PROFILE",
    help="Specify 'all' to authenticate to AWS and scan from *all* AWS credentials profiles. Specify a non-default profile here. Defaults to the 'default' profile.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Path to store the output. Defaults to current directory.",
)
@click.option(
    "--include-non-default-policy-versions",
    is_flag=True,
    default=False,
    help="When downloading AWS managed policy documents, also include the non-default policy versions. Note that this will dramatically increase the size of the downloaded file.",
)
@click.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def download(profile: str, output: str, include_non_default_policy_versions: bool, verbosity: int) -> int:
    """
    Runs aws iam get-authorization-details on all accounts specified in the aws credentials file, and stores them in
    account-alias.json
    """
    set_log_level(verbosity)

    default_region = "us-east-1"
    session_data = {"region_name": default_region}

    if profile:
        session_data["profile_name"] = profile
        output_filename = os.path.join(output, f"{profile}.json")
    else:
        output_filename = os.path.join(output, "default.json")

    results = get_account_authorization_details(session_data, include_non_default_policy_versions)
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, default=str)
    # output_filename.write_text(json.dumps(results, indent=4, default=str))
    print(f"Saved results to {output_filename}")
    return 1


def get_account_authorization_details(
    session_data: dict[str, str], include_non_default_policy_versions: bool
) -> dict[str, list[Any]]:
    """Runs aws-iam-get-account-authorization-details"""
    session = boto3.Session(**session_data)  # type:ignore[arg-type]
    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    iam_client: IAMClient = session.client("iam", config=config)

    results: dict[str, list[Any]] = {
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
                    for policy_version in policy.get("PolicyVersionList") or []:
                        if policy_version.get("VersionId") == policy.get("DefaultVersionId"):
                            policy_version_list.append(policy_version)
                            break
                    entry = {
                        "PolicyName": policy.get("PolicyName"),
                        "PolicyId": policy.get("PolicyId"),
                        "Arn": policy.get("Arn"),
                        "Path": policy.get("Path"),
                        "DefaultVersionId": policy.get("DefaultVersionId"),
                        "AttachmentCount": policy.get("AttachmentCount"),
                        "PermissionsBoundaryUsageCount": policy.get("PermissionsBoundaryUsageCount"),
                        "IsAttachable": policy.get("IsAttachable"),
                        "CreateDate": policy.get("CreateDate"),
                        "UpdateDate": policy.get("UpdateDate"),
                        "PolicyVersionList": policy_version_list,
                    }
                    results["Policies"].append(entry)
    return results
