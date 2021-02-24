"""
Expands the wildcards (*) on an IAM policy file so it is easier for a human to understand. Example: s3:g* vs s3:GetObject, s3:GetObjectAcl, etc.
"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo rootgit pus
# or https://opensource.org/licenses/BSD-3-Clause
import logging
import json
import click
from policy_sentry.analysis.expand import get_expanded_policy
from cloudsplaining import change_log_level

logger = logging.getLogger(__name__)


@click.command(
    short_help="Expand the * Actions in IAM policy files to improve readability"
)
@click.option(
    "--input-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the JSON policy file.",
)
@click.option(
    "--verbose",
    "-v",
    type=click.Choice(
        ["critical", "error", "warning", "info", "debug"], case_sensitive=False
    ),
)
def expand_policy(input_file, verbose):  # pylint: disable=redefined-builtin
    """
    Expand the * Actions in IAM policy files to improve readability
    """
    if verbose:
        log_level = getattr(logging, verbose.upper())
        change_log_level(log_level)
    with open(input_file) as json_file:
        logger.debug(f"Opening {input_file}")
        data = json.load(json_file)
        policy = get_expanded_policy(data)
        print(json.dumps(policy, indent=4))
