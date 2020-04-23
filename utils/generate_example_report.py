from cloudsplaining.output.html_report import generate_html_report
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
import os
import json

example_results_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "examples",
        "files",
        "iam-results-authz-details.json",
    )
)

with open(example_results_file) as json_file:
    example_results = json.load(json_file)


def generate_example_report():
    output_directory = os.getcwd()
    account_metadata = {
        "account_name": "fake",
        "account_id": "000011112222",
        "customer_managed_policies": 20,  # Fake value
        "aws_managed_policies": 30,  # Fake value
    }

    generate_html_report(account_metadata, example_results, output_directory, DEFAULT_EXCLUSIONS_CONFIG)


if __name__ == '__main__':
    generate_example_report()
