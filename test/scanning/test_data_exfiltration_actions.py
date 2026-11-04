"""Every Data Exfiltration action must be detectable when allowed on Resource "*".

This also verifies policy_sentry recognizes every action in DATA_EXFILTRATION_ACTIONS:
an unrecognized or misspelled action would drop out during expansion and not be flagged.
"""

import unittest

from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.constants import DATA_EXFILTRATION_ACTIONS


class TestDataExfiltrationActionsAreDetectable(unittest.TestCase):
    def test_no_duplicate_actions(self):
        lowered = [action.lower() for action in DATA_EXFILTRATION_ACTIONS]
        self.assertEqual(len(lowered), len(set(lowered)))

    def test_every_action_detected_on_wildcard_resource(self):
        undetected = []
        for action in DATA_EXFILTRATION_ACTIONS:
            test_policy = {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": action, "Resource": "*"}],
            }
            if PolicyDocument(test_policy).allows_data_exfiltration_actions != [action]:
                undetected.append(action)
        self.assertEqual(undetected, [], f"actions not detected: {undetected}")
