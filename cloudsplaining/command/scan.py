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
import webbrowser
import json
from pathlib import Path
import yaml
import click
import click_log
from cloudsplaining.shared.constants import EXCLUSIONS_FILE
from cloudsplaining.shared.validation import check_authorization_details_schema
from cloudsplaining.shared.exclusions import Exclusions, DEFAULT_EXCLUSIONS
from cloudsplaining.scan.authorization_details import AuthorizationDetails
from cloudsplaining.output.triage_worksheet import create_triage_worksheet
from cloudsplaining.output.data_file import write_results_data_file
from cloudsplaining.output.report import HTMLReport

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
    input, exclusions_file, output, skip_open_report
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
        account_name = Path(input).stem
        with open(input) as f:
            contents = f.read()
            account_authorization_details_cfg = json.loads(contents)
        rendered_html_report = scan_account_authorization_details(
            account_authorization_details_cfg, exclusions, account_name, output, write_data_files=True
        )
        html_output_file = os.path.join(output, f"iam-report-{account_name}.html")
        logger.info("Saving the report to %s", html_output_file)
        if os.path.exists(html_output_file):
            os.remove(html_output_file)

        with open(html_output_file, "w") as f:
            f.write(rendered_html_report)

        print(f"Wrote HTML results to: {html_output_file}")

        # Open the report by default
        if not skip_open_report:
            print("Opening the HTML report")
            url = "file://%s" % os.path.abspath(html_output_file)
            webbrowser.open(url, new=2)

    if os.path.isdir(input):
        logger.info(
            "The path given is a directory. Scanning for account authorization files and generating report."
        )
        input_files = get_authorization_files_in_directory(input)
        for file in input_files:
            logger.info(f"Scanning file: {file}")
            with open(file) as f:
                contents = f.read()
                account_authorization_details_cfg = json.loads(contents)

            account_name = Path(file).stem
            # Scan the Account Authorization Details config
            rendered_html_report = scan_account_authorization_details(
                account_authorization_details_cfg, exclusions, account_name, output, write_data_files=True
            )
            html_output_file = os.path.join(output, f"iam-report-{account_name}.html")
            logger.info("Saving the report to %s", html_output_file)
            if os.path.exists(html_output_file):
                os.remove(html_output_file)

            with open(html_output_file, "w") as f:
                f.write(rendered_html_report)

            print(f"Wrote HTML results to: {html_output_file}")

            # Open the report by default
            if not skip_open_report:
                print("Opening the HTML report")
                url = "file://%s" % os.path.abspath(html_output_file)
                webbrowser.open(url, new=2)


def scan_account_authorization_details(
    account_authorization_details_cfg, exclusions, account_name="default", output_directory=None, write_data_files=False
):  # pragma: no cover
    """
    Given the path to account authorization details files and the exclusions config file, scan all inline and
    managed policies in the account to identify actions that do not leverage resource constraints.
    """

    logger.debug(
        "Identifying modify-only actions that are not leveraging "
        "resource constraints..."
    )
    check_authorization_details_schema(account_authorization_details_cfg)
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

    # Lazy method to get an account ID
    account_id = None
    for item in results:
        if item["ManagedBy"] == "Customer":
            account_id = item["AccountID"]
            break

    html_report = HTMLReport(
        account_id=account_id,
        account_name=account_name,
        results=results,
        exclusions_cfg=exclusions,
        principal_policy_mapping=principal_policy_mapping
    )
    rendered_report = html_report.get_html_report()

    # Raw data file
    if write_data_files:
        if output_directory is None:
            output_directory = os.getcwd()

        raw_data_file = os.path.join(output_directory, f"iam-results-{account_name}.json")
        raw_data_filepath = write_results_data_file(results, raw_data_file)
        print(f"Raw data file saved: {str(raw_data_filepath)}")

        # Principal policy mapping
        principal_policy_mapping_file = os.path.join(
            output_directory, f"iam-principals-{account_name}.json"
        )
        principal_policy_mapping_filepath = write_results_data_file(
            principal_policy_mapping, principal_policy_mapping_file
        )
        print(f"Principals data file saved: {str(principal_policy_mapping_filepath)}")

        # Create the CSV triage sheet
        create_triage_worksheet(account_name, results, output_directory)

    return rendered_report


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
