"""
Methods that execute specific queries against the database for the ACTIONS table.
This supports the Policy Sentry query functionality
"""

from __future__ import annotations

import functools
import logging
from typing import Any

from policy_sentry.querying.all import get_all_actions, get_all_service_prefixes
from policy_sentry.querying.arns import (
    get_matching_raw_arns,
    get_resource_type_name_with_raw_arn,
)
from policy_sentry.shared.iam_data import (
    get_service_prefix_data,
    iam_definition,
)
from policy_sentry.util.arns import get_service_from_arn

all_service_prefixes = get_all_service_prefixes()
logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1024)
def get_actions_for_service(service_prefix: str, lowercase: bool = False) -> list[str]:
    """
    Get a list of available actions per AWS service

    Arguments:
        service_prefix: List: An AWS service prefix, like `s3` or `kms`
        lowercase: Set to true to have the list of actions be in all lowercase strings.
    Returns:
        List: A list of actions
    """
    service_prefix_data = get_service_prefix_data(service_prefix)
    results = []
    if service_prefix_data and isinstance(service_prefix_data, dict):
        if lowercase:
            privileges = service_prefix_data["privileges_lower_name"]
        else:
            privileges = service_prefix_data["privileges_lower_name"].values()
        results = [f"{service_prefix}:{action}" for action in privileges]

    return results


@functools.lru_cache(maxsize=1024)
def get_action_data(service: str, action_name: str) -> dict[str, list[dict[str, Any]]]:
    """
    Get details about an IAM Action in JSON format.

    Arguments:
        service: An AWS service prefix, like `s3` or `kms`. Case insensitive.
        action_name: The name of an AWS IAM action, like `GetObject`. To get data about all actions in a service, specify "*". Case insensitive.

    Returns:
        List: A dictionary containing metadata about an IAM Action.
    """
    action_data_results = {}
    try:
        service_prefix_data = get_service_prefix_data(service)
        if action_name.endswith("*"):
            stripped_action_name = action_name.removesuffix("*")
            results = []
            for this_action_name, this_action_data in service_prefix_data["privileges"].items():
                if not this_action_name.startswith(stripped_action_name):
                    continue
                if this_action_data:
                    entries = create_action_data_entries(
                        service_prefix_data=service_prefix_data,
                        action_name=this_action_name,
                        action_data=this_action_data,
                    )
                    results.extend(entries)
            action_data_results[service] = results
            return action_data_results
        else:
            this_action_name = service_prefix_data["privileges_lower_name"].get(action_name.lower())
            if this_action_name:
                this_action_data = service_prefix_data["privileges"][this_action_name]
                entries = create_action_data_entries(
                    service_prefix_data=service_prefix_data,
                    action_name=this_action_name,
                    action_data=this_action_data,
                )
                action_data_results[service] = entries
                return action_data_results
    except TypeError as t_e:
        logger.debug(t_e)

    return action_data_results


