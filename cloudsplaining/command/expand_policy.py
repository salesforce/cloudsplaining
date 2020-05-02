"""
Expands the wildcards (*) on an IAM policy file so it is easier for a human to understand. Example: s3:g* vs s3:GetObject, s3:GetObjectAcl, etc.
"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
import json
import click
import click_log
from policy_sentry.analysis.expand import get_expanded_policy

logger = logging.getLogger()
click_log.basic_config(logger)


@click.command(
    short_help="Expand the * Actions in IAM policy files to improve readability"
)
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Path to the JSON policy file.",
)
@click_log.simple_verbosity_option(logger)
def expand_policy(input):  # pylint: disable=redefined-builtin
    """
    Expand the * Actions in IAM policy files to improve readability
    """
    file = input
    with open(file) as json_file:
        logger.debug(f"Opening {file}")
        data = json.load(json_file)
        policy = get_expanded_policy(data)
        print(json.dumps(policy, indent=4))
