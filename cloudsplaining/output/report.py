"""Creates the HTML Reports"""
import os
import codecs
import datetime
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from cloudsplaining.bin.version import __version__


class HTMLReport:
    """
    HTML Report
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, account_name, account_id, exclusions_cfg, results, principal_policy_mapping):
        self.account_name = account_name
        self.account_id = account_id
        self.scan_results = results
        self.principal_policy_mapping = principal_policy_mapping
        self.exclusions_cfg = exclusions_cfg

        self.report_generated_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # Calculate ratio of policies with PrivEsc, Permissions management, or Data leak potential
        self.policies_with_data_leak_potential = 0
        self.policies_with_permissions_management = 0
        self.policies_with_privilege_escalation = 0

        for finding in results:
            # These are stats we care about regardless of who manages it, as they help with prioritization
            if finding["DataExfiltrationActions"]:
                self.policies_with_data_leak_potential += 1
            if finding["PrivilegeEscalation"]:
                self.policies_with_privilege_escalation += 1
            if finding["PermissionsManagementActions"]:
                self.policies_with_permissions_management += 1

    def get_html_report(self):
        """Get the HTML Report as a string"""
        report_documentation = ReportDocumentation()
        # Formatted results to feed into the HTML
        iam_report_results_formatted = dict(
            account_name=self.account_name,
            account_id=self.account_id,
            report_generated_time=self.report_generated_time,
            cloudsplaining_version=__version__,
            results=self.scan_results,
            principal_policy_mapping=self.principal_policy_mapping,
            overview_write_up=report_documentation.overview_html,
            triage_guidance_write_up=report_documentation.triage_guidance_html,
            remediation_guidance_write_up=report_documentation.validation_guidance_html,
            glossary_write_up=report_documentation.glossary_html,
            policies_with_data_leak_potential=self.policies_with_data_leak_potential,
            policies_with_privilege_escalation=self.policies_with_privilege_escalation,
            policies_with_permissions_management=self.policies_with_permissions_management,
            exclusions_configiuration=yaml.dump(self.exclusions_cfg),
        )
        # HTML Report template
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader=FileSystemLoader(template_path))  # nosec
        template = env.get_template("template.html")
        return template.render(t=iam_report_results_formatted)


class ReportDocumentation:
    """Holds the rendered Markdown documentation that goes along with the report"""
    def __init__(self):
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
        self.overview_html = markdown.markdown(
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
        self.triage_guidance_html = markdown.markdown(
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
        self.remediation_guidance_html = markdown.markdown(
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
        self.validation_guidance_html = markdown.markdown(
            validation_guidance_file.read(), extensions=["markdown.extensions.extra"]
        )

        # 5. Glossary
        glossary_file = codecs.open(
            os.path.join(os.path.dirname(__file__), "templates", "guidance", "glossary.md"),
            mode="r",
            encoding="utf-8",
        )
        self.glossary_html = markdown.markdown(
            glossary_file.read(), extensions=["markdown.extensions.extra"]
        )
