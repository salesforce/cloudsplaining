"""
Util methods for handling operations relating to access levels.
All of these access_levels methods are specific to policy sentry internals."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def override_access_level(
    service_override_config: dict[str, list[str]],
    action_name: str,
    provided_access_level: str,
) -> str | None:
    """
    Given the service-specific override config, determine whether or not the
    override config tells us to override the access level in the documentation.

    Arguments:
        service_override_config: Given that the name
        action_name: The name of the action
        provided_access_level: Read, Write, List, Tagging, or 'Permissions management'.
    """
    real_access_level = None  # This will hold the real access level
    try:
        for access_level, actions_list in service_override_config.items():
            # If it exists in the list, then set the real_access_level to the key (key is read, write, list, etc.)
            # Once we meet this condition, break the loop so we can return the value
            if action_name.lower() in actions_list:
                real_access_level = access_level
                break
    except AttributeError as a_e:
        logger.debug(f"AttributeError: {a_e}\nService overrides config is {service_override_config}")
    # first index will contain the access level given in the override config for that action.
    # since we break the loop, we know it only contains one value.
    if real_access_level and real_access_level != provided_access_level:
        # If AWS hasn't fixed their documentation yet, then our YAML override cfg will not match their documentation.
        # Therefore, accept our override instead.
        return real_access_level
        # Otherwise, they have fixed their documentation because our override file matches their documentation.
        # Therefore, return false because we don't need to override

    return None


def transform_access_level_text(access_level: str) -> str:
    """This takes the Click choices for access levels, like permissions-management, and
    returns the text format matching that access level, but in the format that the database expects
    """
    if access_level == "read":
        level = "Read"
    elif access_level == "write":
        level = "Write"
    elif access_level == "list":
        level = "List"
    elif access_level == "tagging":
        level = "Tagging"
    elif access_level == "permissions-management":
        level = "Permissions management"
    else:
        logger.debug("Error: Please specify the correct access level.")
        sys.exit(0)
    return level


def determine_access_level_override(
    service: str,
    action_name: str,
    provided_access_level: str,
    service_override_config: dict[str, list[str]],
) -> str | None:
    """
    Arguments:
        service: service, like iam
        action_name: action name, like ListUsers
        provided_access_level: The access level provided in the scraping process
        service_override_config: Specific to each service. returned by get_action_overrides_from_yml
    """
    # overrides = get_action_overrides_from_yml(service)
    # To reduce memory, this should be used in the table building,
    # and then run the rest of this for if else statement eval later.
    # Using str.lower to make sure we don't get failing cases if there are
    # minor capitalization differences
    provided_access_level_lower = provided_access_level.lower()
    if provided_access_level_lower == "read":
        override_decision = override_access_level(service_override_config, action_name.lower(), "Read")
    elif provided_access_level_lower == "write":
        override_decision = override_access_level(service_override_config, action_name.lower(), "Write")
    elif provided_access_level_lower == "list":
        override_decision = override_access_level(service_override_config, action_name.lower(), "List")
    elif provided_access_level_lower == "permissions management":
        override_decision = override_access_level(
            service_override_config, action_name.lower(), "Permissions management"
        )
    elif provided_access_level_lower == "tagging":
        override_decision = override_access_level(service_override_config, action_name.lower(), "Tagging")
    else:
        logger.debug(
            "Unknown error - determine_override_status() can't determine the access level of %s:%s during "
            "the scraping process. The provided access level was %s. Exiting...",
            service,
            action_name.lower(),
            provided_access_level,
        )
        sys.exit()
    return override_decision
