"""Tests for the local hardening fixes to the vendored iterate-pr scripts (Codex F2/F3/F4)."""
import importlib.util
from pathlib import Path

SCRIPTS = Path(__file__).parents[2] / ".claude" / "skills" / "iterate-pr" / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


monitor = _load("monitor_pr_checks")
feedback = _load("fetch_pr_feedback")
checks = _load("fetch_pr_checks")


# --- F2: cancelled / skipped checks must not be reported as green ---

def test_cancelled_check_is_not_green():
    result = monitor.terminal_marker([{"bucket": "pass"}, {"bucket": "cancel"}], [])
    assert result == "CHECKS_DONE_WITH_FAILURES"


def test_unknown_bucket_is_not_green():
    result = monitor.terminal_marker([{"bucket": "pass"}, {"bucket": "action_required"}], [])
    assert result == "CHECKS_DONE_WITH_FAILURES"


def test_skipped_and_pass_is_green():
    result = monitor.terminal_marker([{"bucket": "pass"}, {"bucket": "skipping"}], [])
    assert result == "ALL_CHECKS_PASSED"


def test_only_human_gate_pending_is_review_gate():
    pending = [{"bucket": "pending"}]
    result = monitor.terminal_marker([{"bucket": "pass"}, *pending], pending)
    assert result == "CHECKS_BLOCKED_BY_REVIEW_GATE"


# --- F3: paginated (concatenated) JSON must be preserved, not dropped ---

def test_paginated_arrays_are_merged():
    assert feedback._parse_gh_json('[{"a": 1}][{"a": 2}]') == [{"a": 1}, {"a": 2}]


def test_single_document_unchanged():
    assert feedback._parse_gh_json('{"x": 1}') == {"x": 1}
    assert feedback._parse_gh_json("[1, 2, 3]") == [1, 2, 3]
    assert feedback._parse_gh_json("") is None


# --- F4: failure logs must be bound to the PR head SHA ---

def test_matching_run_requires_head_sha():
    failed = [
        {"databaseId": 1, "name": "build", "headSha": "OLDSHA"},
        {"databaseId": 2, "name": "build", "headSha": "NEWSHA"},
    ]
    run = checks.find_matching_run(failed, "NEWSHA", "build")
    assert run["databaseId"] == 2


def test_matching_run_without_sha_falls_back_to_name():
    failed = [{"databaseId": 9, "name": "lint", "headSha": "X"}]
    run = checks.find_matching_run(failed, None, "lint")
    assert run["databaseId"] == 9


def test_no_match_for_stale_sha():
    failed = [{"databaseId": 1, "name": "build", "headSha": "OLDSHA"}]
    assert checks.find_matching_run(failed, "NEWSHA", "build") is None
