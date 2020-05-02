"""
Scan a single policy file to identify missing resource constraints.
"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
import json
from pathlib import Path
import yaml
import click
import click_log
from cloudsplaining.output.findings import Findings, Finding
from cloudsplaining.shared.constants import EXCLUSIONS_FILE, DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.validation import check_exclusions_schema
from cloudsplaining.shared.exclusions import is_name_excluded

logger = logging.getLogger(__name__)
click_log.basic_config(logger)
BOLD = "\033[1m"
RED = "\033[91m"
END = "\033[0m"


@click.command(
    short_help="Scan a single policy file to identify identify missing resource constraints."
)
@click.option(
    "--file",
    type=click.Path(exists=True),
    required=True,
    help="Path of to the IAM policy file.",
)
@click.option(
    "--exclusions-file",
    help="A yaml file containing a list of actions to ignore when scanning.",
    type=click.Path(exists=True),
    required=False,
    default=EXCLUSIONS_FILE,
)
@click.option(
    "--high-priority-only",
    required=False,
    default=False,
    is_flag=True,
    help="If issues are found, only print the high priority risks"
    " (Resource Exposure, Privilege Escalation, Data Exfiltration). This can help with prioritization.",
)
@click_log.simple_verbosity_option(logger)
def scan_policy_file(file, exclusions_file, high_priority_only):
    """Scan a single policy file to identify missing resource constraints."""

    # Get the exclusions configuration
    with open(exclusions_file, "r") as yaml_file:
        try:
            exclusions_cfg = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            logger.critical(exc)
    check_exclusions_schema(exclusions_cfg)

    # Get the Policy
    with open(file) as json_file:
        logger.debug(f"Opening {file}")
        policy = json.load(json_file)

    policy_name = Path(file).stem

    # Run the scan and get the raw data.
    results = scan_policy(policy, policy_name, exclusions_cfg)

    # There will only be one finding in the results but it is in a list.
    for finding in results:
        if finding["PrivilegeEscalation"]:
            print(f"{RED}Issue found: Privilege Escalation{END}")
            for item in finding["PrivilegeEscalation"]:
                print(f"- Method: {item['type']}")
                print(f"  Actions: {', '.join(item['PrivilegeEscalation'])}\n")
        if finding["DataExfiltrationActions"]:
            print(f"{RED}Issue found: Data Exfiltration{END}")
            print(
                f"{BOLD}Actions{END}: {', '.join(finding['DataExfiltrationActions'])}\n"
            )
        if finding["PermissionsManagementActions"]:
            print(f"{RED}Issue found: Resource Exposure{END}")
            print(
                f"{BOLD}Actions{END}: {', '.join(finding['PermissionsManagementActions'])}\n"
            )
        if not high_priority_only:
            print(f"{RED}Issue found: Unrestricted Infrastructure Modification{END}")
            print(f"{BOLD}Actions{END}: {', '.join(finding['Actions'])}")


def scan_policy(policy_json, policy_name, exclusions_cfg=DEFAULT_EXCLUSIONS_CONFIG):
    """
    Scan a policy document for missing resource constraints.

    :param policy_json: The AWS IAM policy document.
    :param exclusions_cfg: Defaults to the embedded exclusions file, which has no effect here.
    :param policy_name: The name of the IAM policy. Defaults to the filename when used from command line.
    :return:
    """
    policy_document = PolicyDocument(policy_json)
    actions_missing_resource_constraints = []

    # EXCLUDED ACTIONS - actions to exclude if they are false positives
    excluded_actions = exclusions_cfg.get("exclude-actions", None)
    if excluded_actions == [""]:
        excluded_actions = None

    # convert to lowercase for comparison purposes
    # some weird if/else logic to reduce loops and improve performance slightly
    if excluded_actions:
        excluded_actions = [x.lower() for x in excluded_actions]

    always_include_actions = exclusions_cfg.get("include-actions")
    findings = Findings()

    for statement in policy_document.statements:
        if statement.effect == "Allow":
            actions_missing_resource_constraints.extend(
                statement.missing_resource_constraints_for_modify_actions(
                    always_include_actions
                )
            )
    if actions_missing_resource_constraints:
        results_placeholder = []
        for action in actions_missing_resource_constraints:
            if excluded_actions:
                if not is_name_excluded(action.lower(), excluded_actions):
                    results_placeholder.append(action)
            else:
                results_placeholder.append(action)
        actions_missing_resource_constraints = list(
            dict.fromkeys(results_placeholder)
        )  # remove duplicates
        actions_missing_resource_constraints.sort()
        finding = Finding(
            policy_name=policy_name,
            arn=policy_name,
            actions=actions_missing_resource_constraints,
            policy_document=policy_document,
        )
        findings.add(finding)
    return findings.json
