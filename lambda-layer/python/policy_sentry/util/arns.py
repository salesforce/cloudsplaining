"""
Functions to use for parsing ARNs, matching ARN types, and getting the right fragment/component from an ARN string,
"""

#     Case 1: arn:partition:service:region:account-id:resource
#     Case 2: arn:partition:service:region:account-id:resourcetype/resource
#     Case 3: arn:partition:service:region:account-id:resourcetype/resource/qualifier
#     Case 4: arn:partition:service:region:account-id:resourcetype/resource:qualifier
#     Case 5: arn:partition:service:region:account-id:resourcetype:resource
#     Case 6: arn:partition:service:region:account-id:resourcetype:resource:qualifier
#     Source: https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#genref-arns
from __future__ import annotations

import logging
import re

ARN_SEPARATOR_PATTERN = re.compile(r"[:/]")
# Note: Each service can only have one of these, so these are definitely exceptions
EXCLUSION_LIST = {
    "${ObjectName}",
    "${RepositoryName}",
    "${BucketName}",
    "table/${TableName}",
    "${BucketName}/${ObjectName}",
}

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class ARN:
    """Class that helps to match ARN resource type formats neatly"""

    def __init__(self, provided_arn: str) -> None:
        self.arn = provided_arn
        follows_arn_format = re.search(r"^arn:([^:]*):([^:]*):([^:]*):([^:]*):(.+)$", provided_arn)

        if not follows_arn_format:
            raise Exception("The provided value does not follow required ARN format.")
        try:
            elements = self.arn.split(":", 5)
            self.partition = elements[1]
            self.service_prefix = elements[2]
            self.region = elements[3]
            self.account = elements[4]
            self.resource = elements[5]
        except IndexError as error:
            raise Exception(f"The provided ARN is invalid. IndexError: {error}. Please provide a valid ARN.") from error
        if "/" in self.resource:
            self.resource, self.resource_path = self.resource.split("/", 1)
        elif ":" in self.resource:
            self.resource, self.resource_path = self.resource.split(":", 1)
        self.resource_string = self._resource_string()

    def __repr__(self) -> str:
        return self.arn

    # pylint: disable=too-many-return-statements
    def _resource_string(self) -> str:
        """
        Given an ARN, return the string after the account ID, no matter the ARN format.
        Return:
            String: The resource string, like `resourcetype/resource`
        """
        # Resource string will equal:
        #     Case 1: resource
        #     Case 2: resourcetype/resource
        #     Case 3: resourcetype/resource/qualifier
        #     Case 4: resourcetype/resource:qualifier
        #     Case 5: resourcetype:resource
        #     Case 6: resourcetype:resource:qualifier
        split_arn = self.arn.split(":")
        resource_string = ":".join(split_arn[5:])
        return resource_string

    def same_resource_type(self, arn_in_database: str) -> bool:
        """Given an arn, see if it has the same resource type"""

        # 1. If the RAW ARN in the database is *, then it doesn't have a resource type
        if arn_in_database == "*":
            return False

        # 2. ARNs should have the same service
        elements = arn_in_database.split(":", 5)
        if self.service_prefix != elements[2]:
            return False

        # 3. Add support for resource type wildcards, per #204
        # When specifying an ARN and setting a * on the resource type (e.g. instead of db:instance it is *:*),
        #   multiple ARNs can match.
        #   Previously, this would fail and return empty results.
        #   Now it correctly returns the full list of matching ARNs and corresponding actions.
        resource_type_arn_to_test = parse_arn_for_resource_type(self.arn)
        if resource_type_arn_to_test == "*":
            return True

        # 4. Match patterns for complicated resource strings, leveraging the standardized format of the Raw ARN format
        # table/${TableName} should not match `table/${TableName}/backup/${BackupName}`
        resource_string_arn_in_database = get_resource_string(arn_in_database)

        split_resource_string_in_database = re.split(ARN_SEPARATOR_PATTERN, resource_string_arn_in_database)
        # logger.debug(str(split_resource_string_in_database))
        arn_format_list = []
        for elem in split_resource_string_in_database:
            if "${" not in elem:
                arn_format_list.append(elem)
            else:
                # If an element says something like ${TableName}, normalize it to an empty string
                arn_format_list.append("")

        split_resource_string_to_test = re.split(ARN_SEPARATOR_PATTERN, self.resource_string)
        # 4b: If we have a confusing resource string, the length of the split resource string list
        #  should at least be the same
        # Again, table/${TableName} (len of 2) should not match `table/${TableName}/backup/${BackupName}` (len of 4)
        # if len(split_resource_string_to_test) != len(arn_format_list):
        #     return False

        lower_resource_string = [x.lower() for x in split_resource_string_to_test]
        for elem in arn_format_list:
            if elem and elem.lower() not in lower_resource_string:
                return False

        # 4c: See if the non-normalized fields match
        for idx, elem in enumerate(arn_format_list):
            # If the field is not normalized to empty string, then make sure the resource type segments match
            # So, using table/${TableName}/backup/${BackupName} as an example:
            # table should match, backup should match,
            # and length of the arn_format_list should be the same as split_resource_string_to_test
            # If all conditions match, then the ARN format is the same.
            if elem:
                if elem == split_resource_string_to_test[idx] or split_resource_string_to_test[idx] == "*":
                    pass
                else:
                    return False

        # 4. Special type for S3 bucket objects and CodeCommit repos
        resource_path_arn_in_database = elements[5]
        if resource_path_arn_in_database in EXCLUSION_LIST:
            logger.debug(f"Special type: {resource_path_arn_in_database}")
            # handling special case table/${TableName}
            if resource_string_arn_in_database in (
                "table/${TableName}",
                "${BucketName}",
            ):
                return len(self.resource_string.split("/")) == len(elements[5].split("/"))
            # If we've made it this far, then it is a special type
            # return True
            # Presence of / would mean it's an object in both so it matches
            elif "/" in self.resource_string and "/" in elements[5]:  # noqa: SIM114
                return True
            # / not being present in either means it's a bucket in both so it matches
            elif "/" not in self.resource_string and "/" not in elements[5]:  # noqa: SIM103
                return True
            # If there is a / in one but not in the other, it does not match
            else:
                return False

        # 5. If we've made it this far, then it should pass
        return True


