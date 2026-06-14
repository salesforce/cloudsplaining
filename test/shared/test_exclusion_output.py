"""Tests for how exclusion-match messages are emitted.

The "Excluded prefix/suffix" lines from ``is_name_excluded`` must be quiet for library
consumers (routed to ``logger.debug`` so they can be silenced via standard logging) but
must still print to stdout on the CLI. The CLI scopes that printing to the invocation and
restores the prior value afterward, so an in-process CLI run does not leak printing state
back into later library use.
"""

import contextlib
import io
import unittest

from click.testing import CliRunner

from cloudsplaining.bin.cli import cloudsplaining as cloudsplaining_cli
from cloudsplaining.shared.exclusions import is_name_excluded, set_exclusion_output


class ExclusionOutputRoutingTestCase(unittest.TestCase):
    def setUp(self):
        # Every test starts from the library default and restores it afterward.
        self.addCleanup(set_exclusion_output, False)
        set_exclusion_output(False)

    def test_library_default_is_quiet_on_prefix_match(self):
        """As a library (default), a prefix exclusion match prints nothing to stdout."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = is_name_excluded("/aws-service-role/foo", "/aws-service-role*")
        self.assertTrue(result)
        self.assertEqual(buffer.getvalue(), "")

    def test_library_default_is_quiet_on_suffix_match(self):
        """As a library (default), a suffix exclusion match prints nothing to stdout."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = is_name_excluded("Secure-ish", "*ish")
        self.assertTrue(result)
        self.assertEqual(buffer.getvalue(), "")

    def test_prefix_match_is_logged_at_debug(self):
        """As a library, the prefix match is emitted as a DEBUG log record."""
        with self.assertLogs("cloudsplaining.shared.exclusions", level="DEBUG") as captured:
            is_name_excluded("/aws-service-role/foo", "/aws-service-role*")
        self.assertTrue(any("Excluded prefix" in message for message in captured.output))

    def test_cli_mode_prints_prefix_match(self):
        """When the CLI enables output, the prefix match still prints to stdout."""
        set_exclusion_output(True)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = is_name_excluded("/aws-service-role/foo", "/aws-service-role*")
        self.assertTrue(result)
        self.assertIn("Excluded prefix", buffer.getvalue())

    def test_set_exclusion_output_returns_previous_value(self):
        """set_exclusion_output returns the prior value so callers can restore it."""
        self.assertFalse(set_exclusion_output(True))
        self.assertTrue(set_exclusion_output(False))

    def test_cli_invocation_does_not_leak_output_state(self):
        """Regression (Codex adversarial-review finding): after an in-process CLI run, the
        toggle is restored so a later library call stays quiet."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cloudsplaining_cli, ["create-exclusions-file", "-o", "exclusions.yml"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        # The CLI must have restored the library-quiet default: a later library call that
        # hits an exclusion match prints nothing to stdout.
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            is_name_excluded("/aws-service-role/foo", "/aws-service-role*")
        self.assertEqual(buffer.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
