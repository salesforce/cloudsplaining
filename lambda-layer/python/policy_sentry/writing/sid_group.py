"""
sid_group indicates that this is a collection of policy-related data organized by their SIDs
"""

from __future__ import annotations

import logging
import re
from typing import Any

from policy_sentry.analysis.expand import determine_actions_to_expand
from policy_sentry.querying.actions import (
    get_action_data,
    get_actions_at_access_level_that_support_wildcard_arns_only,
    get_actions_that_support_wildcard_arns_only,
    get_actions_with_arn_type_and_access_level,
    get_dependent_actions,
)
from policy_sentry.querying.all import get_all_actions
from policy_sentry.querying.arns import get_resource_type_name_with_raw_arn
from policy_sentry.shared.constants import POLICY_LANGUAGE_VERSION
from policy_sentry.util.actions import get_lowercase_action_list
from policy_sentry.util.arns import does_arn_match, get_service_from_arn, parse_arn
from policy_sentry.util.text import capitalize_first_character, strip_special_characters
from policy_sentry.writing.minimize import minimize_statement_actions
from policy_sentry.writing.validate import check_actions_schema, check_crud_schema

SANITIZE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9]+")

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class SidGroup:
    """
    This class is critical to the creation of least privilege policies.
    It uses the SIDs as namespaces. The namespaces follow this format:
        `{Servicename}{Accesslevel}{Resourcetypename}`

    So, a resulting statement's SID might look like 'S3ListBucket'

    If a condition key is supplied (like `s3:RequestJob`), the SID string will be significantly longer.

    It will resemble this format:
            `{Servicename}{Accesslevel}{Resourcetypename}{Conditionkeystring}{Conditiontypestring}{Conditionkeyvalue}`

    For example: EC2 write actions on the security-group resource, using the following condition map:
    ```
        "Condition": {
            "StringEquals": {"ec2:ResourceTag/Owner": "${aws:username}"}
        }
    ```

    The resulting SID would be:
        `Ec2WriteSecuritygroupResourcetagownerStringequalsAwsusername`

    Or, for actions that support wildcard ARNs only, an example could be:
        `Ec2WriteMultResourcetagownerStringequalsAwsusername`
    """

    def __init__(self) -> None:
        # Dict instead of list
        # sids instead of ARN
        self.sids: dict[str, dict[str, Any]] = {}
        self.universal_conditions: dict[str, Any] = {}
        self.skip_resource_constraints: list[str] = []
        self.exclude_actions: list[str] = []
        self.wildcard_only_single_actions: list[str] = []
        # When a user requests all wildcard-only actions available under a service at a specific access level
        self.wildcard_only_service_read: list[str] = []
        self.wildcard_only_service_write: list[str] = []
        self.wildcard_only_service_list: list[str] = []
        self.wildcard_only_service_tagging: list[str] = []
        self.wildcard_only_service_permissions_management: list[str] = []

    def get_sid_group(self) -> dict[str, dict[str, Any]]:
        """
        Get the whole SID group as JSON
        """
        return self.sids

    def get_sid(self, sid: str) -> dict[str, Any]:
        """Get a single group by the SID identifier"""
        if self.sids[sid]:
            return self.sids[sid]
        else:
            raise Exception(f"No SID with the value of {sid}")

    def list_sids(self) -> list[str]:
        """
        Get a list of all of the SIDs by their identifiers

        Returns:
            List: A list of SIDs in the SID group
        """
        return list(self.sids.keys())

    def add_exclude_actions(self, exclude_actions: list[str]) -> None:
        """To exclude actions from the output"""
        if exclude_actions:
            expanded_actions = determine_actions_to_expand(exclude_actions)
            self.exclude_actions = [x.lower() for x in expanded_actions]
        else:
            self.exclude_actions = []

    def add_skip_resource_constraints(self, skip_resource_constraints_actions: str | list[str]) -> None:
        """
        To override resource constraint requirements - i.e., instead of restricting `s3:PutObject` to a path and
        allowing `s3:PutObject` to `*` resources, put `s3:GetObject` here.
        """
        if isinstance(skip_resource_constraints_actions, list):
            self.skip_resource_constraints.extend(skip_resource_constraints_actions)
        elif isinstance(skip_resource_constraints_actions, str):
            self.skip_resource_constraints.append(skip_resource_constraints_actions)
        else:
            raise Exception("Please provide 'skip_resource_constraints' as a list of IAM actions.")

    def add_sts_actions(self, sts_actions: dict[str, list[str]]) -> None:
        """
        To add STS actions to the output from special YAML section
        """
        if sts_actions:
            # Hard coded for this special case
            service_prefix = "sts"
            access_level = "Write"

            for action, arns in sts_actions.items():
                clean_action = action.replace("-", "")  # Convention to follow adding dashes instead of CamelCase
                service_action_data = get_action_data(service_prefix, clean_action)

                # Schema validation takes care of this, but just in case. No data returned for the action
                if not service_action_data:
                    raise Exception(f"Could not find service action data for {service_prefix} - {clean_action}")

                for row in service_action_data[service_prefix]:
                    for arn in arns:
                        if not arn:  # skip the - '' situation
                            continue
                        if row["access_level"] == access_level and does_arn_match(arn, row["resource_arn_format"]):
                            raw_arn_format = row["resource_arn_format"]

                            # Each action will get its own namespace sts:AssumeRole -> AssumeRole
                            # -1 index is a neat trick if the colon ever goes away we won't get an index error.
                            sid_namespace = row["action"].split(":")[-1]

                            temp_sid_dict = {
                                "arn": [arn],
                                "service": service_prefix,
                                "access_level": access_level,
                                "arn_format": raw_arn_format,
                                "actions": [row["action"]],
                                "conditions": [],  # TODO: Add conditions
                            }

                            # Using a custom namespace and not gathering actions so no need to find
                            # dependent actions either, though we could do it here

                            if sid_namespace in self.sids:
                                # If the ARN already exists there, skip it.
                                if arn not in self.sids[sid_namespace]["arn"]:
                                    self.sids[sid_namespace]["arn"].append(arn)
                            else:
                                self.sids[sid_namespace] = temp_sid_dict

    def add_requested_service_wide(self, service_prefixes: list[str], access_level: str) -> None:
        """
        When a user requests all wildcard-only actions available under a service at a specific access level

        Arguments:
            service_prefixes: A list of service prefixes
            access_level: The requested access level
        """
        if access_level == "Read":
            self.wildcard_only_service_read = service_prefixes
        elif access_level == "Write":
            self.wildcard_only_service_write = service_prefixes
        elif access_level == "List":
            self.wildcard_only_service_list = service_prefixes
        elif access_level == "Tagging":
            self.wildcard_only_service_tagging = service_prefixes
        elif access_level == "Permissions management":
            self.wildcard_only_service_permissions_management = service_prefixes

    def process_wildcard_only_actions(self) -> None:
        """
        After (1) the list of wildcard-only single actions have been added and (2) the list of wildcard-only service-wide actions have been added, process them and store them under the proper SID.
        """
        provided_wildcard_actions = (
            self.wildcard_only_single_actions
            + get_wildcard_only_actions_matching_services_and_access_level(self.wildcard_only_service_read, "Read")
            + get_wildcard_only_actions_matching_services_and_access_level(self.wildcard_only_service_list, "List")
            + get_wildcard_only_actions_matching_services_and_access_level(self.wildcard_only_service_write, "Write")
            + get_wildcard_only_actions_matching_services_and_access_level(
                self.wildcard_only_service_tagging, "Tagging"
            )
            + get_wildcard_only_actions_matching_services_and_access_level(
                self.wildcard_only_service_permissions_management,
                "Permissions management",
            )
        )
        self.add_wildcard_only_actions(provided_wildcard_actions)

    def get_rendered_policy(self, minimize: int | None = None) -> dict[str, Any]:
        """
        Get the JSON rendered policy

        Arguments:
            minimize: Reduce the character count of policies without creating overlap with other action names
        Returns:
            Dictionary: The IAM Policy JSON
        """
        statements: list[dict[str, Any]] = []
        # Only set the actions to lowercase if minimize is provided
        all_actions = get_all_actions(lowercase=True)

        # render the policy
        sids_to_be_changed = []
        for sid, group in self.sids.items():
            temp_actions = group["actions"]
            if not temp_actions:
                logger.debug(f"No actions for sid {sid}")
                continue
            actions = []
            if self.exclude_actions:
                for temp_action in temp_actions:
                    if temp_action.lower() in self.exclude_actions:
                        logger.debug(f"\tExcluded action: {temp_action}")
                    else:
                        if temp_action not in actions:
                            actions.append(temp_action)
            else:
                actions = temp_actions
            # Check if SID is empty of actions. Continue if yes.
            if not actions:
                continue
            match_found = False
            if minimize is not None and isinstance(minimize, int):
                logger.debug("Minimizing statements...")
                actions = minimize_statement_actions(actions, all_actions, minchars=minimize)
                # searching in the existing statements
                # further minimizing the output
                for stmt in statements:
                    if stmt["Resource"] == group["arn"]:
                        stmt["Action"].extend(x for x in actions if x not in stmt["Action"])
                        match_found = True
                        sids_to_be_changed.append(stmt["Sid"])
                        break
                actions = list(set(actions))  # remove duplicates
            actions.sort()
            logger.debug(f"Adding statement with SID {sid}")
            logger.debug(f"{sid} SID has the actions: {actions}")
            logger.debug(f"{sid} SID has the resources: {group['arn']}")
            if not match_found:
                statements.append(
                    {
                        "Sid": sid,
                        "Effect": "Allow",
                        "Action": actions,
                        "Resource": group["arn"],
                    }
                )

        if sids_to_be_changed:
            for stmt in statements:
                if stmt["Sid"] in sids_to_be_changed:
                    arn_details = parse_arn(stmt["Resource"][0])
                    resource_path = arn_details.get("resource_path")
                    resource_sid_segment = strip_special_characters(f"{arn_details['resource']}{resource_path}")
                    stmt["Sid"] = create_policy_sid_namespace(arn_details["service"], "Mult", resource_sid_segment)
                    # If we have combined the statements, minimize it again
                    if minimize is not None and isinstance(minimize, int):
                        actions = minimize_statement_actions(stmt["Action"], all_actions, minchars=minimize)
                        actions.sort()
                        stmt["Action"] = actions
        policy = {"Version": POLICY_LANGUAGE_VERSION, "Statement": statements}
        return policy

    # pylint: disable=unused-argument
    def add_by_arn_and_access_level(
        self,
        arn_list: list[str],
        access_level: str,
        _conditions_block: dict[str, Any] | None = None,
    ) -> None:
        """
        This adds the user-supplied ARN(s), service prefixes, access levels, and condition keys (if applicable) given
        by the user. It derives the list of IAM actions based on the user's requested ARNs and access levels.

        Arguments:
            arn_list: Just a list of resource ARNs.
            access_level: "Read", "List", "Tagging", "Write", or "Permissions management"
            conditions_block: Optionally, a condition block with one or more conditions
        """
        for arn in arn_list:
            service_prefix = get_service_from_arn(arn)
            if "$" in service_prefix:
                logger.debug(f"Not supported service {service_prefix} found in ARN {arn}")
                continue

            service_action_data = get_action_data(service_prefix, "*")
            for service_prefix, action_data in service_action_data.items():
                for row in action_data:
                    raw_arn_format = row["resource_arn_format"]
                    if row["access_level"] == access_level and does_arn_match(arn, raw_arn_format):
                        resource_type_name = get_resource_type_name_with_raw_arn(raw_arn_format)
                        if resource_type_name is None:
                            continue

                        sid_namespace = create_policy_sid_namespace(service_prefix, access_level, resource_type_name)
                        actions = get_actions_with_arn_type_and_access_level(
                            service_prefix, resource_type_name, access_level
                        )
                        # List comprehension to get all dependent actions that are not in the supplied actions.
                        dependent_actions = [
                            action for action in get_dependent_actions(actions) if action not in actions
                        ]
                        for dep_action in dependent_actions:
                            self.add_action_without_resource_constraint(dep_action)

                        if sid_namespace in self.sids:
                            # If the ARN already exists there, skip it.
                            if arn not in self.sids[sid_namespace]["arn"]:
                                self.sids[sid_namespace]["arn"].append(arn)
                        # If it did not exist before at all, create it.
                        else:
                            temp_sid_dict = {
                                "arn": [arn],
                                "service": service_prefix,
                                "access_level": access_level,
                                "arn_format": raw_arn_format,
                                "actions": actions,
                                "conditions": [],  # TODO: Add conditions
                            }
                            self.sids[sid_namespace] = temp_sid_dict

    def add_action_without_resource_constraint(
        self, action: str, sid_namespace: str = "MultMultNone"
    ) -> dict[str, Any]:
        """
        This handles the cases where certain actions do not handle resource constraints - either by AWS, or for
        flexibility when adding dependent actions.

        Arguments:
            action: The single action to add to the SID namespace. For instance, s3:ListAllMyBuckets
            sid_namespace: MultMultNone by default. Other valid option is "SkipResourceConstraints"
        """
        if sid_namespace == "SkipResourceConstraints":
            temp_sid_dict = {
                "arn": ["*"],
                "service": "Skip",
                "access_level": "ResourceConstraints",
                "arn_format": "*",
                "actions": [action],
            }
        elif sid_namespace == "MultMultNone":
            temp_sid_dict = {
                "arn": ["*"],
                "service": "Mult",
                "access_level": "Mult",
                "arn_format": "*",
                "actions": [action],
            }
        else:
            raise Exception("Please specify the sid_namespace as either 'SkipResourceConstraints' or 'MultMultNone'.")
        if isinstance(action, str):
            if sid_namespace in self.sids:
                if action not in self.sids[sid_namespace]["actions"]:
                    self.sids[sid_namespace]["actions"].append(action)
            else:
                self.sids[sid_namespace] = temp_sid_dict
        else:
            raise Exception("Please provide the action as a string, not a list.")
        return self.sids

    def add_by_list_of_actions(self, supplied_actions: list[str]) -> dict[str, Any]:
        """
        Takes a list of actions, queries the database for corresponding arns, adds them to the object.

        Arguments:
            supplied_actions: A list of supplied actions
        """
        dependent_actions = [
            action for action in get_dependent_actions(supplied_actions) if action not in supplied_actions
        ]
        logger.debug("Adding by list of actions")
        logger.debug(f"Supplied actions: {supplied_actions}")
        logger.debug(f"Dependent actions: {dependent_actions}")
        arns_matching_supplied_actions = []

        # arns_matching_supplied_actions is a list of dicts.
        # It must do this rather than dictionaries because there will be duplicate
        #     values by nature of how the entries in the IAM database are structured.
        # I'll provide the example values here to improve readability.

        for action in supplied_actions:
            service_name, action_name = action.split(":")
            action_data = get_action_data(service_name, action_name)
            for row in action_data[service_name]:
                if row["resource_arn_format"] not in arns_matching_supplied_actions:
                    arns_matching_supplied_actions.append(
                        {
                            "resource_arn_format": row["resource_arn_format"],
                            "access_level": row["access_level"],
                            "action": row["action"],
                        }
                    )

        # Identify the actions that do not support resource constraints
        # If that's the case, add it to the wildcard namespace. Otherwise, don't add it.

        actions_without_resource_constraints = []
        for item in arns_matching_supplied_actions:
            if item["resource_arn_format"] != "*":
                self.add_by_arn_and_access_level([item["resource_arn_format"]], item["access_level"])
            else:
                actions_without_resource_constraints.append(item["action"])

        # If there are any dependent actions, we need to add them without resource constraints.
        # Otherwise, we get into issues where the amount of extra SIDs will balloon.
        # Also, the user has no way of knowing what those dependent actions are beforehand.
        # TODO: This is, in fact, a great opportunity to introduce conditions. But we aren't there yet.
        for dep_action in dependent_actions:
            self.add_action_without_resource_constraint(dep_action)
        # Now, because add_by_arn_and_access_level() adds all actions under an access level, we have to
        # remove all actions that do not match the supplied_actions. This is done in-place.
        logger.debug("Purging actions that do not match the requested actions and dependent actions")
        logger.debug(f"Supplied actions: {supplied_actions}")
        logger.debug(f"Dependent actions: {dependent_actions}")
        self.remove_actions_not_matching_these(supplied_actions + dependent_actions)
        for action in actions_without_resource_constraints:
            logger.debug(f"Deliberately adding the action {action} without resource constraints")
            self.add_action_without_resource_constraint(action)
        logger.debug(
            "Removing actions that are in the wildcard arn (Resources = '*') as well as other statements that have "
            "resource constraints "
        )
        self.remove_actions_duplicated_in_wildcard_arn()
        logger.debug("Getting the rendered policy")
        rendered_policy = self.get_rendered_policy()
        return rendered_policy

    def process_template(self, cfg: dict[str, Any], minimize: int | None = None) -> dict[str, Any]:
        """
        Process the Policy Sentry template as a dict. This auto-detects whether or not the file is in CRUD mode or
        Actions mode.

        Arguments:
            cfg: The loaded YAML as a dict. Must follow Policy Sentry dictated format.
            minimize: Minimize the resulting statement with *safe* usage of wildcards to reduce policy length. Set this to the character length you want - for example, 0, or 4. Defaults to none.
        Returns:
            Dictionary: The rendered IAM JSON Policy
        """
        cfg_mode = cfg.get("mode")
        if cfg_mode == "crud":
            logger.debug("CRUD mode selected")
            check_crud_schema(cfg)
            # EXCLUDE ACTIONS
            cfg_exclude = cfg.get("exclude-actions")
            if cfg_exclude and cfg_exclude[0]:
                self.add_exclude_actions(cfg_exclude)
            # WILDCARD ONLY SECTION
            cfg_wildcard = cfg.get("wildcard-only")
            if cfg_wildcard:
                provided_wildcard_actions = cfg_wildcard.get("single-actions")
                if provided_wildcard_actions and provided_wildcard_actions[0] != "":
                    logger.debug(f"Requested wildcard-only actions: {provided_wildcard_actions}")
                    self.wildcard_only_single_actions = provided_wildcard_actions

                service_read = cfg_wildcard.get("service-read")
                if service_read and service_read[0]:
                    logger.debug(f"Requested wildcard-only actions: {service_read}")
                    self.wildcard_only_service_read = service_read

                service_write = cfg_wildcard.get("service-write")
                if service_write and service_write[0]:
                    logger.debug(f"Requested wildcard-only actions: {service_write}")
                    self.wildcard_only_service_write = service_write

                service_list = cfg_wildcard.get("service-list")
                if service_list and service_list[0]:
                    logger.debug(f"Requested wildcard-only actions: {service_list}")
                    self.wildcard_only_service_list = service_list

                service_tagging = cfg_wildcard.get("service-tagging")
                if service_tagging and service_tagging[0]:
                    logger.debug(f"Requested wildcard-only actions: {service_tagging}")
                    self.wildcard_only_service_tagging = service_tagging

                service_permissions_management = cfg_wildcard.get("service-permissions-management")
                if service_permissions_management and service_permissions_management[0]:
                    logger.debug(f"Requested wildcard-only actions: {service_permissions_management}")
                    self.wildcard_only_service_permissions_management = service_permissions_management

            # Process the wildcard-only section
            self.process_wildcard_only_actions()

            # Standard access levels
            cfg_read = cfg.get("read")
            if cfg_read and cfg_read[0]:
                logger.debug(f"Requested access to arns: {cfg_read}")
                self.add_by_arn_and_access_level(cfg_read, "Read")
            cfg_write = cfg.get("write")
            if cfg_write and cfg_write[0]:
                logger.debug(f"Requested access to arns: {cfg_write}")
                self.add_by_arn_and_access_level(cfg_write, "Write")
            cfg_list = cfg.get("list")
            if cfg_list and cfg_list[0]:
                logger.debug(f"Requested access to arns: {cfg_list}")
                self.add_by_arn_and_access_level(cfg_list, "List")
            tagging = cfg.get("tagging")
            if tagging and tagging[0]:
                logger.debug(f"Requested access to arns: {tagging}")
                self.add_by_arn_and_access_level(tagging, "Tagging")
            cfg_mgmt = cfg.get("permissions-management")
            if cfg_mgmt and cfg_mgmt[0]:
                logger.debug(f"Requested access to arns: {cfg_mgmt}")
                self.add_by_arn_and_access_level(cfg_mgmt, "Permissions management")

            # SKIP RESOURCE CONSTRAINTS
            cfg_skip = cfg.get("skip-resource-constraints")
            if cfg_skip and cfg_skip[0]:
                logger.debug(f"Requested override: the actions {cfg_skip} will skip resource constraints.")
                self.add_skip_resource_constraints(cfg_skip)
                for skip_resource_constraints_action in self.skip_resource_constraints:
                    self.add_action_without_resource_constraint(
                        skip_resource_constraints_action, "SkipResourceConstraints"
                    )

            # STS Section
            cfg_sts = cfg.get("sts")
            if cfg_sts:
                logger.debug("STS section detected. Building assume role policy statement")
                self.add_sts_actions(cfg_sts)

        elif cfg_mode == "actions":
            check_actions_schema(cfg)
            if "actions" in cfg:
                cfg_actions = cfg["actions"]
                if cfg_actions is not None and cfg_actions[0] != "":
                    self.add_by_list_of_actions(cfg_actions)

        rendered_policy = self.get_rendered_policy(minimize)
        return rendered_policy

    def add_wildcard_only_actions(self, provided_wildcard_actions: list[str]) -> None:
        """
        Given a list of IAM actions, add individual IAM Actions that do not support resource constraints to the MultMultNone SID

        Arguments:
            provided_wildcard_actions: list actions provided by the user.
        """
        if isinstance(provided_wildcard_actions, list):
            verified_wildcard_actions = remove_actions_that_are_not_wildcard_arn_only(provided_wildcard_actions)
            if verified_wildcard_actions:
                logger.debug(f"Attempting to add the following actions to the policy: {verified_wildcard_actions}")
                self.add_by_list_of_actions(verified_wildcard_actions)
                logger.debug(f"Added the following wildcard-only actions to the policy: {verified_wildcard_actions}")

    def add_wildcard_only_actions_matching_services_and_access_level(
        self, services: list[str], access_level: str
    ) -> None:
        """
        Arguments:
            services: A list of AWS services
            access_level: An access level as it is written in the database, such as 'Read', 'Write', 'List', 'Permissions management', or 'Tagging'
        """
        wildcard_only_actions_to_add = []
        for service in services:
            actions = get_actions_at_access_level_that_support_wildcard_arns_only(service, access_level)
            wildcard_only_actions_to_add.extend(actions)
        self.add_wildcard_only_actions(wildcard_only_actions_to_add)

    def remove_actions_not_matching_these(self, actions_to_keep: list[str]) -> None:
        """
        Arguments:
            actions_to_keep: A list of actions to leave in the policy. All actions not in this list are removed.
        """
        actions_to_keep = get_lowercase_action_list(actions_to_keep)
        actions_deleted = []
        for group in self.sids.values():
            placeholder_actions_list = []
            for action in group["actions"]:
                # if the action is not in the list of selected actions, don't copy it to the placeholder list
                action_lower = action.lower()
                if action_lower in actions_to_keep:
                    placeholder_actions_list.append(action)
                else:
                    logger.debug(f"{action_lower} not found in list of actions to keep: {actions_to_keep}")
                    actions_deleted.append(action)
            # only include the updated actions
            group["actions"] = placeholder_actions_list
        # Highlight the actions that you remove
        logger.debug(f"Actions deleted: {actions_deleted}")
        # Now that we've removed a bunch of actions, if there are SID groups without any actions,
        # remove them so we don't get SIDs with empty action lists
        self.remove_sids_with_empty_action_lists()

    def remove_sids_with_empty_action_lists(self) -> None:
        """
        Now that we've removed a bunch of actions, if there are SID groups without any actions, remove them so we don't get SIDs with empty action lists
        """
        sid_namespaces_to_delete = [
            sid
            for sid, group in self.sids.items()
            if not group["actions"]  # If the size is zero, add it to the indexes_to_delete list.
        ]
        # Loop through sid_namespaces_to_delete in reverse order (so we delete index
        # 10 before index 8, for example)
        for sid in reversed(sid_namespaces_to_delete):
            del self.sids[sid]

    def remove_actions_duplicated_in_wildcard_arn(self) -> None:
        """
        Removes actions from the object that are in a resource-specific ARN, as well as the `*` resource.
        For example, if `ssm:GetParameter` is restricted to a specific parameter path, as well as `*`, then we want to
        remove the `*` option to force least privilege.
        """
        actions_under_wildcard_resources = []
        actions_under_wildcard_resources_to_nuke = []

        # Build a temporary list. Contains actions in MultMultNone SID (where resources = "*")
        for group in self.sids.values():
            if group["arn_format"] == "*":
                actions_under_wildcard_resources.extend(group["actions"])

        # If the actions under the MultMultNone SID exist under other SIDs
        if actions_under_wildcard_resources:
            for group in self.sids.values():
                if "*" not in group["arn_format"]:
                    for action in actions_under_wildcard_resources:
                        if action in group["actions"] and action not in self.skip_resource_constraints:
                            # add it to a list of actions to nuke when they are under other SIDs
                            actions_under_wildcard_resources_to_nuke.append(action)  # noqa: PERF401

        # If there are actions that we need to remove from SIDs outside of MultMultNone SID
        if actions_under_wildcard_resources_to_nuke:
            for group in self.sids.values():
                if "*" in group["arn_format"]:
                    for action in actions_under_wildcard_resources_to_nuke:
                        if action in group["actions"]:
                            group["actions"].remove(action)


