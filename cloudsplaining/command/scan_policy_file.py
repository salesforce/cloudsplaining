"""
Scan a single policy file to identify missing resource constraints.
"""
import logging
import textwrap
import json
import yaml
import click
import click_log
from cloudsplaining.shared.constants import EXCLUSIONS_FILE
from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.validation import check_exclusions_schema
from cloudsplaining.shared.exclusions import is_name_excluded

logger = logging.getLogger(__name__)
click_log.basic_config(logger)
BOLD = "\033[1m"
END = "\033[0m"
finding_description = """
The policy does not practice the principle of least privilege by leveraging resource ARN constraints where possible.

For example, s3:PutObject should be restricted to a specific bucket and object path - such as 'Resource':
'arn:aws:s3:::my-bucket/path/*'. IAM Resource ARN constraints are preferable to allowing access to all resources,
like 'Resource': '*', which would allow the IAM principal to upload an S3 object to any bucket at any path.

This security control is not just limited to the context of S3, however. Other IAM actions, such as s3:PutObject,
iam:PassRole, and ssm:GetParameter should always be scoped down to only the resources that they need access to. In
the case of a compromise, overly permissive IAM policies can lead to the compromised principal having access to more
resources than necessary, which can result in data leakage or other damaging post-exploitation activities. To limit
the blast radius of compromised credentials, it is imperative to restrict access to only the IAM actions and
resource ARNs that are necessary for the IAM principal to function properly.

The following is a full list of all the actions included in the policy that do not leverage resource constraints.
"""


@click.command(
    short_help="Scan a single policy file to identify identify missing resource constraints."
)
@click.option(
    "--file",
    type=click.Path(exists=True),
    required=True,
    help="Path of to the IAM policy file.",
)
@click.option(
    "--exclusions-file",
    help="A yaml file containing a list of actions to ignore when scanning.",
    type=click.Path(exists=True),
    required=False,
    default=EXCLUSIONS_FILE,
)
@click.option(
    "--all-access-levels",
    required=False,
    default=False,
    is_flag=True,
    help="Include 'read' or 'list' actions in the results. Defaults to 'modify' only actions",
)
@click_log.simple_verbosity_option(logger)
def scan_policy_file(file, exclusions_file, all_access_levels):
    """Scan a single policy file to identify missing resource constraints."""

    # Get the exclusions configuration
    with open(exclusions_file, "r") as yaml_file:
        try:
            exclusions_cfg = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            logger.critical(exc)
    check_exclusions_schema(exclusions_cfg)

    # Get the Policy
    with open(file) as json_file:
        logger.debug(f"Opening {file}")
        policy = json.load(json_file)

    # Run the scan and get the raw data.
    results = scan_policy(policy, exclusions_cfg, all_access_levels)

    if not all_access_levels:
        issue = "{}{}{}".format(
            BOLD, "Issue found: Modify actions without resource constraints", END
        )
    else:
        issue = "{}{}{}".format(
            BOLD, "Issue found: Actions without resource constraints", END
        )
    if results:
        print("\n")
        print(issue)
        print(finding_description)
        print(textwrap.indent(str(results), "\t"))


def scan_policy(policy, exclusions_cfg, all_access_levels=False):
    """
    Scan a policy document for missing resource constraints.

    :param policy: The AWS IAM policy document.
    :param exclusions_cfg: Defaults to the embedded exclusions file, which has no effect here.
    :param all_access_levels: Include 'read' or 'list' actions in the results. Defaults to 'modify' only actions
    :return:
    """
    policy_document = PolicyDocument(policy)
    actions_missing_resource_constraints = []
    if all_access_levels:
        logger.debug(
            "--all-access-levels selected. Identifying all actions that are not leveraging resource "
            "constraints..."
        )
        for statement in policy_document.statements:
            if statement.effect == "Allow":
                actions_missing_resource_constraints.extend(statement.missing_resource_constraints)
    else:
        logger.debug(
            "--all-access-levels NOT selected. Identifying modify-only actions that are not leveraging "
            "resource constraints..."
        )
        always_include_actions = exclusions_cfg.get("include-actions", None)
        for statement in policy_document.statements:
            if statement.effect == "Allow":
                actions_missing_resource_constraints.extend(statement.missing_resource_constraints_for_modify_actions(
                    always_include_actions))
    results = []

    # EXCLUDED ACTIONS - actions to exclude if they are false positives
    excluded_actions = exclusions_cfg.get("exclude-actions", None)
    if excluded_actions == [""]:
        excluded_actions = None

    # convert to lowercase for comparison purposes
    # some weird if/else logic to reduce loops and improve performance slightly
    if excluded_actions:
        excluded_actions = [x.lower() for x in excluded_actions]

    for action in actions_missing_resource_constraints:
        if excluded_actions:
            if not is_name_excluded(action.lower, excluded_actions):
                results.append(action)
        else:
            results.append(action)
    return results
