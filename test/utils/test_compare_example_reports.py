"""Tests for utils/compare_example_reports.py — the deterministic report regression guard."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "utils" / "compare_example_reports.py"


def _write(data: dict) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(data, f)
    f.close()
    return f.name


def _run(old: dict, new: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--old", _write(old), "--new", _write(new)],
        capture_output=True,
        text=True,
    )


def _policy(findings):
    return {"customer_managed_policies": {"p1": {"PrivilegeEscalation": {"findings": findings}}}}


CREATE_ACCESS_KEY = {"type": "CreateAccessKey", "actions": ["iam:createaccesskey"]}
ATTACH_ROLE_POLICY = {"type": "AttachRolePolicy", "actions": ["iam:attachrolepolicy"]}


def test_identical_passes():
    d = _policy([CREATE_ACCESS_KEY])
    r = _run(d, d)
    assert r.returncode == 0, r.stdout + r.stderr


def test_added_finding_passes():
    old = _policy([CREATE_ACCESS_KEY])
    new = _policy([CREATE_ACCESS_KEY, ATTACH_ROLE_POLICY])
    r = _run(old, new)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "AttachRolePolicy" in r.stdout


def test_removed_finding_fails():
    old = _policy([CREATE_ACCESS_KEY, ATTACH_ROLE_POLICY])
    new = _policy([CREATE_ACCESS_KEY])
    r = _run(old, new)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "AttachRolePolicy" in r.stdout


def test_flat_action_findings_supported():
    # Non-privesc categories store findings as plain action strings.
    old = {"customer_managed_policies": {"p1": {"DataExfiltration": {"findings": ["s3:GetObject", "ssm:GetParameter"]}}}}
    new = {"customer_managed_policies": {"p1": {"DataExfiltration": {"findings": ["s3:GetObject"]}}}}
    r = _run(old, new)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "ssm:GetParameter" in r.stdout
