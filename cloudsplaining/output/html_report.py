"""Functions that handle the report writing functionality of this tool."""
import codecs
import os
import datetime
import statistics
import webbrowser
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader

from cloudsplaining.output.triage_worksheet import create_triage_worksheet


def generate_html_report(account_metadata, results, output_directory, exclusions_cfg):
    """Create IAM HTML report"""

    account_id = account_metadata.get('account_id')
    account_name = account_metadata.get('account_name')
    html_output_file = os.path.join(output_directory, f"iam-report-{account_name}-{account_id}.html")
    sorted_results = sorted(results, key=lambda i: i["PolicyName"])

    # STATS FOR NERDS 8-|
    # Services affected per policy type
    total_services_affected_by_customer_policies = []
    total_services_affected_by_aws_policies = []

    # Calculate median stats per policy
    service_count_per_customer_policy = []
    service_count_per_aws_policy = []

    action_count_per_customer_policy = []
    action_count_per_aws_policy = []

    # Calculate ratio of policies with PrivEsc, Permissions management, or Data leak potential
    policies_with_data_leak_potential = 0
    policies_with_permissions_management = 0
    policies_with_privilege_escalation = 0

    for finding in sorted_results:
        if finding["ManagedBy"] == "Customer":
            service_count_per_customer_policy.append(finding["ServicesCount"])
            action_count_per_customer_policy.append(finding["ActionsCount"])
            for service in finding["Services"]:
                if service not in total_services_affected_by_customer_policies:
                    total_services_affected_by_customer_policies.append(service)
        if finding["ManagedBy"] == "AWS":
            service_count_per_aws_policy.append(finding["ServicesCount"])
            action_count_per_aws_policy.append(finding["ActionsCount"])
            for service in finding["Services"]:
                if service not in total_services_affected_by_aws_policies:
                    total_services_affected_by_aws_policies.append(service)

        # These are stats we care about regardless of who manages it, as they help with prioritization
        if finding["AllowsDataLeakActions"]:
            policies_with_data_leak_potential += 1
        if finding["PrivilegeEscalation"]:
            policies_with_privilege_escalation += 1
        if finding["PermissionsManagementActions"]:
            policies_with_permissions_management += 1

    total_services_affected_by_aws_policies.sort()
    total_services_affected_by_customer_policies.sort()

    policies_in_use = account_metadata.get('customer_managed_policies') + account_metadata.get('aws_managed_policies')

    # MARKDOWN WRITE-UPS
    # Leverage this documentation for setting HTML in the markdown file.
    # We are using markdown because it's just an easier way to modify the general reusable text content.
    # https://python-markdown.github.io/extensions/md_in_html/
    # 1. Overview
    overview_file = codecs.open(os.path.join(os.path.dirname(__file__), "templates", "guidance", "1-overview.md"), mode="r", encoding="utf-8")
    overview_text = overview_file.read()
    overview_html = markdown.markdown(overview_text)

    # 2. Triage guidance
    triage_guidance_file = codecs.open(os.path.join(os.path.dirname(__file__), "templates", "guidance", "2-triage-guidance.md"), mode="r", encoding="utf-8")
    triage_guidance_text = triage_guidance_file.read()
    triage_guidance_html = markdown.markdown(triage_guidance_text, extensions=['md_in_html'])

    # 3. Remediation Guidance
    remediation_guidance_file = codecs.open(os.path.join(os.path.dirname(__file__), "templates", "guidance", "3-remediation-guidance.md"), mode="r", encoding="utf-8")
    remediation_guidance_text = remediation_guidance_file.read()
    remediation_guidance_html = markdown.markdown(remediation_guidance_text, extensions=['md_in_html'])

    # 4. Validation
    validation_guidance_file = codecs.open(os.path.join(os.path.dirname(__file__), "templates", "guidance", "4-validation.md"), mode="r", encoding="utf-8")
    validation_guidance_text = validation_guidance_file.read()
    validation_guidance_html = markdown.markdown(validation_guidance_text, extensions=['md_in_html'])

    # 4. Validation
    glossary_file = codecs.open(os.path.join(os.path.dirname(__file__), "templates", "guidance", "glossary.md"), mode="r", encoding="utf-8")
    glossary_html = markdown.markdown(glossary_file.read(), extensions=['md_in_html'])

    # Formatted results to feed into the HTML
    iam_report_results_formatted = {
        "account_name": account_name,
        "account_id": account_id,
        "report_generated_time": datetime.datetime.now().strftime("%Y-%m-%d"),
        "results": sorted_results,
        # Write-ups rendered from markdown
        "overview_write_up": overview_html,
        "triage_guidance_write_up": triage_guidance_html,
        "remediation_guidance_write_up": remediation_guidance_html,
        "validation_guidance_write_up": validation_guidance_html,
        "glossary_write_up": glossary_html,
        # STATS FOR NERDS 8-|
        "policies_in_use": policies_in_use,
        "total_services_affected_by_customer_policies": len(total_services_affected_by_customer_policies),
        "total_services_affected_by_aws_policies": len(total_services_affected_by_aws_policies),
        "median_service_findings_per_customer_policy": statistics.median(service_count_per_customer_policy),
        "median_service_findings_per_aws_policy": statistics.median(service_count_per_aws_policy),
        "median_action_findings_per_customer_policy": statistics.median(action_count_per_customer_policy),
        "median_action_findings_per_aws_policy": statistics.median(action_count_per_aws_policy),
        "policies_with_data_leak_potential": policies_with_data_leak_potential,
        "policies_with_privilege_escalation": policies_with_privilege_escalation,
        "policies_with_permissions_management": policies_with_permissions_management,
        "exclusions_configuration": yaml.dump(exclusions_cfg, allow_unicode=True)
    }

    # HTML Report template
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template("template.html")
    with open(html_output_file, "w") as f:
        f.write(template.render(t=iam_report_results_formatted))

    # with open(html_output_file, "w") as f:
    #     f.write(template.render(t=iam_report_results_formatted))
    print(f"Wrote HTML results to: {html_output_file}")

    # Open the report by default
    print('Opening the HTML report')
    url = 'file://%s' % os.path.abspath(html_output_file)
    webbrowser.open(url, new=2)

    # Create the CSV triage sheet
    create_triage_worksheet(account_name, account_id, sorted_results, output_directory)


