"""
Given a Policy Sentry YML template, write a least-privilege IAM Policy in CRUD mode or Actions mode.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import TYPE_CHECKING, Any

import click
import yaml
from click import Context

from policy_sentry import set_stream_logger
from policy_sentry.util.file import read_yaml_file
from policy_sentry.writing.sid_group import SidGroup

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


# adapted from
# https://stackoverflow.com/questions/40753999/python-click-make-option-value-optional


class RegisterLengthOption(click.Option):
    """Mark this option as getting a _length option"""

    register_length = True


class RegisterLengthOptionHelp(click.Option):
    """Translate help for the hidden _length suffix"""

    def get_help_record(self, ctx: Context) -> tuple[str, str] | None:
        help_text = super().get_help_record(ctx)
        if help_text is None:
            return None

        return (help_text[0].replace("_length ", " "),) + help_text[1:]


class RegisterMinimizeLengthCommand(click.Command):
    """Translate any opt= to opt_length= as needed"""

    def parse_args(self, ctx: Context, args: list[str]) -> list[str]:
        options = [o for o in ctx.command.params if getattr(o, "register_length", None)]
        prefixes = {p for p in sum((o.opts for o in options), []) if p.startswith("--")}  # noqa: RUF017
        for i, a in enumerate(args):
            a_tuple = a.split("=")
            if a_tuple[0] in prefixes:
                if len(a_tuple) > 1:
                    args[i] = a_tuple[0]
                    args.insert(i + 1, a_tuple[0] + "_length=" + a_tuple[1])  # noqa: B909
                else:
                    # check if next argument is naked
                    if len(args) > i + 1 and not args[i + 1].startswith("--"):
                        value = args[i + 1]
                        args[i + 1] = a_tuple[0] + "_length=" + value  # noqa: B909
        return super().parse_args(ctx, args)


@click.command(
    cls=RegisterMinimizeLengthCommand,
    short_help="Write least-privilege IAM policies, restricting all actions to resource ARNs.",
)
# pylint: disable=duplicate-code
@click.option(
    "--input-file",
    "-i",
    type=str,
    help="Path of the YAML File used for generating policies",
)
@click.option(
    "--minimize",
    "-m",
    cls=RegisterLengthOption,
    is_flag=True,
    required=False,
    default=False,
    help="Minimize the resulting statement with *safe* usage of wildcards to reduce policy length.",
)
@click.option(
    "--minimize_length",
    cls=RegisterLengthOptionHelp,
    help="Sets the minimum character length for minimization. Defaults to zero.",
    type=click.IntRange(0),
    required=False,
    default=0,
)
@click.option(
    "--fmt",
    type=click.Choice(["yaml", "json", "terraform"]),
    default="json",
    required=False,
    help='Format output as YAML or JSON. Defaults to "json"',
)
@click.option(
    "--verbose",
    "-v",
    type=click.Choice(["critical", "error", "warning", "info", "debug"], case_sensitive=False),
)
def write_policy(
    input_file: str | Path,
    minimize: int,
    minimize_length: int,
    fmt: str,
    verbose: str | None,
) -> None:
    """
    Write least-privilege IAM policies, restricting all actions to resource ARNs.
    """
    if verbose:
        log_level = getattr(logging, verbose.upper())
        set_stream_logger(level=log_level)

    if input_file:
        cfg = read_yaml_file(input_file)
    else:
        try:
            cfg = yaml.safe_load(sys.stdin)
        except yaml.YAMLError as exc:
            logger.critical(exc)
            sys.exit()

    min_length = None
    if minimize:
        min_length = minimize_length
    policy = write_policy_with_template(cfg, min_length)

    if fmt == "yaml":
        policy_str = yaml.dump(policy, sort_keys=False)
    else:
        indent = 4 if fmt == "json" else None
        policy_str = json.dumps(policy, indent=indent)
        if fmt == "terraform":
            obj = {"policy": policy_str}
            policy_str = json.dumps(obj)
    print(policy_str)


def write_policy_with_template(cfg: dict[str, Any], minimize: int | None = None) -> dict[str, Any]:
    """
    This function is called by write-policy so the config can be passed in as a dict without running into a Click-related error. Use this function, rather than the write-policy function, if you are using Policy Sentry as a python library.

    Arguments:
        cfg: The loaded YAML as a dict. Must follow Policy Sentry dictated format.
        minimize: Minimize the resulting statement with *safe* usage of wildcards to reduce policy length. Set this to the character length you want - for example, 0, or 4. Defaults to none.
    Returns:
        Dictionary: The JSON policy
    """
    sid_group = SidGroup()
    policy = sid_group.process_template(cfg, minimize)
    return policy
