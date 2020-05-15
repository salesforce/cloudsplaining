"""Functions that handle the report writing functionality of this tool."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import os
import codecs
import datetime
import webbrowser
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from cloudsplaining.bin.version import __version__
from cloudsplaining.output.triage_worksheet import create_triage_worksheet


def generate_html_report(
    account_metadata,
    results,
    principal_policy_mapping,
    output_directory,
    exclusions_cfg,
    skip_open_report=False,
):
    """Create IAM HTML report"""

    account_id = account_metadata.get("account_id")
    account_name = account_metadata.get("account_name")
    html_output_file = os.path.join(output_directory, f"iam-report-{account_name}.html")
    # sorted_results = sorted(results, key=lambda i: i["PolicyName"])

    # Calculate ratio of policies with PrivEsc, Permissions management, or Data leak potential
    policies_with_data_leak_potential = 0
    policies_with_permissions_management = 0
    policies_with_privilege_escalation = 0

    for finding in results:
        # These are stats we care about regardless of who manages it, as they help with prioritization
        if finding["DataExfiltrationActions"]:
            policies_with_data_leak_potential += 1
        if finding["PrivilegeEscalation"]:
            policies_with_privilege_escalation += 1
        if finding["PermissionsManagementActions"]:
            policies_with_permissions_management += 1

    # MARKDOWN WRITE-UPS
    # Leverage this documentation for setting HTML in the markdown file.
    # We are using markdown because it's just an easier way to modify the general reusable text content.
    # https://python-markdown.github.io/extensions/md_in_html/
    # 1. Overview
    overview_file = codecs.open(
        os.path.join(
            os.path.dirname(__file__), "templates", "guidance", "1-overview.md"
        ),
        mode="r",
        encoding="utf-8",
    )
    overview_html = markdown.markdown(
        overview_file.read(), extensions=["markdown.extensions.extra"]
    )

    # 2. Triage guidance
    triage_guidance_file = codecs.open(
        os.path.join(
            os.path.dirname(__file__), "templates", "guidance", "2-triage-guidance.md"
        ),
        mode="r",
        encoding="utf-8",
    )
    triage_guidance_html = markdown.markdown(
        triage_guidance_file.read(), extensions=["markdown.extensions.extra"]
    )

    # 3. Remediation Guidance
    remediation_guidance_file = codecs.open(
        os.path.join(
            os.path.dirname(__file__),
            "templates",
            "guidance",
            "3-remediation-guidance.md",
        ),
        mode="r",
        encoding="utf-8",
    )
    remediation_guidance_html = markdown.markdown(
        remediation_guidance_file.read(), extensions=["markdown.extensions.extra"]
    )

    # 4. Validation
    validation_guidance_file = codecs.open(
        os.path.join(
            os.path.dirname(__file__), "templates", "guidance", "4-validation.md"
        ),
        mode="r",
        encoding="utf-8",
    )
    validation_guidance_html = markdown.markdown(
        validation_guidance_file.read(), extensions=["markdown.extensions.extra"]
    )

    # 5. Glossary
    glossary_file = codecs.open(
        os.path.join(os.path.dirname(__file__), "templates", "guidance", "glossary.md"),
        mode="r",
        encoding="utf-8",
    )
    glossary_html = markdown.markdown(
        glossary_file.read(), extensions=["markdown.extensions.extra"]
    )

    # Formatted results to feed into the HTML
    iam_report_results_formatted = {
        # Metadata
        "account_name": account_name,
        "account_id": account_id,
        "report_generated_time": datetime.datetime.now().strftime("%Y-%m-%d"),
        "cloudsplaining_version": __version__,
        # Actual results
        "results": results,
        # IAM Principals
        "principal_policy_mapping": principal_policy_mapping,
        # Write-ups rendered from markdown
        "overview_write_up": overview_html,
        "triage_guidance_write_up": triage_guidance_html,
        "remediation_guidance_write_up": remediation_guidance_html,
        "validation_guidance_write_up": validation_guidance_html,
        "glossary_write_up": glossary_html,
        # Count of policies with these findings for the stats
        "policies_with_data_leak_potential": policies_with_data_leak_potential,
        "policies_with_privilege_escalation": policies_with_privilege_escalation,
        "policies_with_permissions_management": policies_with_permissions_management,
        # Exclusions config for appendix and user reference
        "exclusions_configuration": yaml.dump(exclusions_cfg),
    }

    # HTML Report template
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_path))  # nosec
    template = env.get_template("template.html")
    with open(html_output_file, "w") as f:
        f.write(template.render(t=iam_report_results_formatted))

    print(f"Wrote HTML results to: {html_output_file}")

    # Open the report by default
    if not skip_open_report:
        print("Opening the HTML report")
        url = "file://%s" % os.path.abspath(html_output_file)
        webbrowser.open(url, new=2)

    # Create the CSV triage sheet
    create_triage_worksheet(account_name, results, output_directory)
