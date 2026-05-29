#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Monitor PR checks until they reach a terminal state.

Usage:
    uv run monitor_pr_checks.py [--pr PR_NUMBER]

If --pr is not specified, uses the PR for the current branch.

Output:
    - Prints `ALL_CHECKS_PASSED` when all checks finish without failures
    - Prints `CHECKS_DONE_WITH_FAILURES` when checks finish with failures
    - Prints `NO_CHECKS_REGISTERED` when checks do not appear after the grace period
    - Prints `DRAFT_PR_WITH_NO_CHECKS` when a draft PR has no checks after the grace period
    - Prints `CHECKS_BLOCKED_BY_REVIEW_GATE` when only human review/approval gates remain
    - Prints a tab-separated check summary after the terminal marker

The script stays quiet while polling so background monitor tools do not emit
unnecessary notifications on every iteration. Transient `gh` failures are
retried instead of terminating the monitor.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any

HUMAN_GATE_PATTERNS = [
    r"(?i)review\s+required",
    r"(?i)required\s+review",
    r"(?i)requires\s+review",
    r"(?i)required\s+approving\s+review",
    r"(?i)approval\s+required",
    r"(?i)waiting\s+for\s+approval",
    r"(?i)manual\s+approval",
    r"(?i)draft\s+(pull\s+request|pr)",
]


def run_gh_json(
    args: list[str],
    allowed_returncodes: tuple[int, ...] = (0,),
    empty_stdout_value: list[dict[str, Any]] | dict[str, Any] | None = None,
) -> list[dict[str, Any]] | dict[str, Any] | None:
    """Run a gh command that returns JSON."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in allowed_returncodes:
        return None

    if not result.stdout.strip():
        return empty_stdout_value

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_pr_info(pr_number: int | None) -> dict[str, Any] | None:
    """Resolve the PR to monitor."""
    if pr_number is not None:
        pr_info = run_gh_json([
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,url,isDraft,reviewDecision",
        ])
    else:
        pr_info = run_gh_json(["pr", "view", "--json", "number,url,isDraft,reviewDecision"])

    if not isinstance(pr_info, dict):
        return None

    number = pr_info.get("number")
    return pr_info if isinstance(number, int) else None


def get_checks(pr_number: int) -> list[dict[str, Any]] | None:
    """Fetch the current check list for a PR."""
    checks = run_gh_json([
        "pr",
        "checks",
        str(pr_number),
        "--json",
        "name,bucket,link,workflow,state,description",
    ], allowed_returncodes=(0, 1, 8, 16), empty_stdout_value=[])
    return checks if isinstance(checks, list) else None


def is_human_gate_check(check: dict[str, Any]) -> bool:
    """Return true when a pending entry is a human review/approval gate."""
    haystack = " ".join(
        str(check.get(field, ""))
        for field in ("name", "state", "description", "workflow")
    )
    return any(re.search(pattern, haystack) for pattern in HUMAN_GATE_PATTERNS)


def print_check_summary(checks: list[dict[str, Any]], max_lines: int = 20) -> None:
    """Print a concise tab-separated check summary."""
    for check in checks[:max_lines]:
        name = str(check.get("name", "unknown"))
        bucket = str(check.get("bucket", "unknown"))
        link = str(check.get("link", ""))
        print(f"{name}\t{bucket}\t{link}".rstrip(), flush=True)


def print_no_checks_summary(pr_info: dict[str, Any]) -> None:
    number = pr_info.get("number", "unknown")
    url = pr_info.get("url", "")
    is_draft = str(bool(pr_info.get("isDraft"))).lower()
    review_decision = str(pr_info.get("reviewDecision") or "")
    print(f"PR #{number}\tno_checks\t{url}".rstrip(), flush=True)
    print(f"is_draft\t{is_draft}", flush=True)
    if review_decision:
        print(f"review_decision\t{review_decision}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor PR checks until they finish")
    parser.add_argument("--pr", type=int, help="PR number (defaults to current branch PR)")
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=30,
        help="Polling interval while checks are pending or gh is transiently failing",
    )
    parser.add_argument(
        "--no-checks-seconds",
        type=int,
        default=15,
        help="Retry delay when a fresh push has not registered any checks yet",
    )
    parser.add_argument(
        "--no-checks-timeout-seconds",
        type=int,
        default=180,
        help="Maximum time to wait for checks to register before reporting no checks",
    )
    args = parser.parse_args()

    pr_info = get_pr_info(args.pr)
    if pr_info is None:
        print("No PR found for current branch", file=sys.stderr)
        return 1

    pr_number = pr_info["number"]
    no_checks_started_at: float | None = None

    while True:
        checks = get_checks(pr_number)
        if checks is None:
            time.sleep(args.poll_seconds)
            continue

        if not checks:
            now = time.monotonic()
            if no_checks_started_at is None:
                no_checks_started_at = now
            if now - no_checks_started_at >= args.no_checks_timeout_seconds:
                marker = "DRAFT_PR_WITH_NO_CHECKS" if pr_info.get("isDraft") else "NO_CHECKS_REGISTERED"
                print(marker, flush=True)
                print_no_checks_summary(pr_info)
                return 0
            time.sleep(args.no_checks_seconds)
            continue

        no_checks_started_at = None

        pending_checks = [check for check in checks if check.get("bucket") == "pending"]
        failed = sum(1 for check in checks if check.get("bucket") == "fail")
        actionable_pending = [
            check for check in pending_checks if not is_human_gate_check(check)
        ]
        if actionable_pending:
            time.sleep(args.poll_seconds)
            continue
        if failed:
            print("CHECKS_DONE_WITH_FAILURES", flush=True)
            print_check_summary(checks)
            return 0
        if pending_checks:
            print("CHECKS_BLOCKED_BY_REVIEW_GATE", flush=True)
            print_check_summary(checks)
            return 0

        print("ALL_CHECKS_PASSED", flush=True)
        print_check_summary(checks)
        return 0


if __name__ == "__main__":
    sys.exit(main())
