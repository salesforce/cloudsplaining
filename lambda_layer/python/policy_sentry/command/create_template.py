"""
Create YML Template files for the write-policy command.
Users don't have to remember exactly how to phrase the yaml files, so this command creates it for them.
"""

from __future__ import annotations

import logging
from pathlib import Path

import click

from policy_sentry import set_stream_logger
from policy_sentry.writing.template import create_actions_template, create_crud_template

logger = logging.getLogger(__name__)


@click.command(
    context_settings={"max_content_width": 160},
    short_help="Create write-policy YML template files",
)
@click.option(
    "--output-file",
    "-o",
    type=str,
    required=True,
    help="Relative path to output file where we want to store policy_sentry YML files.",
)
@click.option(
    "--template-type",
    "-t",
    type=click.Choice(["actions", "crud"], case_sensitive=False),
    required=True,
    help="Type of write_policy template to create - actions or CRUD. Case insensitive.",
)
@click.option(
    "--verbose",
    "-v",
    type=click.Choice(["critical", "error", "warning", "info", "debug"], case_sensitive=False),
)
def create_template(output_file: str | Path, template_type: str, verbose: str) -> None:
    """
    Writes YML file templates for use in the write-policy
    command, so users can fill out the fields
    without needing to look up the required format.
    """
    if verbose:
        log_level = getattr(logging, verbose.upper())
        set_stream_logger(level=log_level)

    filename = Path(output_file).resolve()
    if template_type == "actions":
        actions_template = create_actions_template()
        with open(filename, "a", encoding="utf-8") as file_obj:
            for line in actions_template:
                file_obj.write(line)

    if template_type == "crud":
        crud_template = create_crud_template()
        with open(filename, "a", encoding="utf-8") as file_obj:
            for line in crud_template:
                file_obj.write(line)

    print(f"write-policy template file written to: {filename}")
