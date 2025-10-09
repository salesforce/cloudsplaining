#! /usr/bin/env python
"""
Policy Sentry is a tool for generating least-privilege IAM Policies.
"""

import click

from policy_sentry import command
from policy_sentry.bin.version import __version__


@click.group()
@click.version_option(version=__version__)
def policy_sentry() -> None:
    """
    Policy Sentry is a tool for generating least-privilege IAM Policies.
    """


policy_sentry.add_command(command.initialize.initialize_command)
policy_sentry.add_command(command.write_policy.write_policy)
policy_sentry.add_command(command.create_template.create_template)
policy_sentry.add_command(command.query.query)


def main() -> None:
    """Policy Sentry is a tool for generating least-privilege IAM Policies."""
    policy_sentry()


if __name__ == "__main__":
    main()
