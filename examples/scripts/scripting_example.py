#!/usr/bin/env python
"""
Demonstrates how to use Cloudsplaining as a library. Using this method you can get the HTML report back as a string.
"""
from cloudsplaining.command.scan import scan_account_authorization_details
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS
import click
import json


@click.command(
    short_help="Shows how to use Cloudsplaining's scan_account_authorization_details method to get the HTML results as a string"
)
@click.option(
    '--file',
    required=True,
    type=click.Path(exists=True),
    help='Path to the account authorization details JSON file.'
)
def scripting_example(file):
    with open(file) as f:
        contents = f.read()
        account_authorization_details_cfg = json.loads(contents)
    rendered_html_report = scan_account_authorization_details(
        account_authorization_details_cfg, DEFAULT_EXCLUSIONS, account_name="example"
    )
    print(rendered_html_report)


if __name__ == '__main__':
    scripting_example()
