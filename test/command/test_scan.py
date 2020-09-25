import unittest
import os
import json
from cloudsplaining.command.scan import scan_account_authorization_details
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS
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


# class PolicyFileTestCase(unittest.TestCase):
#     def test_scan_authz_details_and_output_html_as_string(self):
#         example_authz_details_file = os.path.abspath(
#             os.path.join(
#                 os.path.dirname(__file__),
#                 os.path.pardir,
#                 "files",
#                 "example-authz-details.json",
#             )
#         )
#         with open(example_authz_details_file, "r") as json_file:
#             cfg = json.load(json_file)
#             decision = check_authorization_details_schema(cfg)
#         self.assertTrue(decision)
#
#         rendered_html_report = scan_account_authorization_details(
#             cfg, DEFAULT_EXCLUSIONS, account_name="Something", output_directory=os.getcwd(),
#             write_data_files=False
#         )
#         # print(rendered_html_report)
