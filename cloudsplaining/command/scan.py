"""
Scan a single account authorization file
"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
import os
import json
from pathlib import Path
import yaml
import click
import click_log
from cloudsplaining.shared.constants import EXCLUSIONS_FILE
from cloudsplaining.shared.validation import check_authorization_details_schema
from cloudsplaining.shared.exclusions import Exclusions, DEFAULT_EXCLUSIONS
from cloudsplaining.scan.authorization_details import AuthorizationDetails
from cloudsplaining.output.html_report import generate_html_report
from cloudsplaining.output.data_file import write_results_data_file

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command(
    short_help="Scan a single file containing AWS IAM account authorization details and generate report on "
    "IAM security posture. "
)
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Path of IAM account authorization details file",
)
@click.option(
    "--exclusions-file",
    help="A yaml file containing a list of policy names to exclude from the scan.",
    type=click.Path(exists=True),
    required=False,
    default=EXCLUSIONS_FILE,
)
@click.option(
    "--output",
    required=False,
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Output directory.",
)
@click.option(
    "--all-access-levels",
    required=False,
    default=False,
    is_flag=True,
    help="Include 'read' or 'list' actions in the results. Defaults to 'modify' only actions",
)
@click.option(
    "--skip-open-report",
    required=False,
    default=False,
    is_flag=True,
    help="Don't open the HTML report in the web browser after creating. "
    "This helps when running the report in automation.",
)
@click_log.simple_verbosity_option()
# pylint: disable=redefined-builtin
def scan(
    input, exclusions_file, output, all_access_levels, skip_open_report
):  # pragma: no cover
    """
    Given the path to account authorization details files and the exclusions config file, scan all inline and
    managed policies in the account to identify actions that do not leverage resource constraints.
    """
    if exclusions_file:
        # Get the exclusions configuration
        with open(exclusions_file, "r") as yaml_file:
            try:
                exclusions_cfg = yaml.safe_load(yaml_file)
            except yaml.YAMLError as exc:
                logger.critical(exc)
        exclusions = Exclusions(exclusions_cfg)
    else:
        exclusions = DEFAULT_EXCLUSIONS

    if os.path.isfile(input):
        scan_account_authorization_file(
            input, exclusions, output, all_access_levels, skip_open_report
        )
    if os.path.isdir(input):
        logger.info(
            "The path given is a directory. Scanning for account authorization files and generating report."
        )
        input_files = get_authorization_files_in_directory(input)
        for file in input_files:
            logger.info(f"Scanning file: {file}")
            scan_account_authorization_file(
                file, exclusions, output, all_access_levels, skip_open_report
            )


def scan_account_authorization_file(
    input_file, exclusions, output, all_access_levels, skip_open_report
):  # pragma: no cover
    """
    Given the path to account authorization details files and the exclusions config file, scan all inline and
    managed policies in the account to identify actions that do not leverage resource constraints.
    """
    with open(input_file) as f:
        contents = f.read()
        account_authorization_details_cfg = json.loads(contents)
        check_authorization_details_schema(account_authorization_details_cfg)

    # Scan authorization details. Defaults to modify-only permissions
    if all_access_levels:
        logger.debug(
            "--all-access-levels selected. Identifying all actions that are not leveraging resource "
            "constraints..."
        )
        authorization_details = AuthorizationDetails(account_authorization_details_cfg)
        results = authorization_details.missing_resource_constraints(
            exclusions, modify_only=False
        )
    else:
        logger.debug(
            "--all-access-levels NOT selected. Identifying modify-only actions that are not leveraging "
            "resource constraints..."
        )
        authorization_details = AuthorizationDetails(account_authorization_details_cfg)
        results = authorization_details.missing_resource_constraints(
            exclusions, modify_only=True
        )

    principal_policy_mapping = authorization_details.principal_policy_mapping
    # For the IAM Principals tab, add on risk stats per principal
    for principal_policy_entry in principal_policy_mapping:
        for finding in results:
            if principal_policy_entry.get("PolicyName").lower() == finding.get("PolicyName").lower():
                principal_policy_entry["Actions"] = len(finding["Actions"])
                principal_policy_entry["PrivilegeEscalation"] = len(
                    finding["PrivilegeEscalation"]
                )
                principal_policy_entry["DataExfiltrationActions"] = len(
                    finding["DataExfiltrationActions"]
                )
                principal_policy_entry["PermissionsManagementActions"] = len(
                    finding["PermissionsManagementActions"]
                )
                principal_name = principal_policy_entry["Principal"]
                # Customer Managed Policies
                if finding.get("Type") == "Policy" and finding.get("ManagedBy") == "Customer" and principal_policy_entry.get("Type") != "Policy":
                    if "Principals" not in finding:
                        finding["Principals"] = [principal_name]
                    else:
                        if principal_name not in finding["Principals"]:
                            finding["Principals"].append(principal_name)

                # AWS Managed Policies
                if finding.get("Type") == "Policy" and finding.get("ManagedBy") == "AWS":
                    if "Principals" not in finding:
                        finding["Principals"] = [principal_name]
                    else:
                        if principal_name not in finding["Principals"]:
                            finding["Principals"].append(principal_name)

    account_name = Path(input_file).stem

    # Lazy method to get an account ID
    account_id = None
    for item in results:
        if item["ManagedBy"] == "Customer":
            account_id = item["AccountID"]
            break

    # HTML report
    output_directory = output

    # Account metadata
    account_metadata = {
        "account_name": account_name,
        "account_id": account_id,
        "customer_managed_policies": len(
            authorization_details.customer_managed_policies_in_use
        ),
        "aws_managed_policies": len(authorization_details.aws_managed_policies_in_use),
    }

    # Raw data file
    raw_data_file = os.path.join(output, f"iam-results-{account_name}.json")
    raw_data_filepath = write_results_data_file(results, raw_data_file)
    print(f"Raw data file saved: {str(raw_data_filepath)}")

    # Principal policy mapping
    principal_policy_mapping_file = os.path.join(
        output, f"iam-principals-{account_name}.json"
    )
    principal_policy_mapping_filepath = write_results_data_file(
        principal_policy_mapping, principal_policy_mapping_file
    )
    print(f"Principals data file saved: {str(principal_policy_mapping_filepath)}")

    print("Creating the HTML Report")
    generate_html_report(
        account_metadata,
        results,
        principal_policy_mapping,
        output_directory,
        exclusions.config,
        skip_open_report=skip_open_report,
    )


def get_authorization_files_in_directory(directory):  # pragma: no cover
    """Get a list of download-account-authorization-files in a directory"""
    file_list = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]
    file_list_with_full_path = []
    for file in file_list:
        if file.endswith(".json"):
            file_list_with_full_path.append(
                os.path.abspath(os.path.join(directory, file))
            )
    new_file_list = []
    for file in file_list_with_full_path:
        with open(file) as f:
            contents = f.read()
        account_authorization_details_cfg = json.loads(contents)
        valid_schema = check_authorization_details_schema(
            account_authorization_details_cfg
        )
        if valid_schema:
            new_file_list.append(file)
    return new_file_list
