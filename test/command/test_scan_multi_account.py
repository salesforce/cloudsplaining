import shutil
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner
from moto import mock_aws

from cloudsplaining.command.scan_multi_account import scan_multi_account


class ScanClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @mock_aws
    def test_scan_example_file_with_click(self):
        # given
        examples_directory = Path(__file__).parents[2] / "examples"
        config_file = examples_directory / "files/accounts.yaml"

        args = ["--config", config_file, "--role-name", "example-role", "--output-directory", self.temp_dir, "-v"]

        # when
        response = self.runner.invoke(cli=scan_multi_account, args=args)

        # then
        self.assertTrue(response.exit_code == 0)

        # 3 accounts -> 3 reports
        self.assertEqual(len(list(Path(self.temp_dir).glob("*.html"))), 3)
        self.assertEqual(response.output.count("Scanning account"), 3)
        self.assertEqual(response.output.count("Saved the HTML report to"), 3)
