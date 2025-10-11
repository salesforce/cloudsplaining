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
from pathlib import Path

import click

from cloudsplaining import set_log_level
from cloudsplaining.shared import utils
from cloudsplaining.shared.constants import MULTI_ACCOUNT_CONFIG_TEMPLATE

logger = logging.getLogger(__name__)
OK_GREEN = "\033[92m"
END = "\033[0m"


@click.command(
    context_settings={"max_content_width": 160},
    short_help="Creates a YML file to be used for multi-account scanning",
)
@click.option(
    "-o",
    "--output-file",
    "output_file",
    type=click.Path(exists=False),
    default=str(Path.cwd() / "multi-account-config.yml"),
    required=True,
    help="Relative path to output file where we want to store the multi account config template.",
)
@click.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def create_multi_account_config_file(output_file: str, verbosity: int) -> None:
    """
    Creates a YML file to be used as a multi-account config template, so users can scan many different accounts.
    """
    set_log_level(verbosity)

    output_file = Path(output_file)
    if output_file.exists():
        logger.debug("%s exists. Removing the file and replacing its contents.", output_file)
        output_file.unlink()

    with output_file.open("a", encoding="utf-8") as file_obj:
        file_obj.write(MULTI_ACCOUNT_CONFIG_TEMPLATE)

    utils.print_green(f"Success! Multi-account config file written to: {output_file}")
    print(f"\nMake sure you edit the {output_file} file and then run the scan-multi-account command, as shown below.")
    print(f"\n\tcloudsplaining scan-multi-account --exclusions-file exclusions.yml -c {output_file} -o ./")
