"""
Scan a single account authorization file
"""
import logging
import os
import json
from pathlib import Path
import yaml
import click
import click_log
from cloudsplaining.shared.constants import EXCLUSIONS_FILE
from cloudsplaining.shared.validation import (
    check_exclusions_schema,
    check_authorization_details_schema,
)
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
    "--file",
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
@click_log.simple_verbosity_option()
def scan(file, exclusions_file, output, all_access_levels):
    """
    Given the path to account authorization details files and the exclusions config file, scan all inline and
    managed policies in the account to identify actions that do not leverage resource constraints.
    """
    if exclusions_file:
        with open(exclusions_file, "r") as yaml_file:
            try:
                exclusions_cfg = yaml.safe_load(yaml_file)
            except yaml.YAMLError as exc:
                logger.critical(exc)
        check_exclusions_schema(exclusions_cfg)

    with open(file) as f:
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
        results = authorization_details.missing_resource_constraints(exclusions_cfg, modify_only=False)
    else:
        logger.debug(
            "--all-access-levels NOT selected. Identifying modify-only actions that are not leveraging "
            "resource constraints..."
        )
        authorization_details = AuthorizationDetails(account_authorization_details_cfg)
        results = authorization_details.missing_resource_constraints(exclusions_cfg, modify_only=True)

    account_name = Path(file).stem

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
        "customer_managed_policies": len(authorization_details.customer_managed_policies_in_use),
        "aws_managed_policies": len(authorization_details.aws_managed_policies_in_use)
    }

    # Raw data file
    raw_data_file = os.path.join(output, f"iam-results-{account_name}.json")
    raw_data_filepath = write_results_data_file(results, raw_data_file)
    print(f"Raw data file saved: {str(raw_data_filepath)}")

    print("Creating the HTML Report")
    generate_html_report(account_metadata, results, output_directory, exclusions_cfg)
