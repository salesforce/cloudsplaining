#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Fetch PR CI checks and extract relevant failure snippets.

Usage:
    uv run fetch_pr_checks.py [--pr PR_NUMBER]

If --pr is not specified, uses the PR for the current branch.

Output: JSON to stdout with structured check data.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
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


def run_gh(args: list[str]) -> dict[str, Any] | list[Any] | None:
    """Run a gh CLI command and return parsed JSON output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout.strip() else None
    except subprocess.CalledProcessError as e:
        print(f"Error running gh {' '.join(args)}: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        return None


def get_pr_info(pr_number: int | None = None) -> dict[str, Any] | None:
    """Get PR info, optionally by number or for current branch."""
    args = [
        "pr",
        "view",
        "--json",
        "number,url,headRefName,headRefOid,baseRefName,isDraft,reviewDecision",
    ]
    if pr_number:
        args.insert(2, str(pr_number))
    return run_gh(args)


def get_checks(pr_number: int | None = None) -> list[dict[str, Any]]:
    """Get all checks for a PR."""
    args = ["gh", "pr", "checks"]
    if pr_number:
        args.append(str(pr_number))
    args.extend(["--json", "name,bucket,link,workflow,state,description,event"])
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            return []
        try:
            checks = json.loads(result.stdout)
            return checks if isinstance(checks, list) else []
        except json.JSONDecodeError:
            pass

        checks = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                checks.append({
                    "name": parts[0].strip(),
                    "bucket": parts[1].strip(),
                    "link": parts[3].strip() if len(parts) > 3 else "",
                    "workflow": "",
                })
        return checks
    except Exception:
        return []


def is_human_gate_check(check: dict[str, Any]) -> bool:
    """Return true when a pending entry is a human review/approval gate."""
    haystack = " ".join(
        str(check.get(field, ""))
        for field in ("name", "state", "description", "workflow")
    )
    return any(re.search(pattern, haystack) for pattern in HUMAN_GATE_PATTERNS)


def get_failed_runs(branch: str) -> list[dict[str, Any]]:
    """Get recent failed workflow runs for a branch."""
    result = run_gh([
        "run", "list",
        "--branch", branch,
        "--limit", "10",
        "--json", "databaseId,name,status,conclusion,headSha"
    ])
    if not isinstance(result, list):
        return []
    # Return runs that failed or are in progress
    return [r for r in result if r.get("conclusion") == "failure"]


def extract_failure_snippet(log_text: str, max_lines: int = 50) -> str:
    """Extract relevant failure snippet from log text.

    Looks for common failure markers and extracts surrounding context.
    """
    lines = log_text.split("\n")

    # Patterns that indicate failure points (case-insensitive via re.IGNORECASE)
    failure_patterns = [
        r"error[:\s]",
        r"failed[:\s]",
        r"failure[:\s]",
        r"traceback",
        r"exception",
        r"assert(ion)?.*failed",
        r"FAILED",
        r"panic:",
        r"fatal:",
        r"npm ERR!",
        r"yarn error",
        r"ModuleNotFoundError",
        r"ImportError",
        r"SyntaxError",
        r"TypeError",
        r"ValueError",
        r"KeyError",
        r"AttributeError",
        r"NameError",
        r"IndentationError",
        r"===.*FAILURES.*===",
        r"___.*___",  # pytest failure separators
    ]

    combined_pattern = "|".join(failure_patterns)

    # Find lines matching failure patterns
    failure_indices = []
    for i, line in enumerate(lines):
        if re.search(combined_pattern, line, re.IGNORECASE):
            failure_indices.append(i)

    if not failure_indices:
        # No clear failure point, return last N lines
        return "\n".join(lines[-max_lines:])

    # Extract context around first failure point
    # Include some context before and after
    first_failure = failure_indices[0]
    start = max(0, first_failure - 5)
    end = min(len(lines), first_failure + max_lines - 5)

    snippet_lines = lines[start:end]

    # If there are more failures after our snippet, note it
    remaining_failures = [i for i in failure_indices if i >= end]
    if remaining_failures:
        snippet_lines.append(f"\n... ({len(remaining_failures)} more error(s) follow)")

    return "\n".join(snippet_lines)


def get_run_logs(run_id: int) -> str | None:
    """Get failed logs for a workflow run."""
    try:
        result = subprocess.run(
            ["gh", "run", "view", str(run_id), "--log-failed"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        return None
    except subprocess.CalledProcessError:
        return None


def find_matching_run(
    failed_runs: list[dict[str, Any]], head_sha: str | None, workflow_name: str
) -> dict[str, Any] | None:
    """Pick the failed run for a check, bound to the PR head SHA.

    Local fix, diverged from getsentry/skills upstream (Codex F4): matching only by branch
    + substring name can pull logs from an older commit or a similarly-named workflow after
    multiple pushes. Require the run's headSha to equal the PR head SHA when it is known.
    """
    candidates = failed_runs
    if head_sha:
        candidates = [run for run in failed_runs if run.get("headSha") == head_sha]
    return next((run for run in candidates if workflow_name in run.get("name", "")), None)


def main():
    parser = argparse.ArgumentParser(description="Fetch PR CI checks with failure snippets")
    parser.add_argument("--pr", type=int, help="PR number (defaults to current branch PR)")
    args = parser.parse_args()

    # Get PR info
    pr_info = get_pr_info(args.pr)
    if not pr_info:
        print(json.dumps({"error": "No PR found for current branch"}))
        sys.exit(1)

    pr_number = pr_info["number"]
    branch = pr_info["headRefName"]
    head_sha = pr_info.get("headRefOid")

    # Get checks
    checks = get_checks(pr_number)

    # Process checks and add failure snippets
    processed_checks = []
    failed_runs = None  # Lazy load

    for check in checks:
        status = check.get("bucket", check.get("state", "unknown"))
        human_gate = status == "pending" and is_human_gate_check(check)
        processed = {
            "name": check.get("name", "unknown"),
            "status": status,
            "link": check.get("link", ""),
            "workflow": check.get("workflow", ""),
        }
        if check.get("state"):
            processed["state"] = check["state"]
        if check.get("description"):
            processed["description"] = check["description"]
        if human_gate:
            processed["human_gate"] = True

        # For failures, try to get log snippet
        if processed["status"] == "fail":
            if failed_runs is None:
                failed_runs = get_failed_runs(branch)

            # Find matching run by workflow name, bound to the PR head SHA
            workflow_name = processed["workflow"] or processed["name"]
            matching_run = find_matching_run(failed_runs, head_sha, workflow_name)

            if matching_run:
                logs = get_run_logs(matching_run["databaseId"])
                if logs:
                    processed["log_snippet"] = extract_failure_snippet(logs)
                    processed["run_id"] = matching_run["databaseId"]

        processed_checks.append(processed)

    # Build output
    output = {
        "pr": {
            "number": pr_number,
            "url": pr_info.get("url", ""),
            "branch": branch,
            "base": pr_info.get("baseRefName", ""),
            "is_draft": bool(pr_info.get("isDraft")),
            "review_decision": pr_info.get("reviewDecision", ""),
        },
        "summary": {
            "total": len(processed_checks),
            "passed": sum(1 for c in processed_checks if c["status"] == "pass"),
            "failed": sum(1 for c in processed_checks if c["status"] == "fail"),
            "pending": sum(1 for c in processed_checks if c["status"] == "pending"),
            "actionable_pending": sum(
                1
                for c in processed_checks
                if c["status"] == "pending" and not c.get("human_gate")
            ),
            "human_gate_pending": sum(
                1
                for c in processed_checks
                if c["status"] == "pending" and c.get("human_gate")
            ),
            "skipped": sum(1 for c in processed_checks if c["status"] in ("skipping", "cancel")),
        },
        "checks": processed_checks,
    }

    if pr_info.get("isDraft") and not processed_checks:
        output["action_required"] = "Draft PR has no registered checks; do not wait for CI indefinitely"
    elif not processed_checks:
        output["action_required"] = "No registered checks; monitor before reporting NO_CHECKS_REGISTERED"
    elif output["summary"]["actionable_pending"]:
        output["action_required"] = "Wait for actionable checks to finish; poll feedback while waiting"
    elif output["summary"]["failed"]:
        output["action_required"] = "Address failed checks"
    elif output["summary"]["pending"] and not output["summary"]["actionable_pending"]:
        output["action_required"] = "Only human review or approval gates remain pending"

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
