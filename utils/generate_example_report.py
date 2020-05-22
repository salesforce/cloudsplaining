#! /usr/bin/env python
from cloudsplaining.output.html_report import generate_html_report
from cloudsplaining.shared.constants import DEFAULT_EXCLUSIONS_CONFIG
import os
import webbrowser
import json
import shutil

example_results_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
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
        "examples",
        "files",
        "iam-principals-example.json",
    )
)

with open(example_principal_policy_mapping_file) as json_file:
    example_principal_policy_mapping = json.load(json_file)


def generate_example_report():
    output_directory = os.getcwd()
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
    html_output_file = os.path.join(output_directory, f"iam-report-{account_name}.html")

    with open(html_output_file, "w") as f:
        f.write(rendered_html_report)

    print(f"Wrote HTML results to: {html_output_file}")
    index_output_file = os.path.join(output_directory, "index.html")
    shutil.copyfile(os.path.join(output_directory, "iam-report-fake.html"), index_output_file)
    url = "file://%s" % os.path.abspath(index_output_file)
    webbrowser.open(url, new=2)


if __name__ == '__main__':
    generate_example_report()
