"""Manages the exclusions template for scanning the Authorizations file"""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging

logger = logging.getLogger(__name__)


# pylint: disable=inconsistent-return-statements
def is_name_excluded(name, exclusions_list):
    """
    :param name: The name of the policy, role, user, or group
    :param exclusions_list: List of exclusions
    :return:
    """
    for exclusion in exclusions_list:
        # Skip empty items
        if exclusion == "":
            continue
        if exclusion == name:
            print(f"\tExcluded: {exclusion}")
            return True
        # ThePerfectManDoesntExi*
        if exclusion.endswith("*"):
            prefix = exclusion[: exclusion.index("*")]
            # print(prefix)
            if name.startswith(prefix):
                # logger.debug(f"Excluded prefix: {exclusion}")
                print(f"\tExcluded prefix: {exclusion}")
                return True
        if exclusion.startswith("*"):
            suffix = exclusion.split("*")[-1]
            if name.endswith(suffix):
                # logger.debug(f"Excluded suffix: {exclusion}")
                print(f"\tExcluded suffix: {exclusion}")
                return True
