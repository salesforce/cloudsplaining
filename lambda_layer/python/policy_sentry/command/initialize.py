"""
Create the Policy Sentry config folder (~/.policy_sentry/) and the contents within
Create the SQLite datastore and fill it with the tables scraped from the AWS Docs
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

import click

from policy_sentry import set_stream_logger
from policy_sentry.querying.all import get_all_service_prefixes
from policy_sentry.shared.constants import (
    BUNDLED_DATA_DIRECTORY,
    BUNDLED_DATASTORE_FILE_PATH,
    CONFIG_DIRECTORY,
    DATASTORE_FILE_PATH,
    LOCAL_ACCESS_OVERRIDES_FILE,
    LOCAL_DATASTORE_FILE_PATH,
    LOCAL_HTML_DIRECTORY_PATH,
)

logger = logging.getLogger(__name__)


@click.command(
    name="initialize",
    short_help="Create a local datastore to store AWS IAM information.",
)
@click.option(
    "--access-level-overrides-file",
    type=str,
    required=False,
    help="Path to access level overrides file, used to override the Access Levels per action provided by AWS docs",
)
@click.option(
    "--fetch",
    is_flag=True,
    required=False,
    default=False,
    help="Specify this flag to fetch the HTML Docs directly from the AWS website. This will be helpful if the docs "
    "in the Git repository are behind the live docs and you need to use the latest version of the docs right "
    "now.",
)
@click.option(
    "--build",
    is_flag=True,
    required=False,
    default=False,
    help="Build the IAM data file from the HTML files rather than copying the data file from "
    "the python package. Defaults to false",
)
@click.option(
    "--verbose",
    "-v",
    type=click.Choice(["critical", "error", "warning", "info", "debug"], case_sensitive=False),
)
def initialize_command(
    access_level_overrides_file: str | None,
    fetch: bool,
    build: bool,
    verbose: str | None,
) -> None:
    """
    CLI command for initializing the local data file
    """
    if verbose:
        log_level = getattr(logging, verbose.upper())
        set_stream_logger(level=log_level)

    initialize(access_level_overrides_file, fetch, build)


def initialize(
    access_level_overrides_file: str | None = None,
    fetch: bool = False,
    build: bool = False,
) -> None:
    """
    Initialize the local data file to store AWS IAM information, which can be used to generate IAM policies, and for
    querying the database.
    """

    # importing 'awsdocs' is quite pricey, when it is actually only used for initialize the IAM DB
    from policy_sentry.shared.awsdocs import (
        create_database,
        update_html_docs_directory,
    )

    if not access_level_overrides_file:
        overrides_file = LOCAL_ACCESS_OVERRIDES_FILE
    else:
        overrides_file = Path(access_level_overrides_file)
    # Create the config directory
    database_path = create_policy_sentry_config_directory()

    # Create local html docs folder, if it doesn't exist
    LOCAL_HTML_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

    # Create overrides file, which allows us to override the Access Levels
    # provided by AWS documentation
    file_list = [f for f in BUNDLED_DATA_DIRECTORY.iterdir() if (BUNDLED_DATA_DIRECTORY / f).is_file()]

    for file in file_list:
        if file.suffix == ".yml":
            shutil.copy(BUNDLED_DATA_DIRECTORY / file, CONFIG_DIRECTORY)
            logger.debug("copying overrides file %s to %s", file, CONFIG_DIRECTORY)
    print(f"Database will be stored here: {database_path}")

    if not build and not fetch:
        # copy from the bundled database location to the destination path
        shutil.copy(BUNDLED_DATASTORE_FILE_PATH, database_path)

    # --fetch: wget the AWS IAM Actions, Resources and Condition Keys pages and store them locally.
    if fetch:
        # `wget` the html docs to the local directory
        update_html_docs_directory(LOCAL_HTML_DIRECTORY_PATH)
    elif not next(LOCAL_HTML_DIRECTORY_PATH.glob("*.html"), None):
        print("No HTML docs found, fetching from AWS!")
        update_html_docs_directory(LOCAL_HTML_DIRECTORY_PATH)

    # --build
    if build or access_level_overrides_file or fetch:
        create_database(CONFIG_DIRECTORY, overrides_file)
        print("Created the database!")

    # Query the database for all the services that are now in the database.
    all_aws_service_prefixes = get_all_service_prefixes()
    print("Initialization complete!")
    print(f"Total AWS services in the IAM database: {len(all_aws_service_prefixes)}")
    logger.debug("\nService prefixes:")
    logger.debug(", ".join(all_aws_service_prefixes))


def create_policy_sentry_config_directory() -> Path:
    """
    Creates a config directory at $HOME/.policy_sentry/
    :return: the path of the database file
    """
    print("Creating the database...")
    logger.debug(f"We will store the new database here: {DATASTORE_FILE_PATH}")
    # If the database file already exists, remove it
    if LOCAL_DATASTORE_FILE_PATH.exists():
        logger.debug(f"The database at {DATASTORE_FILE_PATH} already exists. Removing and replacing it.")
        LOCAL_DATASTORE_FILE_PATH.unlink()
    else:
        CONFIG_DIRECTORY.mkdir(exist_ok=True)
    return LOCAL_DATASTORE_FILE_PATH
