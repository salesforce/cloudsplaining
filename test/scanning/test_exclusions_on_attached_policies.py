import os
import unittest
import json
from cloudsplaining.scan.group_details import GroupDetailList
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails
from cloudsplaining.scan.user_details import UserDetail

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


# class TestPolicyAttachments(unittest.TestCase):
#     def test_user_detail_attached_managed_policies(self):
#         user_detail_json_input = auth_details_json["UserDetailList"][2]
#         policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
#
#         all_group_details_json = auth_details_json["GroupDetailList"]
#         all_group_details = GroupDetailList(all_group_details_json, policy_details)
