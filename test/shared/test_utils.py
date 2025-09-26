import unittest
from cloudsplaining.shared.utils import (
    get_account_id_from_principal,
    remove_read_level_actions,
    remove_wildcard_only_actions,
)


class TestUtils(unittest.TestCase):
    def test_remove_wildcard_only_actions(self):
        actions = [
            # 3 wildcard only actions
            "secretsmanager:getrandompassword",
            "secretsmanager:listsecrets",
            # This one is wildcard OR "secret"
            "secretsmanager:putsecretvalue",
        ]
        results = remove_wildcard_only_actions(actions)
        # print(results)
        self.assertListEqual(results, ["secretsmanager:PutSecretValue"])

    def test_remove_read_level_actions(self):
        actions = ["ssm:GetParameters", "ecr:PutImage"]
        result = remove_read_level_actions(actions)
        expected_result = ["ecr:PutImage"]
        self.assertListEqual(result, expected_result)

    def test_get_account_id_from_principal(self):
        self.assertEqual(
            get_account_id_from_principal("arn:aws:iam::123456789012:role/test"),
            "123456789012",
        )
        self.assertEqual(get_account_id_from_principal(" 210987654321"), "210987654321")
        self.assertIsNone(get_account_id_from_principal("invalid"))
