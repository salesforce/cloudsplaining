"""
Create YML Template files for the exclusions template command.
This way, users don't have to remember exactly how to phrase the yaml files, since this command creates it for them.
"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import os
from pathlib import Path
import logging
import click
from cloudsplaining.shared.constants import MULTI_ACCOUNT_CONFIG_TEMPLATE
from cloudsplaining import set_log_level
from cloudsplaining.shared import utils

logger = logging.getLogger(__name__)
OK_GREEN = "\033[92m"
END = "\033[0m"


@click.command(
    context_settings=dict(max_content_width=160),
    short_help="Creates a YML file to be used for multi-account scanning",
)
@click.option(
    "--output-file",
    "-o",
    "output_file",
    type=click.Path(exists=False),
    default=os.path.join(os.getcwd(), "multi-account-config.yml"),
    required=True,
    help="Relative path to output file where we want to store the multi account config template.",
)
@click.option(
    "-v", "--verbose", "verbosity", count=True,
)
def create_multi_account_config_file(output_file: str, verbosity: int) -> None:
    """
    Creates a YML file to be used as a multi-account config template, so users can scan many different accounts.
    """
    set_log_level(verbosity)

    filename = Path(output_file).resolve()

    if filename.exists():
        logger.debug(
            "%s exists. Removing the file and replacing its contents.", filename
        )
        filename.unlink()

    with open(filename, "a") as file_obj:
        for line in MULTI_ACCOUNT_CONFIG_TEMPLATE:
            file_obj.write(line)
    utils.print_green(
        f"Success! Multi-account config file written to: {os.path.relpath(filename)}"
    )
    print(
        f"\nMake sure you edit the {os.path.relpath(filename)} file and then run the scan-multi-account command, as shown below."
    )
    print(
        f"\n\tcloudsplaining scan-multi-account --exclusions-file exclusions.yml -c {os.path.relpath(filename)} -o ./"
    )