def create_action_data_entries(
    service_prefix_data: dict[str, Any], action_name: str, action_data: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Creates entries of IAM Action data.

    Arguments:
        service_prefix_data: IAM Action metadata of an AWS service
        action_name: The name of an AWS IAM action, like `GetObject`. To get data about all actions in a service, specify "*". Case insensitive.
        action_data: Metadata of the given IAM Action
    Returns:
        List: A list of dictionaries containing metadata about an IAM Action.
    """

    results = []
    dependent_actions = []

    # check for condition keys, which can be used with any allowed resource type
    wildcard_condition_keys = []
    if wildcard_resource_type := action_data["resource_types"].get(""):
        wildcard_condition_keys = wildcard_resource_type["condition_keys"]

    for resource_type, resource_type_entry in action_data["resource_types"].items():
        # Set default value for if no other matches are found
        resource_arn_format = "*"
        condition_keys = []
        # Get the dependent actions
        resource_dependent_actions = resource_type_entry["dependent_actions"]
        if resource_dependent_actions:
            dependent_actions.extend(resource_dependent_actions)
        # Get the condition keys
        if resource_type:
            service_resource_data = service_prefix_data["resources"].get(resource_type)
            if service_resource_data:
                resource_arn_format = service_resource_data.get("arn", "*")
                if resource_condition_keys := service_resource_data.get("condition_keys"):
                    condition_keys.extend(resource_condition_keys)

        if wildcard_condition_keys:
            condition_keys.extend(wildcard_condition_keys)

        temp_dict = {
            "action": f"{service_prefix_data['prefix']}:{action_name}",
            "description": action_data["description"],
            "access_level": action_data["access_level"],
            "api_documentation_link": action_data.get("api_documentation_link"),
            "resource_arn_format": resource_arn_format,
            "condition_keys": condition_keys,
            "dependent_actions": dependent_actions,
        }
        results.append(temp_dict)

    return results


def get_actions_with_access_level(service_prefix: str, access_level: str) -> list[str]:
    """
    Get a list of actions in a service under different access levels.

    Arguments:
        service_prefix: A single AWS service prefix, like `s3` or `kms`
        access_level: An access level as it is written in the database, such as 'Read', 'Write', 'List', 'Permisssions management', or 'Tagging'

    Returns:
        List: A list of actions with that access level and service prefix
    """
    results = []
    if service_prefix == "all":
        for some_prefix in all_service_prefixes:
            actions = get_actions_with_access_level(
                service_prefix=some_prefix,
                access_level=access_level,
            )
            if actions:
                results.extend(actions)
    else:
        service_prefix_data = get_service_prefix_data(service_prefix)
        results = [
            f"{service_prefix}:{action_name}"
            for action_name, action_data in service_prefix_data["privileges"].items()
            if action_data["access_level"] == access_level
        ]
    return results


def get_actions_at_access_level_that_support_wildcard_arns_only(service_prefix: str, access_level: str) -> list[str]:
    """
    Get a list of actions at an access level that do not support restricting the action to resource ARNs.
    Set service to "all" to get a list of actions across all services.

    Arguments:
        service_prefix: A single AWS service prefix, like `s3` or `kms`
        access_level: An access level as it is written in the database, such as 'Read', 'Write', 'List', 'Permisssions management', or 'Tagging'
    Returns:
        List: A list of actions at that access level that do not support resource ARN constraints
    """
    results = []
    if service_prefix == "all":
        for some_prefix in all_service_prefixes:
            actions = get_actions_at_access_level_that_support_wildcard_arns_only(
                service_prefix=some_prefix,
                access_level=access_level,
            )
            if actions:
                results.extend(actions)
    else:
        service_prefix_data = get_service_prefix_data(service_prefix)
        for action_name, action_data in service_prefix_data["privileges"].items():
            if action_data["access_level"] == access_level:
                resource_types = action_data["resource_types"]
                if len(resource_types) == 1 and "" in resource_types:
                    results.append(f"{service_prefix}:{action_name}")
    return results


def get_actions_with_arn_type_and_access_level(
    service_prefix: str, resource_type_name: str, access_level: str
) -> list[str]:
    """
    Get a list of actions in a service under different access levels, specific to an ARN format.

    Arguments:
        service_prefix: A single AWS service prefix, like `s3` or `kms`
        resource_type_name: The ARN type name, like `bucket` or `key`
        access_level: Access level like "Read" or "List" or "Permissions management"
    Return:
        List: A list of actions that have that ARN type and Access level
    """
    if resource_type_name == "*":
        return get_actions_at_access_level_that_support_wildcard_arns_only(
            service_prefix=service_prefix, access_level=access_level
        )

    results = []
    if service_prefix == "all":
        for some_prefix in all_service_prefixes:
            actions = get_actions_with_arn_type_and_access_level(
                service_prefix=some_prefix,
                resource_type_name=resource_type_name,
                access_level=access_level,
            )
            if actions:
                results.extend(actions)
    else:
        service_prefix_data = get_service_prefix_data(service_prefix)
        for action_name, action_data in service_prefix_data["privileges"].items():
            if (
                action_data["access_level"] == access_level
                and resource_type_name.lower() in action_data["resource_types_lower_name"]
            ):
                results.append(f"{service_prefix}:{action_name}")

    return results


def get_actions_that_support_wildcard_arns_only(service_prefix: str) -> list[str]:
    """
    Get a list of actions that do not support restricting the action to resource ARNs.
    Set service to "all" to get a list of actions across all services.

    Arguments:
        service_prefix: A single AWS service prefix, like `s3` or `kms`

    Returns:
        List: A list of actions that do not support resource ARN constraints
    """
    results = []
    if service_prefix == "all":
        for some_prefix in all_service_prefixes:
            actions = get_actions_that_support_wildcard_arns_only(
                service_prefix=some_prefix,
            )
            if actions:
                results.extend(actions)
    else:
        service_prefix_data = get_service_prefix_data(service_prefix)
        for action_name, action_data in service_prefix_data["privileges"].items():
            if len(action_data["resource_types"]) == 1 and action_data["resource_types"].get(""):
                results.append(f"{service_prefix}:{action_name}")
    return results


def get_actions_matching_arn_type(service_prefix: str, resource_type_name: str) -> list[str]:
    """
    Get a list of actions in a service specific to ARN type.

    Arguments:
        service_prefix: A single AWS service prefix, like `s3` or `kms`
        resource_type_name: The ARN type name, like `bucket` or `key`
    Return:
        List: A list of actions that have that ARN type
    """
    if resource_type_name == "*":
        return get_actions_that_support_wildcard_arns_only(service_prefix)

    results = []

    if service_prefix == "all":
        for some_prefix in all_service_prefixes:
            actions = get_actions_matching_arn_type(
                service_prefix=some_prefix,
                resource_type_name=resource_type_name,
            )
            if actions:
                results.extend(actions)
    else:
        service_prefix_data = get_service_prefix_data(service_prefix)
        for action_name, action_data in service_prefix_data["privileges"].items():
            if resource_type_name.lower() in action_data["resource_types_lower_name"]:
                results.append(f"{service_prefix}:{action_name}")
    return results


def get_actions_matching_arn(arn: str) -> list[str]:
    """
    Given a user-supplied ARN, get a list of all actions that correspond to that ARN.

    Arguments:
        arn: A user-supplied arn
    Returns:
        List: A list of all actions that can match it.
    """
    raw_arns = get_matching_raw_arns(arn)
    results = set()
    for raw_arn in raw_arns:
        resource_type_name = get_resource_type_name_with_raw_arn(raw_arn)
        if resource_type_name is None:
            continue

        service_prefix = get_service_from_arn(raw_arn)
        service_prefix_data = get_service_prefix_data(service_prefix)
        for action_name, action_data in service_prefix_data["privileges"].items():
            if resource_type_name.lower() in action_data["resource_types_lower_name"]:
                results.add(f"{service_prefix}:{action_name}")

    return list(results)


def get_actions_matching_condition_key(service_prefix: str, condition_key: str) -> list[str]:
    """
    Get a list of actions under a service that allow the use of a specified condition key

    Arguments:
        service_prefix: A single AWS service prefix
        condition_key: The condition key to look for.
    Returns:
        List: A list of actions
    """
    if service_prefix == "all":
        results = []
        for some_prefix in all_service_prefixes:
            actions = get_actions_matching_condition_key(
                service_prefix=some_prefix,
                condition_key=condition_key,
            )
            if actions:
                results.extend(actions)
    else:
        service_prefix_data = get_service_prefix_data(service_prefix)
        results = [
            f"{service_prefix}:{action_name}"
            for action_name, action_data in service_prefix_data["privileges"].items()
            for resource_data in action_data["resource_types"].values()
            if condition_key in resource_data["condition_keys"]
        ]
    return results


# def get_actions_matching_condition_crud_and_arn(
#     condition_key, access_level, raw_arn
# ):
#     """
#     Get a list of IAM Actions matching a condition key, CRUD level, and raw ARN format.
#
#         condition_key: A condition key, like aws:TagKeys
#         access_level: Access level that matches the database value. "Read", "Write", "List", "Tagging", or "Permissions management"
#         raw_arn: The raw ARN format in the database, like arn:${Partition}:s3:::${BucketName}
#     :return: List of IAM Actions
#     """
#     print()
#     # TODO: This one is non-essential right now.
#


def remove_actions_not_matching_access_level(actions_list: list[str], access_level: str) -> list[str]:
    """
    Given a list of actions, return a list of actions that match an access level

    Arguments:
        actions_list: A list of actions
        access_level: 'read', 'write', 'list', 'tagging', or 'permissions-management'
    Returns:
        List: An Updated list of actions, where the actions not matching the requested access level are removed.
    """
    new_actions_list = []

    if actions_list == ["*"]:
        actions_list = []
        for some_prefix in all_service_prefixes:
            service_prefix_data = get_service_prefix_data(some_prefix)
            for action_name, action_data in service_prefix_data["privileges"].items():
                if action_data["access_level"] == access_level:
                    actions_list.append(f"{some_prefix}:{action_name}")
    for action in actions_list:
        try:
            service_prefix, action_name = action.split(":")
        except ValueError as v_e:
            logger.debug(f"{v_e} - for action {action}")
            continue
        result = get_action_matching_access_level(
            service_prefix=service_prefix,
            action_name=action_name,
            access_level=access_level,
        )
        if result:
            new_actions_list.append(result)
    return new_actions_list


def get_action_matching_access_level(service_prefix: str, action_name: str, access_level: str) -> str | None:
    """
    Get the action under a service that match the given access level

    Arguments:
        service_prefix: A single AWS service prefix
        action_name: Name of the action
        access_level: Access level like "Read" or "List" or "Permissions management"
    Returns:
        List: action or None
    """
    service_prefix_data = get_service_prefix_data(service_prefix.lower())
    if service_prefix_data:
        this_action_name = service_prefix_data["privileges_lower_name"].get(action_name.lower())
        if this_action_name:
            action_data = service_prefix_data["privileges"][this_action_name]
            if action_data["access_level"] == access_level:
                return f"{service_prefix}:{this_action_name}"

    return None


def get_dependent_actions(actions_list: list[str]) -> list[str]:
    """
    Given a list of IAM Actions, query the database to determine if the action has dependent actions in the
    fifth column of the Resources, Actions, and Condition keys tables. If it does, add the dependent actions
    to the list, and return the updated list.

    It includes the original action in there as well. So, if you supply `kms:CreateCustomKeyStore`, it will give you `kms:CreateCustomKeyStore` as well as `cloudhsm:DescribeClusters`

    To get dependent actions for a single given IAM action, just provide the action as a list with one item, like this:
    `get_dependent_actions(db_session, ['kms:CreateCustomKeystore'])`

    Arguments:
        actions_list: A list of actions to use in querying the database for dependent actions
    Returns:
        List: Updated list of actions, including dependent actions if applicable.
    """
    new_actions = set()
    for action in actions_list:
        service, action_name = action.split(":")
        rows = get_action_data(service, action_name)
        for row in rows[service]:
            dependent_actions = row["dependent_actions"]
            if dependent_actions:
                new_actions.update(dependent_actions)

    return list(new_actions)


def remove_actions_that_are_not_wildcard_arn_only(actions_list: list[str]) -> list[str]:
    """
    Given a list of actions, remove the ones that CAN be restricted to ARNs, leaving only the ones that cannot.

    Arguments:
        actions_list: A list of actions
    Returns:
        List: An updated list of actions
    """
    # remove duplicates, if there are any
    actions_list_unique = set(actions_list)
    results = []
    for action in actions_list_unique:
        service_prefix, action_name = action.split(":")
        action_data = get_action_data(service_prefix, action_name)
        if len(action_data[service_prefix]) == 1 and action_data[service_prefix][0]["resource_arn_format"] == "*":
            # Let's return the CamelCase action name format
            results.append(action_data[service_prefix][0]["action"])
    return results


def get_privilege_info(service_prefix: str, action: str) -> dict[str, Any]:
    """
    Given a service, like `s3` and an action name, like `ListBucket`, return info about that action.

    Arguments:
        service_prefix: The service prefix, like `s3`
        action: An action name, like `ListBucket`

    Returns:
        List: The info from the docs about that action, along with some of the info from the docs
    """
    try:
        privilege_info: dict[str, Any] = iam_definition[service_prefix]["privileges"][action]
        privilege_info["service_resources"] = iam_definition[service_prefix]["resources"]
        privilege_info["service_conditions"] = iam_definition[service_prefix]["conditions"]
    except KeyError as k_e:
        raise Exception(f"Unknown action {service_prefix}:{action}") from k_e
    return privilege_info


def get_api_documentation_link_for_action(service_prefix: str, action_name: str) -> str | None:
    """
    Given a service, like `s3` and an action name, like `ListBucket`, return the documentation link about that specific
    API call.

    Arguments:
        service_prefix: The service prefix, like `s3`
        action_name: An action name, like `ListBucket`

    Returns:
        List: Link to the documentation about that API call
    """
    rows = get_action_data(service_prefix, action_name)
    for row in rows.get(service_prefix, []):
        doc_link: str | None = row.get("api_documentation_link")
        if doc_link:
            return doc_link
    return None


@functools.lru_cache(maxsize=1024)
def get_all_action_links() -> dict[str, str | None]:
    """
    Gets a huge list of the links to all AWS IAM actions. This is meant for use by Cloudsplaining.

    :return: A dictionary of all actions present in the database, with the values being the API documentation links.
    """
    all_actions = get_all_actions()
    results: dict[str, str | None] = {}
    for action in all_actions:
        try:
            service_prefix, action_name = action.split(":")
        except ValueError as v_e:
            logger.debug(f"{v_e} - for action {action}")
            continue
        link = get_api_documentation_link_for_action(service_prefix, action_name)
        results[action] = link
    return results
