"""Every privilege-escalation method must be detectable from its own action set.

PRIVILEGE_ESCALATION_METHODS is matched by subset: a policy whose expanded actions are
a superset of a method's actions is flagged with that method. This test builds, for each
method, a policy granting exactly that method's actions and asserts the method is detected.
It also implicitly verifies policy_sentry recognizes every action (an unrecognized action
would drop out during expansion and the method would not be detected).
"""

import unittest

from cloudsplaining.scan.policy_document import PolicyDocument
from cloudsplaining.shared.constants import PRIVILEGE_ESCALATION_METHODS


class TestPrivilegeEscalationMethodsAreDetectable(unittest.TestCase):
    def test_every_method_detected_from_its_own_actions(self):
        undetected = []
        for method, actions in PRIVILEGE_ESCALATION_METHODS.items():
            test_policy = {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": list(actions), "Resource": "*"}],
            }
            detected = {finding["type"] for finding in PolicyDocument(test_policy).allows_privilege_escalation}
            if method not in detected:
                undetected.append((method, actions))
        self.assertEqual(undetected, [], f"methods not detected from their own actions: {undetected}")
