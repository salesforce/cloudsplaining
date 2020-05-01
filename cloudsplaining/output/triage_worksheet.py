"""Creates a triage CSV worksheet for account owners to fill out. This helps with identifying false positives."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import os
import csv
from policy_sentry.util.arns import get_resource_string


def create_triage_worksheet(account_name, results, output_directory):
    """
    Create a triage spreadsheet for account owners to fill out. They can specify whether it is a false positive
    depending on context or whether or not it needs to be fixed.
    """
    triage_spreadsheet_file = os.path.join(
        output_directory, f"iam-triage-{account_name}.csv"
    )
    csv_fieldnames = [
        "PolicyName",
        "Type",
        "ManagedBy",
        "Services",  # ServicesCount
        "Actions",  # ActionsCount
        "Justification",
    ]
    if os.path.exists(triage_spreadsheet_file):
        os.remove(triage_spreadsheet_file)
    with open(triage_spreadsheet_file, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_fieldnames)
        writer.writeheader()
        # Write customer findings first
        for finding in results:
            if finding["ManagedBy"] == "Customer":
                entry = {
                    "PolicyName": finding["PolicyName"],
                    "Type": get_resource_string(finding["Arn"]).split("/")[0],
                    "ManagedBy": finding["ManagedBy"],
                    "Services": finding["ServicesCount"],
                    "Actions": finding["ActionsCount"],
                    "Justification": "",
                }
                writer.writerow(entry)
        # Write AWS findings second
        for finding in results:
            if finding["ManagedBy"] == "AWS":
                entry = {
                    "PolicyName": finding["PolicyName"],
                    "Type": "Policy",
                    "ManagedBy": finding["ManagedBy"],
                    "Services": finding["ServicesCount"],
                    "Actions": finding["ActionsCount"],
                    "Justification": "",
                }
                writer.writerow(entry)

        print(f"Use this spreadsheet to triage results: {triage_spreadsheet_file}")
