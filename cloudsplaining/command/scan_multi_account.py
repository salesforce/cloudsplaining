"""Scan multiple AWS accounts via AssumeRole"""
import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml
import click
from click_option_group import optgroup
from cloudsplaining.shared.constants import EXCLUSIONS_FILE
from cloudsplaining.command.download import get_account_authorization_details
from cloudsplaining import set_log_level
from cloudsplaining.shared.exclusions import Exclusions, DEFAULT_EXCLUSIONS
from cloudsplaining.shared import utils, aws_login
from cloudsplaining.shared.validation import check_authorization_details_schema
from cloudsplaining.scan.authorization_details import AuthorizationDetails
from cloudsplaining.output.report import HTMLReport

logger = logging.getLogger(__name__)
OK_GREEN = "\033[92m"
END = "\033[0m"


class MultiAccountConfig:
    """Handle the YAML file that parses the Multi-account config"""

    def __init__(self, config: Dict[str, Any], role_name: str) -> None:
        # self.config_file = config_file
        self.config = config
        self.role_name = role_name
        self.accounts = self._accounts()

    def _accounts(self) -> Dict[str, str]:
        accounts: Dict[str, str] = self.config.get("accounts", None)
        if not accounts:
            raise Exception(
                "Please supply a list of accounts in the multi-account config file"
            )
        return accounts


@click.command(short_help="Scan multiple AWS Accounts using a config file")
@click.option(
    "--config",
    "-c",
    "config_file",
    type=click.Path(exists=True),
    required=True,
    help="Path of the multi-account config file",
)
@click.option(
    "--profile",
    "-p",
    "profile",
    type=str,
    required=False,
    help="Specify the AWS IAM profile.",
    envvar="AWS_PROFILE",
)
@click.option(
    "--role-name",
    "-r",
    "role_name",
    type=str,
    required=True,
    help="The name of the IAM role to assume in target accounts. Must be the same name in all target accounts.",
)
@click.option(
    "--exclusions-file",
    "-e",
    "exclusions_file",
    help="A yaml file containing a list of policy names to exclude from the scan.",
    type=click.Path(exists=True),
    required=False,
    default=EXCLUSIONS_FILE,
)
@optgroup.group(
    "Output Target Options", help="",
)
@optgroup.option(
    "--output-directory",
    "-o",
    "output_directory",
    type=click.Path(exists=True),
    help="Output directory. Supply this and/or --bucket.",
)
@optgroup.option(
    "--output-bucket",
    "-b",
    "output_bucket",
    type=str,
    help="The S3 bucket to save the results. Supply this and/or --output-directory.",
)
@optgroup.group(
    "Other Options", help="",
)
@optgroup.option(
    "--write-data-file",
    "-w",
    is_flag=True,
    required=False,
    default=False,
    help="Save the cloudsplaining JSON-formatted data results.",
)
@click.option(
    "-v", "--verbose", "verbosity", count=True,
)
def scan_multi_account(
    config_file: str,
    profile: str,
    role_name: str,
    exclusions_file: str,
    output_directory: str,
    output_bucket: str,
    write_data_file: bool,
    verbosity: int,
) -> None:
    """Scan multiple accounts via AssumeRole"""
    set_log_level(verbosity)

    # Read the config file from the user
    with open(config_file, "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    # Use the following lines to run this in a library
    multi_account_config = MultiAccountConfig(config=config, role_name=role_name)
    exclusions = get_exclusions(exclusions_file=exclusions_file)
    scan_accounts(
        multi_account_config=multi_account_config,
        exclusions=exclusions,
        profile=profile,
        role_name=role_name,
        output_directory=output_directory,
        output_bucket=output_bucket,
        write_data_file=write_data_file,
    )


def scan_accounts(
    multi_account_config: MultiAccountConfig,
    exclusions: Exclusions,
    role_name: str,
    write_data_file: bool,
    profile: Optional[str] = None,
    output_directory: Optional[str] = None,
    output_bucket: Optional[str] = None,
) -> None:
    """Use this method as a library to scan multiple accounts"""
    # TODO: Speed improvements? Multithreading? This currently runs sequentially.
    for target_account_name, target_account_id in multi_account_config.accounts.items():
        print(
            f"{OK_GREEN}Scanning account: {target_account_name} (ID: {target_account_id}){END}"
        )
        results = scan_account(
            target_account_id=target_account_id,
            target_role_name=role_name,
            exclusions=exclusions,
            profile=profile,
        )
        html_report = HTMLReport(
            account_id=target_account_id,
            account_name=target_account_name,
            results=results,
            minimize=True,
        )
        rendered_report = html_report.get_html_report()
        if not output_directory and not output_bucket:
            raise Exception(
                "Please supply --output-bucket and/or --output-directory as arguments."
            )
        if output_bucket:
            s3 = aws_login.get_boto3_resource(service="s3", profile=profile)
            # Write the HTML file
            output_file = f"{target_account_name}.html"
            s3.Object(output_bucket, output_file).put(
                ACL="bucket-owner-full-control", Body=rendered_report
            )
            utils.print_green(
                f"Saved the HTML report to: s3://{output_bucket}/{output_file}"
            )
            # Write the JSON data file
            if write_data_file:
                output_file = f"{target_account_name}.json"
                body = json.dumps(results, sort_keys=True, default=str, indent=4)
                s3.Object(output_bucket, output_file).put(
                    ACL="bucket-owner-full-control", Body=body
                )
                utils.print_green(
                    f"Saved the JSON data to: s3://{output_bucket}/{output_file}"
                )
        if output_directory:
            # Write the HTML file
            html_output_file = Path(output_directory) / f"{target_account_name}.html"
            html_output_file.write_text(rendered_report)
            utils.print_green(
                f"Saved the HTML report to: {os.path.relpath(html_output_file)}"
            )
            # Write the JSON data file
            if write_data_file:
                results_data_file = os.path.join(
                    output_directory, f"{target_account_name}.json"
                )
                results_data_filepath = utils.write_results_data_file(
                    results, results_data_file
                )
                utils.print_green(
                    f"Saved the JSON data to: {os.path.relpath(results_data_filepath)}"
                )


def scan_account(
    target_account_id: str,
    target_role_name: str,
    exclusions: Exclusions,
    profile: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """Scan a target account in one shot"""
    account_authorization_details = download_account_authorization_details(
        target_account_id=target_account_id,
        target_role_name=target_role_name,
        profile=profile,
    )
    check_authorization_details_schema(account_authorization_details)
    authorization_details = AuthorizationDetails(account_authorization_details, exclusions)
    results = authorization_details.results
    return results


def download_account_authorization_details(
    target_account_id: str, target_role_name: str, profile: Optional[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Download the account authorization details from a target account"""
    (
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
    ) = aws_login.get_target_account_credentials(
        target_account_id=target_account_id,
        target_account_role_name=target_role_name,
        profile=profile,
    )
    session_data = dict(
        region_name="us-east-1",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )
    include_non_default_policy_versions = False
    authorization_details = get_account_authorization_details(
        session_data, include_non_default_policy_versions
    )
    return authorization_details


def get_exclusions(exclusions_file: Optional[str] = None) -> Exclusions:
    """Get the exclusions configuration from a file"""
    # Get the exclusions configuration
    if exclusions_file:
        with open(exclusions_file, "r") as yaml_file:
            try:
                exclusions_cfg = yaml.safe_load(yaml_file)
            except yaml.YAMLError as exc:
                logger.critical(exc)
        exclusions = Exclusions(exclusions_cfg)
    else:
        exclusions = DEFAULT_EXCLUSIONS
    return exclusions
