"""
Create YML Template files for the exclusions template command.
This way, users don't have to remember exactly how to phrase the yaml files, since this command creates it for them.
"""

# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
import os

import click

from cloudsplaining import set_log_level
from cloudsplaining.shared import utils
from cloudsplaining.shared.constants import EXCLUSIONS_TEMPLATE

logger = logging.getLogger(__name__)


@click.command(
    context_settings=dict(max_content_width=160),
    short_help="Creates a YML file to be used as a custom exclusions template",
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(exists=False),
    default=os.path.join(os.getcwd(), "exclusions.yml"),
    required=True,
    help="Relative path to output file where we want to store the exclusions template.",
)
@click.option("--verbose", "-v", "verbosity", count=True)
def create_exclusions_file(output_file: str, verbosity: int) -> None:
    """
    Creates a YML file to be used as a custom exclusions template,
    so users can fill out the fields without needing to look up the required format.
    """
    set_log_level(verbosity)

    with open(output_file, "a", encoding="utf-8") as file_obj:
        for line in EXCLUSIONS_TEMPLATE:
            file_obj.write(line)
    utils.print_green(f"Success! Exclusions template file written to: {output_file}")
    print(
        "Make sure you download your account authorization details before running the scan."
        "Set your AWS access keys as environment variables then run: "
    )
    print("\tcloudsplaining download")
    print("You can use this with the scan command as shown below: ")
    print("\tcloudsplaining scan --exclusions-file exclusions.yml --input-file default.json")