def remove_actions_that_are_not_wildcard_arn_only(actions_list: list[str]) -> list[str]:
    """
    Given a list of actions, remove the ones that CAN be restricted to ARNs, leaving only the ones that cannot.

    Arguments:
        actions_list: A list of actions
    Returns:
        List: An updated list of actions
    """
    # remove duplicates, if there are any
    actions_set = set(actions_list)
    actions_list_placeholder = []

    for action in actions_set:
        try:
            service_name, _ = action.split(":")
        except ValueError as v_e:
            # We will skip the action because this likely means that the wildcard action provided is not valid.
            logger.debug(v_e)
            logger.debug("The value provided in wildcard-only section is not formatted properly.")
            continue

        action_lower = action.lower()
        rows = get_actions_that_support_wildcard_arns_only(service_name)
        for row in rows:
            if row.lower() == action_lower:
                actions_list_placeholder.append(action)  # noqa: PERF401
    return actions_list_placeholder


def get_wildcard_only_actions_matching_services_and_access_level(services: list[str], access_level: str) -> list[str]:
    """
    Get a list of wildcard-only actions matching the services and access level

    Arguments:
        services: A list of AWS services
        access_level: An access level as it is written in the database, such as 'Read', 'Write', 'List', 'Permissions management', or 'Tagging'
    Returns:
        List: A list of wildcard-only actions matching the services and access level
    """
    wildcard_only_actions_to_add = []
    for service in services:
        actions = get_actions_at_access_level_that_support_wildcard_arns_only(service, access_level)
        wildcard_only_actions_to_add.extend(actions)
    return wildcard_only_actions_to_add


