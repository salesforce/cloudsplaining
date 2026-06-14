#! /usr/bin/env python
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
"""
Cloudsplaining is an AWS IAM Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report.
"""

import click

from cloudsplaining import command
from cloudsplaining.bin.version import __version__
from cloudsplaining.shared.exclusions import set_exclusion_output


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cloudsplaining(ctx: click.Context) -> None:
    """
    Cloudsplaining is an AWS IAM Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report.
    """
    # Surface exclusion-match messages on stdout for the CLI (historical behavior), then
    # restore the prior value when the Click context tears down so an in-process CLI run
    # does not leak printing state into later library use.
    previous = set_exclusion_output(True)
    ctx.call_on_close(lambda: set_exclusion_output(previous))


cloudsplaining.add_command(command.create_exclusions_file.create_exclusions_file)
cloudsplaining.add_command(command.create_multi_account_config_file.create_multi_account_config_file)
cloudsplaining.add_command(command.expand_policy.expand_policy)
cloudsplaining.add_command(command.scan.scan)
cloudsplaining.add_command(command.scan_multi_account.scan_multi_account)
cloudsplaining.add_command(command.scan_policy_file.scan_policy_file)
cloudsplaining.add_command(command.download.download)


def main() -> None:
    """Cloudsplaining is an AWS IAM Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report."""
    cloudsplaining()


if __name__ == "__main__":
    cloudsplaining()
