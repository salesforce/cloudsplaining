#! /usr/bin/env python
# If you ever need to modify example JSON data that is shown in the sampleData.js file, you can use this script to generate it.
import sys
import os
from pathlib import Path
sys.path.append(str(Path(os.path.dirname(__file__)).parent))
import json
from cloudsplaining.shared.validation import check_authorization_details_schema
from cloudsplaining.scan.authorization_details import AuthorizationDetails


account_authorization_details_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "examples",
        "files",
        "example.json",
    )
)

with open(account_authorization_details_file) as json_file:
    account_authorization_details_cfg = json.load(json_file)

results_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "example-iam-data.json",
    )
)


def generate_example_iam_data():
    check_authorization_details_schema(account_authorization_details_cfg)
    authorization_details = AuthorizationDetails(account_authorization_details_cfg)
    results = authorization_details.results
    print(f"Top-level keys of results dictionary: {results.keys()}")
    # Write the results
    if os.path.exists(results_file):
        os.remove(results_file)
    with open(results_file, "w") as file:
        json.dump(results, file, indent=4)
    print(f"Wrote new example IAM data file to: {results_file}")
    # print(json.dumps(results, indent=4))
    return results


def replace_sample_data_js(results):
    sample_data_js_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "cloudsplaining", "output", "src", "sampleData.js"
    ))
    content = f"""var sample_iam_data = {json.dumps(results, indent=4)}


exports.sample_iam_data = sample_iam_data;

"""
    if os.path.exists(sample_data_js_file):
        print(f"Removing existing file and replacing its contents")
        os.remove(sample_data_js_file)

    with open(sample_data_js_file, "w") as f:
        f.write(content)


if __name__ == '__main__':
    results = generate_example_iam_data()
    print("Replacing sampleData.js content with the most recent content")
    replace_sample_data_js(results)
    print("Replaced sampleData.js content")