def create_policy_sid_namespace(
    service: str,
    access_level: str,
    resource_type_name: str,
    condition_block: dict[str, Any] | None = None,
) -> str:
    """
    Simply generates the SID name. The SID groups ARN types that share an access level.

    For example, S3 objects vs. SSM Parameter have different ARN types - as do S3 objects vs S3 buckets. That's how we
    choose to group them.

    Arguments:
        service: `ssm`
        access_level: `Read`
        resource_type_name: `parameter`
        condition_block: `{"condition_key_string": "ec2:ResourceTag/purpose", "condition_type_string": "StringEquals", "condition_value": "test"}`

    Returns:
        String: A string like `SsmReadParameter`
    """
    # Sanitize the resource_type_name; otherwise we hit some list conversion
    # errors
    resource_type_name = re.sub(SANITIZE_NAME_PATTERN, "", resource_type_name)
    # Also remove the space from the Access level, if applicable. This only
    # applies for "Permissions management"
    access_level = re.sub(SANITIZE_NAME_PATTERN, "", access_level)
    sid_namespace_prefix = (
        capitalize_first_character(strip_special_characters(service))
        + capitalize_first_character(access_level)
        + capitalize_first_character(resource_type_name)
    )

    if condition_block:
        condition_key_namespace = re.sub(SANITIZE_NAME_PATTERN, "", condition_block["condition_key_string"])
        condition_type_namespace = condition_block["condition_type_string"]
        condition_value_namespace = re.sub(SANITIZE_NAME_PATTERN, "", condition_block["condition_value"])
        sid_namespace_condition_suffix = (
            f"{capitalize_first_character(condition_key_namespace)}"
            f"{capitalize_first_character(condition_type_namespace)}"
            f"{capitalize_first_character(condition_value_namespace)}"
        )
        sid_namespace = sid_namespace_prefix + sid_namespace_condition_suffix
    else:
        sid_namespace = sid_namespace_prefix
    return sid_namespace
