from cloudsplaining.scan.authorization_details import AuthorizationDetails
import os
import json
import unittest
from cloudsplaining.shared.exclusions import Exclusions


class ExclusionsNewTestCase(unittest.TestCase):
    def test_new_exclusions_approach(self):
        exclusions_cfg = {
            "policies": [
                "aws-service-role*"
            ],
            "roles": ["aws-service-role*"],
            "users": [""],
            "include-actions": ["s3:GetObject"],
            "exclude-actions": ["kms:Decrypt"]
        }
        exclusions = Exclusions(exclusions_cfg)
        test_actions_list = [
            "s3:GetObject",
            "kms:decrypt",
            "ssm:GetParameter",
            "ec2:DescribeInstances"
        ]
        result = exclusions.get_allowed_actions(test_actions_list)
        self.assertListEqual(result, ['s3:GetObject', 'ssm:GetParameter', 'ec2:DescribeInstances'])

    # def test_principal_policy_mapping(self):
    #     principal_policy_mapping = PrincipalPolicyMapping()
    #     principal_policy_mapping.add_with_detail(
    #         "Bob", "User", "Inline", "Customer", "MyPolicy", "Group membership"
    #     )
    #     result = principal_policy_mapping.json
    #     # print(json.dumps(result, indent=4))
    #     expected_result = [
    #         {
    #             "Principal": "Bob",
    #             "Type": "User",
    #             "PolicyType": "Inline",
    #             "ManagedBy": "Customer",
    #             "PolicyName": "MyPolicy",
    #             "Comment": "Group membership"
    #         }
    #     ]
    #     self.assertListEqual(result, expected_result)
    #
    # def test_full_exclusions_case(self):
    #     principal_policy_mapping = PrincipalPolicyMapping()
    #     principal_policy_mapping.add_with_detail("AdminUsers", "Group", "Managed", "AWS", "AdministratorAccess", None)
    #     principal_policy_mapping.add_with_detail("NginxServer", "Role", "Inline", "Customer", "SsmOnboardingInlinePolicy", None)
    #     principal_policy_mapping.add_with_detail("SsoDeveloperRole", "Role", "Inline", "Customer", "InlinePolicyForTestingOverride", None)
    #     principal_policy_mapping.add_with_detail("Obama", "User", "Managed", "AWS", "AdministratorAccess", ["AdminUsers"])  # via AdminUsers
    #     principal_policy_mapping.add_with_detail("Pelosi", "User", "Managed", "Customer", "PowerUserCustom", None)  # Managed policy directly attached to user
    #     # Note how above there is only one user with AdministratorAccess - Obama.
    #     # If we exclude obama, we should be able to not include the group
    #     exclusions_cfg = {
    #         # We only care about the "Obama" user here.
    #         "users": ["Obama"],
    #         "policies": [
    #             "aws-service-role*"
    #         ],
    #         "roles": ["aws-service-role*"],
    #         "include-actions": ["s3:GetObject"],
    #         "exclude-actions": ["kms:Decrypt"]
    #     }
    #     exclusions = Exclusions(exclusions_cfg)
    #     results = principal_policy_mapping.get_post_exclusion_principal_policy_mapping(exclusions)
    #     # print(json.dumps(results.json, indent=4))
    #     # Obama should not be included in the results
    #     self.assertTrue(False for entry in results.json if "Obama" in entry["Principal"])
    #     self.assertTrue(False for entry in results.json if "AdminUsers" in entry["Principal"])
    #     # The results should not include Obama OR AdministratorAccess
    #     # Now let's add Biden. The results should now include AdminUsers AND Biden, but NOT Obama
    #     principal_policy_mapping.add_with_detail("Biden", "User", "Managed", "AWS", "AdministratorAccess", ["AdminUsers"])
    #     results = principal_policy_mapping.get_post_exclusion_principal_policy_mapping(exclusions)
    #     # print(json.dumps(results.json, indent=4))
    #     self.assertTrue(True for entry in results.json if "AdminUsers" in entry["Principal"])
    #     self.assertTrue(True for entry in results.json if "Biden" in entry["Principal"])
    #     # Let's just print it out here so it's easy to visualize the results in the test file
    #     expected_results = [
    #         {
    #             "Principal": "AdminUsers",
    #             "Type": "Group",
    #             "PolicyType": "Managed",
    #             "ManagedBy": "AWS",
    #             "PolicyName": "AdministratorAccess",
    #             "Comment": None
    #         },
    #         {
    #             "Principal": "NginxServer",
    #             "Type": "Role",
    #             "PolicyType": "Inline",
    #             "ManagedBy": "Customer",
    #             "PolicyName": "SsmOnboardingInlinePolicy",
    #             "Comment": None
    #         },
    #         {
    #             "Principal": "SsoDeveloperRole",
    #             "Type": "Role",
    #             "PolicyType": "Inline",
    #             "ManagedBy": "Customer",
    #             "PolicyName": "InlinePolicyForTestingOverride",
    #             "Comment": None
    #         },
    #         {
    #             "Principal": "Biden",
    #             "Type": "User",
    #             "PolicyType": "Managed",
    #             "ManagedBy": "AWS",
    #             "PolicyName": "AdministratorAccess",
    #             "Comment": [
    #                 "AdminUsers"
    #             ]
    #         }
    #     ]
    #     self.assertListEqual(results.json, expected_results)
