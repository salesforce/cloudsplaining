import boto3
from moto import mock_aws

from cloudsplaining.shared.aws_login import (
    get_current_account_id,
    get_available_regions,
    get_target_account_credentials,
    get_boto3_client,
    get_boto3_resource,
)


@mock_aws
def test_get_boto3_client():
    # given
    service = "sts"
    region = "eu-central-1"

    # when
    client = get_boto3_client(service=service, region=region)

    # then
    assert client  # just make sure it doesn't raise an exception


@mock_aws
def test_get_boto3_resource():
    # given
    service = "s3"
    region = "eu-central-1"

    # when
    resource = get_boto3_resource(service=service, region=region)

    # then
    assert resource  # just make sure it doesn't raise an exception


@mock_aws
def test_get_current_account_id():
    # given
    client = boto3.client("sts")

    # when
    account_id = get_current_account_id(client)

    # then
    assert account_id  # make sure it is not empty


@mock_aws
def test_get_available_regions():
    # given
    service = "s3"

    # when
    regions = get_available_regions(service)

    # then
    assert len(regions) >= 30


@mock_aws
def test_get_target_account_credentialscredentials():
    # given
    role_name = "example-role"
    account_id = "111111111111"

    # when
    creds = get_target_account_credentials(
        target_account_role_name=role_name,
        target_account_id=account_id,
    )

    # then
    assert len(creds) == 3
    assert creds[0]  # make sure it is not empty
    assert creds[1]  # make sure it is not empty
    assert creds[2]  # make sure it is not empty
