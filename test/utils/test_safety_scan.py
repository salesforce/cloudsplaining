"""Tests for utils/safety_scan.py — TDD, one test at a time.

Run with: uv run pytest test/utils/test_safety_scan.py -v
"""
import subprocess
import sys
from pathlib import Path

SCAN = Path(__file__).parent.parent.parent / "utils" / "safety_scan.py"


def _run(content: str) -> subprocess.CompletedProcess:
    """Write *content* to a temp file and scan it."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        tmp = f.name
    return subprocess.run(
        [sys.executable, str(SCAN), "--path", tmp],
        capture_output=True,
        text=True,
    )


# NOTE: trigger strings are built via concatenation and avoid the "EXAMPLE"
# placeholder so (a) the scanner actually fires on them, and (b) the literal
# credential pattern never appears in this source file — otherwise the
# pre-push branch scan would flag its own test fixtures.
def test_detects_aws_access_key():
    """A file containing an AKIA access key must cause exit 1."""
    result = _run("key = " + "AKIA" + "Z7XK4PQR2WTY9ABC" + "\n")
    assert result.returncode == 1, (
        f"Expected exit 1 for AKIA key, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_detects_secret_assignment():
    """A file containing aws_secret_access_key assignment must cause exit 1."""
    result = _run(
        "aws_secret_access_key = " + "wJalrXUtnFEMIK7MDENGbPxRfiCYzABCDdef0123456" + "\n"
    )
    assert result.returncode == 1, (
        f"Expected exit 1 for secret key assignment, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_account_id_warns_but_passes():
    """A file with a 12-digit account ID must exit 0 but mention account id in output."""
    result = _run("arn:aws:iam::210987654321:role/Admin\n")
    assert result.returncode == 0, (
        f"Expected exit 0 for account ID (warn-only), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    combined = (result.stdout + result.stderr).lower()
    assert "account" in combined, (
        f"Expected output to mention 'account' for account-ID warning\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_clean_file_passes():
    """A file with no sensitive content must exit 0."""
    result = _run("nothing sensitive here\n")
    assert result.returncode == 0, (
        f"Expected exit 0 for clean file, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
