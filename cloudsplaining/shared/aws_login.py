"""AWS Login utilities"""
import os
import logging
from typing import Optional, List, Tuple

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)


def get_boto3_client(
    service: str, profile: Optional[str] = None, region: str = "us-east-1"
) -> boto3.Session.client:
    """Get a boto3 client for a given service"""
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)

    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    if os.environ.get("LOCALSTACK_ENDPOINT_URL"):
        client = session.client(
            service,
            config=config,
            endpoint_url=os.environ.get("LOCALSTACK_ENDPOINT_URL"),
        )
    else:
        client = session.client(service, config=config)
    logger.debug(
        f"{client.meta.endpoint_url} in {client.meta.region_name}: boto3 client login successful"
    )
    return client


def get_boto3_resource(
    service: str, profile: Optional[str] = None, region: str = "us-east-1"
) -> boto3.Session.resource:
    """Get a boto3 resource for a given service"""
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)

    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    resource = session.resource(service, config=config)
    return resource


def get_current_account_id(sts_client: boto3.Session.client) -> str:
    """Get the current account ID"""
    response = sts_client.get_caller_identity()
    current_account_id: str = response.get("Account", "")
    return current_account_id


def get_available_regions(service: str) -> List[str]:
    """AWS exposes their list of regions as an API. Gather the list."""
    regions: List[str] = boto3.session.Session().get_available_regions(service)
    logger.debug(
        "The service %s does not have available regions. Returning us-east-1 as default"
    )
    if not regions:
        regions = ["us-east-1"]
    return regions


def get_target_account_credentials(
    target_account_role_name: str,
    target_account_id: str,
    role_session_name: str = "Cloudsplaining",
    profile: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Get a boto3 client for a given AWS service

    :param profile:
    :param role_session_name: AssumeRole session name
    :param target_account_role_name: The name of the target account role
    :param target_account_id: The target account ID
    :return:
    """
    default_region = "us-east-1"
    session_data = {"region_name": default_region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)
    config = Config(connect_timeout=5, retries={"max_attempts": 10})
    sts_client = session.client("sts", config=config)

    acct_b = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{target_account_id}:role/{target_account_role_name}",
        RoleSessionName=role_session_name,
    )

    aws_access_key_id = acct_b["Credentials"]["AccessKeyId"]
    aws_secret_access_key = acct_b["Credentials"]["SecretAccessKey"]
    aws_session_token = acct_b["Credentials"]["SessionToken"]

    return aws_access_key_id, aws_secret_access_key, aws_session_token
