"""
Scan a single policy file to identify missing resource constraints.
"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import sys
import logging
import json
from typing import Dict, Any, List

import yaml
import click
from cloudsplaining.shared.constants import EXCLUSIONS_FILE, DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.exclusions import Exclusions
from cloudsplaining.output.policy_finding import PolicyFinding
from cloudsplaining import set_log_level

logger = logging.getLogger(__name__)
BOLD = "\033[1m"
RED = "\033[91m"
END = "\033[0m"


@click.command(
    short_help="Scan a single policy file to identify identify missing resource constraints."
)
@click.option("-i", "--input-file", type=str, help="Path of the IAM policy file to evaluate.")
@click.option("-e", "--exclusions-file", help="A yaml file containing a list of actions to ignore when scanning.", type=click.Path(exists=True), required=False, default=EXCLUSIONS_FILE)
@click.option("--high-priority-only", required=False, default=False, is_flag=True, help="If issues are found, only print the high priority risks (Resource Exposure, Privilege Escalation, Data Exfiltration). This can help with prioritization.")
@click.option("-aR", "--flag-all-risky-actions", is_flag=True, help="Flag all risky actions, regardless of whether resource ARN constraints or conditions are used.")
@click.option("--verbose", "-v", "verbosity", count=True)
# pylint: disable=redefined-builtin
def scan_policy_file(
    input_file: str, exclusions_file: str, high_priority_only: bool, flag_all_risky_actions: bool, verbosity: int
) -> None:  # pragma: no cover
    """Scan a single policy file to identify missing resource constraints."""
    set_log_level(verbosity)
    if input_file:
        # Get the Policy
        with open(input_file) as json_file:
            logger.debug(f"Opening {input_file}")
            policy = json.load(json_file)
    # If a file is not provided, it should be supplied via STDIN
    else:
        try:
            policy = json.load(sys.stdin)
        except json.decoder.JSONDecodeError as j_e:
            logger.critical(j_e)
            sys.exit()

    # Get the exclusions configuration from the file
    with open(exclusions_file, "r") as yaml_file:
        try:
            exclusions_cfg = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            logger.critical(exc)

    if flag_all_risky_actions:
        flag_conditional_statements = True
        flag_resource_arn_statements = True
    else:
        flag_conditional_statements = False
        flag_resource_arn_statements = False

    # Run the scan and get the raw data.
    results = scan_policy(policy, exclusions_cfg, flag_resource_arn_statements=flag_resource_arn_statements, flag_conditional_statements=flag_conditional_statements)

    # There will only be one finding in the results but it is in a list.
    results_exist = 0
    if results:
        # Privilege Escalation
        if results.get("PrivilegeEscalation"):
            print(
                f"{RED}Potential Issue found: Policy is capable of Privilege Escalation{END}"
            )
            results_exist += 1
            for item in results.get("PrivilegeEscalation", []):
                print(f"- Method: {item.get('type')}")
                print(f"  Actions: {', '.join(item.get('actions', []))}\n")

        # Data Exfiltration
        if results.get("DataExfiltration"):
            results_exist += 1
            print(
                f"{RED}Potential Issue found: Policy is capable of Data Exfiltration{END}"
            )
            print(
                f"{BOLD}Actions{END}: {', '.join(results.get('DataExfiltration', []))}\n"
            )

        # Resource Exposure
        if results.get("ResourceExposure"):
            results_exist += 1
            print(
                f"{RED}Potential Issue found: Policy is capable of Resource Exposure{END}"
            )
            print(
                f"{BOLD}Actions{END}: {', '.join(results.get('ResourceExposure', []))}\n"
            )

        # Service Wildcard
        if results.get("ServiceWildcard"):
            results_exist += 1
            print(
                f"{RED}Potential Issue found: Policy allows ALL Actions from a service (like service:*){END}"
            )
            print(
                f"{BOLD}Actions{END}: {', '.join(results.get('ServiceWildcard', []))}\n"
            )

        # Credentials Exposure
        if results.get("CredentialsExposure"):
            results_exist += 1
            print(
                f"{RED}Potential Issue found: Policy allows actions that return credentials{END}"
            )
            print(
                f"{BOLD}Actions{END}: {', '.join(results.get('CredentialsExposure', []))}\n"
            )

        if not high_priority_only:
            if results.get("InfrastructureModification"):
                # Infrastructure Modification
                results_exist += 1
                print(
                    f"{RED}Potential Issue found: Policy is capable of Unrestricted Infrastructure Modification{END}"
                )
                print(
                    f"{BOLD}Actions{END}: {', '.join(results.get('InfrastructureModification', []))}"
                )

        if results_exist == 0:
            print("There were no results found.")
    else:
        print("There were no results found.")


def scan_policy(
    policy_json: Dict[str, Any],
    exclusions_config: Dict[str, List[str]] = DEFAULT_EXCLUSIONS_CONFIG,
    flag_conditional_statements: bool = False,
    flag_resource_arn_statements: bool = False,
) -> Dict[str, Any]:
    """
    Scan a policy document for missing resource constraints.

    :param policy_json: Dictionary containing the IAM policy.
    :param exclusions_config: Exclusions configuration. If none, just send an empty dictionary. Defaults to the contents of cloudsplaining.shared.default-exclusions.yml
    :param flag_resource_arn_statements:
    :param flag_conditional_statements:
    :return:
    """
    exclusions = Exclusions(exclusions_config)
    policy_document = PolicyDocument(policy_json, exclusions=exclusions, flag_resource_arn_statements=flag_resource_arn_statements, flag_conditional_statements=flag_conditional_statements)
    policy_finding = PolicyFinding(policy_document, exclusions)
    return policy_finding.results
