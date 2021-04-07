import os
import json
import yaml
import unittest
import time
from click.testing import CliRunner
from cloudsplaining.command.create_multi_account_config_file import create_multi_account_config_file
from cloudsplaining.shared import utils


class CreateMultiAccountConfigFileTestCase(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_create_multi_account_config_file_with_click(self):
        """command.create_multi_account_config_file: should return exit code 0"""
        result = self.runner.invoke(create_multi_account_config_file, ["--help"])
        print(result.output)
        self.assertTrue(result.exit_code == 0)

    def test_create_multi_account_config_file(self):
        """command.create_multi_account_config_file: should create the file as expected with contents"""
        file = os.path.join(os.path.dirname(__file__), "multi-account-config.yml")
        args = ["--output-file", file]
        result = self.runner.invoke(create_multi_account_config_file, args)
        print(result.output)
        self.assertTrue(result.exit_code == 0)
        results = utils.read_yaml_file(file)
        os.remove(file)
        self.assertListEqual(list(results.get("accounts").keys()), ["default_account", "prod", "test"])
