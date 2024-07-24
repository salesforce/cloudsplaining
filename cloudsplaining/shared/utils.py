"""Just some utility functions that don't fit neatly into other categories"""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
from __future__ import annotations

import json
import logging
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from policy_sentry.querying.actions import (
    get_action_data,
    remove_actions_not_matching_access_level,
)
from policy_sentry.querying.all import get_all_service_prefixes

all_service_prefixes = get_all_service_prefixes()
logger = logging.getLogger(__name__)
OK_GREEN = "\033[92m"
ERROR_RED = "\033[91m"
GREY = "\33[90m"
END = "\033[0m"


def remove_wildcard_only_actions(actions_list: list[str]) -> list[str]:
    """Given a list of actions, remove the ones that CANNOT be restricted to ARNs, leaving only the ones that CAN."""
    try:
        actions_list_unique = set(actions_list)
    except TypeError as t_e:  # pragma: no cover
        print(t_e)
        return []
    results = []
    for action in actions_list_unique:
        service_prefix, action_name = action.split(":")
        if service_prefix not in all_service_prefixes:
            continue  # pragma: no cover
        action_data = get_action_data(service_prefix, action_name)
        if action_data:
            service_data_len = len(action_data.get(service_prefix, []))
            if service_data_len == 0:
                pass  # pragma: no cover
            elif service_data_len == 1:
                if action_data[service_prefix][0]["resource_arn_format"] == "*":
                    pass
                else:
                    # Let's return the CamelCase action name format
                    results.append(action_data[service_prefix][0]["action"])
            else:
                results.append(action_data[service_prefix][0]["action"])
    return results


def remove_read_level_actions(actions_list: list[str]) -> list[str]:
    """Given a set of actions, return that list of actions,
    but only with actions at the 'Write', 'Tagging', or 'Permissions management' levels
    """
    modify_actions: list[str] = remove_actions_not_matching_access_level(actions_list, "Write")
    modify_actions.extend(remove_actions_not_matching_access_level(actions_list, "Permissions management"))
    modify_actions.extend(remove_actions_not_matching_access_level(actions_list, "Tagging"))
    return modify_actions


def get_full_policy_path(arn: str) -> str:
    """
    Resource string will output strings like the following examples.

    Case 1:
      Input: arn:aws:iam::aws:policy/aws-service-role/AmazonGuardDutyServiceRolePolicy
    Output:
      aws-service-role/AmazonGuardDutyServiceRolePolicy
    Case 2:
      Input: arn:aws:iam::123456789012:role/ExampleRole
      Output: ExampleRole
    :param arn:
    :return:
    """
    resource_string = arn.partition("/")[2]
    return resource_string


def get_policy_name(arn: str) -> str:
    """
    Case 1:
        Input: arn:aws:iam::aws:policy/aws-service-role/AmazonGuardDutyServiceRolePolicy
        Output: AmazonGuardDutyServiceRolePolicy
    Case 2:
        Input: arn:aws:iam::123456789012:role/ExampleRole
        Output: ExampleRole
    :return:
    """
    policy_name = arn.rpartition("/")[2]
    return policy_name


def capitalize_first_character(some_string: str) -> str:
    """Description: Capitalizes the first character of a string"""
    return " ".join("".join([w[0].upper(), w[1:].lower()]) for w in some_string.split())


def get_non_provider_id(some_string: str) -> str:
    """
    Not all resources have an ID and some services allow the use of "." in names, which breaks our recursion scheme
    if name is used as an ID. Use SHA256(name) instead.
    """
    name_hash = sha256()  # nosec
    name_hash.update(some_string.encode("utf-8"))
    return name_hash.hexdigest()


def is_aws_managed(arn: str) -> bool:
    """Determine whether the policy is AWS-Managed or Customer-managed based on a Policy ARN pattern."""
    return arn.startswith("arn:aws:iam::aws:")


# pragma: no cover
def write_results_data_file(results: dict[str, dict[str, Any]], raw_data_file: str) -> str:
    """
    Writes the raw data file containing all the results for an AWS account

    :param results: Dictionary containing the scan results for a particular account
    :param raw_data_file:
    :return:
    """
    # Write the output to a results file if that was specified. Otherwise, just print to stdout
    Path(raw_data_file).write_text(json.dumps(results, indent=4, default=str), encoding="utf-8")
    return raw_data_file


def read_yaml_file(filename: str) -> dict[str, Any]:
    """Reads a YAML file, safe loads, and returns the dictionary"""
    cfg: dict[str, Any] = yaml.safe_load(Path(filename).read_text(encoding="utf-8"))
    return cfg


def print_green(string: str) -> None:
    """Print green text"""
    print(f"{OK_GREEN}{string}{END}")


def print_red(string: str) -> None:
    """Print green text"""
    print(f"{ERROR_RED}{string}{END}")


def print_grey(string: str) -> None:
    """Print grey text"""
    print(f"{GREY}{string}{END}")


def write_file(file: str, content: str) -> None:
    """Write content to file"""
    if os.path.exists(file):
        logger.debug("%s exists. Removing the file and replacing its contents.", file)
        os.remove(file)
    Path(file).write_text(content, encoding="utf-8")


def write_json_to_file(file: str, content: str) -> None:
    """Write JSON content to file"""
    if os.path.exists(file):
        logger.debug("%s exists. Removing the file and replacing its contents.", file)
        os.remove(file)

    Path(file).write_text(json.dumps(content, indent=4, default=str), encoding="utf-8")
