import os
import unittest
import shlex
from click.testing import CliRunner
from cloudsplaining.command.scan import scan


class ScanClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_scan_example_file_with_click(self):
        """cloudsplaining.command.scan: scan should return exit code 0"""
        examples_directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "examples")
        )
        input_file = os.path.join(examples_directory, "files", "example.json")
        exclusions_file = os.path.join(examples_directory, "example-exclusions.yml")
        command = f"--input-file {input_file} " f"--exclusions-file {exclusions_file} " "--skip-open-report " "-v"
        args = shlex.split(command)
        response = self.runner.invoke(cli=scan, args=args)
        # print(response.output)
        self.assertTrue(response.exit_code == 0)
