import unittest
from cloudsplaining.shared.utils import remove_wildcard_only_actions, remove_read_level_actions


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
        actions = [
            "ssm:GetParameters",
            "ecr:PutImage"
        ]
        result = remove_read_level_actions(actions)
        expected_result = ['ecr:PutImage']
        self.assertListEqual(result, expected_result)

