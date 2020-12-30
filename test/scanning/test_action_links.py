import os
import unittest
import json
from cloudsplaining.scan.managed_policy_detail import ManagedPolicyDetails
from cloudsplaining.scan.group_details import GroupDetailList
from cloudsplaining.scan.role_details import RoleDetailList
from cloudsplaining.scan.user_details import UserDetailList
from cloudsplaining.scan.authorization_details import AuthorizationDetails

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


class TestActionLinks(unittest.TestCase):

    def test_infrastructure_modification_actions(self):
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
        infra_mod_actions = sorted(policy_details.all_infrastructure_modification_actions)
        self.assertTrue(len(infra_mod_actions) > 3000)

    def test_group_details_infra_mod_actions(self):
        group_details_json_input = auth_details_json["GroupDetailList"]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
        group_detail_list = GroupDetailList(group_details_json_input, policy_details)
        results = group_detail_list.all_infrastructure_modification_actions_by_inline_policies
        print(json.dumps(results, indent=4))
        expected_results = [
            "s3:GetObject",
            "s3:PutObjectAcl"
        ]
        self.assertListEqual(results, expected_results)
        self.assertTrue(len(results) >= 2)

    def test_role_details_infra_mod_actions(self):
        role_details_json_input = auth_details_json["RoleDetailList"]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))
        role_detail_list = RoleDetailList(role_details_json_input, policy_details)
        results = role_detail_list.all_infrastructure_modification_actions_by_inline_policies
        expected_results = [
            "ec2:AssociateIamInstanceProfile",
            "ec2:DisassociateIamInstanceProfile",
            "iam:AddRoleToInstanceProfile",
            "iam:CreateAccessKey",
            "iam:CreateInstanceProfile",
            "iam:PassRole",
            "s3:GetObject",
            "secretsmanager:GetSecretValue"
        ]
        print(json.dumps(results, indent=4))
        self.assertListEqual(results, expected_results)

    def test_user_details_infra_mod_actions(self):
        user_details_json_input = auth_details_json["UserDetailList"]
        policy_details = ManagedPolicyDetails(auth_details_json.get("Policies"))

        group_details_json_input = auth_details_json["GroupDetailList"]
        group_detail_list = GroupDetailList(group_details_json_input, policy_details)

        user_detail_list = UserDetailList(
            user_details=user_details_json_input,
            policy_details=policy_details,
            all_group_details=group_detail_list
        )
        results = user_detail_list.all_infrastructure_modification_actions_by_inline_policies
        expected_results = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:PutObjectAcl"
        ]
        print(json.dumps(results, indent=4))
        self.assertListEqual(results, expected_results)

    def test_authorization_files_action_links(self):
        authorization_details = AuthorizationDetails(auth_details_json)
        results = authorization_details.links
        """
        # It will look like this, but :
        {
            "a4b:AssociateContactWithAddressBook": "https://docs.aws.amazon.com/a4b/latest/APIReference/API_AssociateContactWithAddressBook.html",
            "a4b:AssociateDeviceWithRoom": "https://docs.aws.amazon.com/a4b/latest/APIReference/API_AssociateDeviceWithRoom.html",
            ...
        }
        """
        print(len(results.keys()))
        self.assertTrue(len(results.keys()) > 3500)
        print(json.dumps(results, indent=4))
