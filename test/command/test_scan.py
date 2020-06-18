import unittest
import os
import json
import webbrowser
from cloudsplaining.command.scan import scan_account_authorization_details
from cloudsplaining.output.html_report import generate_html_report
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions
from cloudsplaining.shared.validation import check_authorization_details_schema

example_results_file = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    os.path.pardir,
    "examples",
    "files",
    "iam-results-example.json",
)
)

with open(example_results_file) as json_file:
    example_results = json.load(json_file)

example_principal_policy_mapping_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
        "examples",
        "files",
        "iam-principals-example.json",
    )
)

with open(example_principal_policy_mapping_file) as json_file:
    example_principal_policy_mapping = json.load(json_file)


class PolicyFileTestCase(unittest.TestCase):
    def test_output_html_output_as_string(self):
        account_name = "fake"
        account_metadata = {
            "account_name": account_name,
            "account_id": "000011112222",
            "customer_managed_policies": 20,  # Fake value
            "aws_managed_policies": 30,  # Fake value
        }

        rendered_html_report = generate_html_report(
            account_metadata,
            example_results,
            example_principal_policy_mapping,
            DEFAULT_EXCLUSIONS_CONFIG
        )
        # print(rendered_html_report)
        output_directory = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
        )
        )
        html_output_file = os.path.join(output_directory, f"iam-report-{account_name}.html")
        with open(html_output_file, "w") as f:
            f.write(rendered_html_report)

        print(f"Wrote HTML results to: {html_output_file}")
        # url = "file://%s" % os.path.abspath(html_output_file)
        # webbrowser.open(url, new=2)

    def test_scan_authz_details_and_output_html_as_string(self):
        example_authz_details_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "files",
                "example-authz-details.json",
            )
        )
        with open(example_authz_details_file, "r") as json_file:
            cfg = json.load(json_file)
            decision = check_authorization_details_schema(cfg)
        self.assertTrue(decision)

        rendered_html_report = scan_account_authorization_details(
            cfg, DEFAULT_EXCLUSIONS, output=os.getcwd(), all_access_levels=False, skip_open_report=True, account_name="Something",
            write_data_files=False
        )
        print(rendered_html_report)
