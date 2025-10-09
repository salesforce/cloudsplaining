"""
Text operations specific to IAM actions
"""

from __future__ import annotations


def get_service_from_action(action: str) -> str:
    """
    Returns the service name from a service:action combination
    :param action: ec2:DescribeInstance
    :return: ec2
    """
    service = action.split(":")[0]
    return service.lower()


def get_action_name_from_action(action: str) -> str:
    """
    Returns the lowercase action name from a service:action combination
    :param action: ec2:DescribeInstance
    :return: describeinstance
    """
    action_name = action.split(":")[1]
    return action_name.lower()


def get_lowercase_action_list(action_list: list[str]) -> list[str]:
    """
    Given a list of actions, return the list but in lowercase format
    """
    return [action.lower() for action in action_list]


def get_full_action_name(service: str, action_name: str) -> str:
    """
    Gets the proper formatting for an action - the service, plus colon, plus action name.
    :param service: service name, like s3
    :param action_name: action name, like createbucket
    :return: the resulting string
    """
    return f"{service}:{action_name}"
