import os
import unittest
import json
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails

example_authz_details_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        "files",
        "example-authz-details.json",
    )
)
with open(example_authz_details_file) as f:
    contents = f.read()
    auth_details_json = json.loads(contents)


class TestManagedPolicyDetail(unittest.TestCase):
    def test_managed_policies(self):
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
        results = policy_details.json
        # print(json.dumps(results))
        # Just going to check what the keys look like. If we try to match all the contents,
        # we'll have to change the test results every time Policy Sentry updates its IAM database
        expected_keys = [
            "NotYourPolicy",
            "InsecurePolicy",
            "ANPAI4UIINUVGB5SEC57G",
            "ANPAI3R4QMOG6Q5A4VWVG",
            "ANPAI3VAJF5ZCRZ7MCQE6",
            "ANPAI4VCZ3XPIZLQ5NZV2",
            "ANPAI65L554VRJ33ECQS6",
            "ANPAI6E2CYYMI4XI7AA5K",
            "ANPAI7XKCFMBPM3QQRRVQ",
            "ANPAIFIR6V6BVTRAHWINE",
            "ANPAIICZJNOJN36GTG6CM",
            "ANPAIKEABORKUXN6DEAZU",
            # "ANPAILL3HVNFSB6DCOWYQ", # ReadOnlyAccess slows the scan down a lot
            "ANPAINAW5ANUWTH3R4ANI",
            "ANPAIONKN3TJZUKXCHXWC",
            "ANPAIQNUJTQYDRJPC3BNK",
            "ANPAIX2T3QCXHR2OGGCTO",
            "ANPAIZTJ4DXE7G6AGAE6M",
            "ANPAJ2P4NXCHAT7NDPNR4",
            "ANPAJBWPGNOVKZD3JI2P2",
            "ANPAJKSO7NDY4T57MWDSQ",
            "ANPAJLIB4VSBVO47ZSBB6",
            "ANPAJNPP7PPPPMJRV2SA4",
            "ANPAJWVDLG5RPST6PHQ3A",
            "ANPAJYRXTHIB4FOVS3ZXS"
        ]
        self.assertListEqual(list(results.keys()), expected_keys)
