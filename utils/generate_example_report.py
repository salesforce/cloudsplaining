#! /usr/bin/env python
import sys
import os
from pathlib import Path
sys.path.append(str(Path(os.path.dirname(__file__)).parent))
from cloudsplaining.output.report import HTMLReport
from cloudsplaining.command.scan import scan_account_authorization_details
from cloudsplaining.shared.exclusions import DEFAULT_EXCLUSIONS
import webbrowser
import json
import shutil

# account_authorization_details_file = os.path.abspath(os.path.join(
#         os.path.dirname(__file__),
#         os.path.pardir,
#         "examples",
#         "files",
#         "example.json",
#     )
# )
#
# with open(account_authorization_details_file) as json_file:
#     account_authorization_details_cfg = json.load(json_file)

results_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "example-iam-data.json",
    )
)

with open(results_file) as json_file:
    results = json.load(json_file)


def generate_example_report():
    output_directory = os.getcwd()
    account_name = "fake"
    account_id = "987654321987"
    # rendered_report = scan_account_authorization_details(
    #     results_file, DEFAULT_EXCLUSIONS, account_name="example", output_directory=os.getcwd()
    # )
    minimize = False
    html_report = HTMLReport(
        account_id=account_id,
        account_name=account_name,
        results=results,
        minimize=minimize
    )
    rendered_report = html_report.get_html_report()

    # html_output_file = os.path.join(output_directory, f"index.html")
    html_output_file = os.path.join(output_directory, f"iam-report-{account_name}.html")
    if os.path.exists(html_output_file):
        print(f"{html_output_file} exists. Removing then replacing...")
        os.remove(html_output_file)

    with open(html_output_file, "w") as f:
        f.write(rendered_report)

    print(f"Wrote HTML results to: {html_output_file}")

    index_output_file = os.path.join(output_directory, "index.html")
    if os.path.exists(index_output_file):
        print(f"{index_output_file} exists. Removing then replacing...")
        os.remove(index_output_file)
    print(f"Copying HTML results to the index file: {index_output_file}")
    shutil.copyfile(os.path.join(output_directory, "iam-report-fake.html"), index_output_file)
    url = "file://%s" % os.path.abspath(index_output_file)
    webbrowser.open(url, new=2)


if __name__ == '__main__':
    generate_example_report()
