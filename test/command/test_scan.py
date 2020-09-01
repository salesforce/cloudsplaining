import unittest
import os
import json
import webbrowser
from cloudsplaining.command.scan import scan_account_authorization_details
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS, Exclusions
from cloudsplaining.shared.validation import check_authorization_details_schema
from cloudsplaining.output.report import HTMLReport
from cloudsplaining.scan.authorization_details import AuthorizationDetails

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
        # TODO: These values are just for testing
        account_authorization_details_cfg = cfg
        exclusions = DEFAULT_EXCLUSIONS

        authorization_details = AuthorizationDetails(account_authorization_details_cfg)
        results = authorization_details.missing_resource_constraints(
            exclusions, modify_only=True
        )

        principal_policy_mapping = authorization_details.principal_policy_mapping
        # For the IAM Principals tab, add on risk stats per principal
        for principal_policy_entry in principal_policy_mapping:
            for finding in results:
                if principal_policy_entry.get("PolicyName").lower() == finding.get("PolicyName").lower():
                    principal_policy_entry["Actions"] = len(finding["Actions"])
                    principal_policy_entry["PrivilegeEscalation"] = len(
                        finding["PrivilegeEscalation"]
                    )
                    principal_policy_entry["DataExfiltration"] = len(
                        finding["DataExfiltration"]
                    )
                    principal_policy_entry["ResourceExposure"] = len(
                        finding["ResourceExposure"]
                    )
                    principal_name = principal_policy_entry["Principal"]
                    # Customer Managed Policies
                    if finding.get("Type") == "Policy" and finding.get(
                        "ManagedBy") == "Customer" and principal_policy_entry.get("Type") != "Policy":
                        if "Principals" not in finding:
                            finding["Principals"] = [principal_name]
                        else:
                            if principal_name not in finding["Principals"]:
                                finding["Principals"].append(principal_name)

                    # AWS Managed Policies
                    if finding.get("Type") == "Policy" and finding.get("ManagedBy") == "AWS":
                        if "Principals" not in finding:
                            finding["Principals"] = [principal_name]
                        else:
                            if principal_name not in finding["Principals"]:
                                finding["Principals"].append(principal_name)

        # Lazy method to get an account ID
        account_id = None
        for item in results:
            if item["ManagedBy"] == "Customer":
                account_id = item["AccountID"]
                break

        html_report = HTMLReport(
            account_id=account_id,
            account_name="CHANGEME",
            results=results,
            exclusions_cfg=exclusions,
        )
        rendered_report = html_report.get_html_report()
        # print(rendered_report)
        # test_report_path = os.path.join(
        #     os.getcwd(),
        #     os.path.pardir,
        #     os.path.pardir,
        #     "tmp",
        #     "testing_new_html_report.html"
        # )
        # with open(test_report_path, "w") as file:
        #     file.write(rendered_report)
        # print("Opening the HTML report")
        # url = "file://%s" % os.path.abspath(test_report_path)
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
            cfg, DEFAULT_EXCLUSIONS, account_name="Something", output_directory=os.getcwd(),
            write_data_files=False
        )
        # print(rendered_html_report)
