import os
import unittest
import shlex
from click.testing import CliRunner
from cloudsplaining.command.expand_policy import expand_policy


class ExpandPolicyClickTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_click_expand_policy_wildcards(self):
        """cloudsplaining.command.expand_policy: expand_policy with wildcards example should return exit code 0"""
        examples_directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "examples")
        )
        input_file = os.path.join(examples_directory, "policies", "wildcards.json")
        command = f"--input-file {input_file}"
        args = shlex.split(command)
        response = self.runner.invoke(cli=expand_policy, args=args)
        print(response.output)
        self.assertTrue(response.exit_code == 0)

    def test_click_expand_policy_explicit_actions(self):
        """cloudsplaining.command.expand_policy: expand_policy with explicit actions example should return exit code 0"""
        examples_directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "examples")
        )
        input_file = os.path.join(examples_directory, "policies", "explicit-actions.json")
        command = f"--input-file {input_file}"
        args = shlex.split(command)
        response = self.runner.invoke(cli=expand_policy, args=args)
        print(response.output)
        self.assertTrue(response.exit_code == 0)
