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
from typing import Dict, Any, List

import yaml
import click
from policy_sentry.util.arns import get_account_from_arn
from cloudsplaining.shared.constants import EXCLUSIONS_FILE
from cloudsplaining.shared.validation import check_authorization_details_schema
from cloudsplaining.shared.exclusions import Exclusions, DEFAULT_EXCLUSIONS
from cloudsplaining.scan.authorization_details import AuthorizationDetails
from cloudsplaining.shared.utils import write_results_data_file
from cloudsplaining.output.report import HTMLReport
from cloudsplaining import set_log_level

logger = logging.getLogger(__name__)


@click.command(
    short_help="Scan a single file containing AWS IAM account authorization details and generate report on "
    "IAM security posture. "
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    required=True,
    help="Path of IAM account authorization details file",
)
@click.option(
    "--exclusions-file",
    "-e",
    help="A yaml file containing a list of policy names to exclude from the scan.",
    type=click.Path(exists=True),
    required=False,
    default=EXCLUSIONS_FILE,
)
@click.option(
    "--output",
    "-o",
    required=False,
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Output directory.",
)
@click.option(
    "--skip-open-report",
    "-s",
    required=False,
    default=False,
    is_flag=True,
    help="Don't open the HTML report in the web browser after creating. "
    "This helps when running the report in automation.",
)
@click.option(
    "--minimize",
    "-m",
    required=False,
    default=False,
    is_flag=True,
    help="Reduce the size of the HTML Report by pulling the Cloudsplaining Javascript code over the internet.",
)
@click.option("--verbose", "-v", "verbosity", count=True)
def scan(
    input_file: str,
    exclusions_file: str,
    output: str,
    skip_open_report: bool,
    minimize: bool,
    verbosity: int,
) -> None:  # pragma: no cover
    """
    Given the path to account authorization details files and the exclusions config file, scan all inline and
    managed policies in the account to identify actions that do not leverage resource constraints.
    """
    set_log_level(verbosity)

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

    if os.path.isfile(input_file):
        account_name = Path(input_file).stem
        with open(input_file) as f:
            contents = f.read()
            account_authorization_details_cfg = json.loads(contents)
        rendered_html_report = scan_account_authorization_details(
            account_authorization_details_cfg,
            exclusions,
            account_name,
            output,
            write_data_files=True,
            minimize=minimize,
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

    if os.path.isdir(input_file):
        logger.info(
            "The path given is a directory. Scanning for account authorization files and generating report."
        )
        input_files = get_authorization_files_in_directory(input_file)
        for file in input_files:
            logger.info(f"Scanning file: {file}")
            with open(file) as f:
                contents = f.read()
                account_authorization_details_cfg = json.loads(contents)

            account_name = Path(file).stem
            # Scan the Account Authorization Details config
            rendered_html_report = scan_account_authorization_details(
                account_authorization_details_cfg,
                exclusions,
                account_name,
                output,
                write_data_files=True,
                minimize=minimize,
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
    account_authorization_details_cfg: Dict[str, Any],
    exclusions: Exclusions,
    account_name: str = "default",
    output_directory: str = os.getcwd(),
    write_data_files: bool = False,
    minimize: bool = False,
) -> str:  # pragma: no cover
    """
    Given the path to account authorization details files and the exclusions config file, scan all inline and
    managed policies in the account to identify actions that do not leverage resource constraints.
    """

    logger.debug(
        "Identifying modify-only actions that are not leveraging "
        "resource constraints..."
    )
    check_authorization_details_schema(account_authorization_details_cfg)
    authorization_details = AuthorizationDetails(
        account_authorization_details_cfg, exclusions
    )
    results = authorization_details.results

    # Lazy method to get an account ID
    account_id = ""
    for role in results.get("roles", []):
        if "arn:aws:iam::aws:" not in results["roles"][role]["arn"]:
            account_id = get_account_from_arn(results["roles"][role]["arn"])
            break

    html_report = HTMLReport(
        account_id=account_id,
        account_name=account_name,
        results=results,
        minimize=minimize,
    )
    rendered_report = html_report.get_html_report()

    # Raw data file
    if write_data_files:
        if output_directory is None:
            output_directory = os.getcwd()

        results_data_file = os.path.join(
            output_directory, f"iam-results-{account_name}.json"
        )
        results_data_filepath = write_results_data_file(
            authorization_details.results, results_data_file
        )
        print(f"Results data saved: {results_data_filepath}")

        findings_data_file = os.path.join(
            output_directory, f"iam-findings-{account_name}.json"
        )
        findings_data_filepath = write_results_data_file(results, findings_data_file)
        print(f"Findings data file saved: {findings_data_filepath}")

    return rendered_report


def get_authorization_files_in_directory(
    directory: str,
) -> List[str]:  # pragma: no cover
    """Get a list of download-account-authorization-files in a directory"""
    file_list_with_full_path = [
        file.absolute() for file in Path(directory).glob("*.json")
    ]

    new_file_list = []
    for file in file_list_with_full_path:
        contents = file.read_text()
        account_authorization_details_cfg = json.loads(contents)
        valid_schema = check_authorization_details_schema(
            account_authorization_details_cfg
        )
        if valid_schema:
            new_file_list.append(str(file))
    return new_file_list
