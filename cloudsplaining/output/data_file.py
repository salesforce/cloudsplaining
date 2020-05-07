"""Creates a JSON data file containing the results."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import os
import json


# pragma: no cover
def write_results_data_file(results, raw_data_file):
    """
    Writes the raw data file containing all the results for an AWS account

    :param results: Dictionary containing the scan results for a particular account
    :param raw_data_file:
    :return:
    """
    # Write the output to a results file if that was specified. Otherwise, just print to stdout
    if os.path.exists(raw_data_file):
        os.remove(raw_data_file)
    with open(raw_data_file, "w") as file:
        json.dump(results, file, indent=4)
    return raw_data_file