def parse_arn(arn: str) -> dict[str, str]:
    """
    Given an ARN, split up the ARN into the ARN namespacing schema dictated by the AWS docs.
    """
    try:
        elements = arn.split(":", 5)
        result = {
            "arn": elements[0],
            "partition": elements[1],
            "service": elements[2],
            "region": elements[3],
            "account": elements[4],
            "resource": elements[5],
            "resource_path": "",
        }
    except IndexError as error:
        raise Exception(f"IndexError: The provided ARN '{arn}' is invalid. Please provide a valid ARN.") from error
    if "/" in result["resource"]:
        result["resource"], result["resource_path"] = result["resource"].split("/", 1)
    elif ":" in result["resource"]:
        result["resource"], result["resource_path"] = result["resource"].split(":", 1)
    return result


def get_service_from_arn(arn: str) -> str:
    """Given an ARN string, return the service"""
    result = parse_arn(arn)
    return result["service"]


def get_region_from_arn(arn: str) -> str:
    """Given an ARN, return the region in the ARN, if it is available. In certain cases like S3 it is not"""
    result = parse_arn(arn)
    # Support S3 buckets with no values under region
    if result["region"] is None:
        return ""
    return result["region"]


def get_account_from_arn(arn: str) -> str:
    """Given an ARN, return the account ID in the ARN, if it is available. In certain cases like S3 it is not"""
    result = parse_arn(arn)
    # Support S3 buckets with no values under account
    if result["account"] is None:
        return ""
    return result["account"]


def get_resource_path_from_arn(arn: str) -> str | None:
    """Given an ARN, parse it according to ARN namespacing and return the resource path. See
    http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html for more details on ARN namespacing.
    """
    result = parse_arn(arn)
    return result["resource_path"]


def get_resource_string(arn: str) -> str:
    """
    Given an ARN, return the string after the account ID, no matter the ARN format.

    Arguments:
        arn: An ARN, like `arn:partition:service:region:account-id:resourcetype/resource`
    Return:
        String: The resource string, like `resourcetype/resource`
    """
    split_arn = arn.split(":")
    resource_string = ":".join(split_arn[5:])
    return resource_string


# In the meantime, we have to skip this pylint check (consider this as tech debt)
# pylint: disable=inconsistent-return-statements
def parse_arn_for_resource_type(arn: str) -> str | None:
    """
    Parses the resource string (resourcetype/resource and other variants) and grab the resource type.

    Arguments:
        arn: The resource string to parse, like `resourcetype/resource`
    Return:
        String: The resource type, like `bucket` or `object`
    """
    split_arn = arn.split(":")
    resource_string = ":".join(split_arn[5:])
    split_resource = re.split(ARN_SEPARATOR_PATTERN, resource_string)
    if len(split_resource) == 1:
        # logger.debug(f"split_resource length is 1: {str(split_resource)}")
        pass
    elif len(split_resource) > 1:
        return split_resource[0]

    return None


def does_arn_match(arn_to_test: str, arn_in_database: str) -> bool:
    """
    Given two ARNs, determine if they have the same resource type.

    Arguments:
        arn_to_test: ARN provided by user
        arn_in_database: Raw ARN that exists in the policy sentry database

    Returns:
        Boolean: result of whether or not the ARNs match
    """
    this_arn = ARN(arn_to_test)
    return this_arn.same_resource_type(arn_in_database)
