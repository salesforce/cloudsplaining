#!/usr/bin/env python3
"""Fail-closed pre-push scanner for AWS credentials accidentally committed.

Usage:
  # Scan specific files (used by tests):
  ./utils/safety_scan.py --path file1.txt --path file2.py

  # Default mode — scan branch diff vs origin/master and verify .gitignore:
  ./utils/safety_scan.py
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------
# FAIL patterns — actual credentials
CRED_PATTERNS = [
    ("access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (
        "aws_secret_access_key",
        re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*\S{16,}"),
    ),
    (
        "aws_session_token",
        re.compile(r"(?i)aws_session_token\s*[=:]\s*\S{16,}"),
    ),
]

# WARN pattern — account IDs (12-digit numbers) — NEVER fail
ACCOUNT_ID_RE = re.compile(r"\b\d{12}\b")

# Required .gitignore entries — their absence is a FAIL
REQUIRED_GITIGNORE_ENTRIES = [
    ".live-scans/",
    "dogfood-output/",
    ".report-snapshots/",
]


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

def scan_file(path: Path) -> tuple[list[tuple[int, str, str]], list[tuple[int, str]]]:
    """Return (fail_hits, warn_hits) for *path*.

    fail_hits: list of (lineno, kind, matched_text)
    warn_hits: list of (lineno, matched_text)
    """
    fail_hits: list[tuple[int, str, str]] = []
    warn_hits: list[tuple[int, str]] = []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
        return fail_hits, warn_hits

    for lineno, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in CRED_PATTERNS:
            for match in pattern.finditer(line):
                # Skip AWS documentation placeholders: AWS reserves keys/secrets
                # containing "EXAMPLE" (e.g. AKIAIOSFODNN7EXAMPLE) and never
                # issues real ones, so these are safe to appear in docs/tests.
                if "EXAMPLE" in match.group(0).upper():
                    continue
                fail_hits.append((lineno, kind, line.strip()))
                break

        if ACCOUNT_ID_RE.search(line):
            warn_hits.append((lineno, line.strip()))

    return fail_hits, warn_hits


# ---------------------------------------------------------------------------
# Git helpers (default mode)
# ---------------------------------------------------------------------------

def get_branch_changed_files() -> list[Path]:
    """Return files changed on this branch vs origin/master."""
    files: set[str] = set()

    for cmd in [
        ["git", "diff", "--name-only", "origin/master...HEAD"],
        ["git", "diff", "--cached", "--name-only"],
    ]:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    files.add(line)

    return [Path(p) for p in sorted(files)]


def check_gitignore(repo_root: Path) -> list[str]:
    """Return list of required entries that are missing from .gitignore."""
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        return list(REQUIRED_GITIGNORE_ENTRIES)

    content = gitignore.read_text(encoding="utf-8", errors="replace")
    missing = []
    for entry in REQUIRED_GITIGNORE_ENTRIES:
        if entry not in content:
            missing.append(entry)
    return missing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed AWS credential scanner for pre-push use."
    )
    parser.add_argument(
        "--path",
        dest="paths",
        metavar="FILE",
        action="append",
        default=[],
        help="Scan exactly this file (repeatable). Omit to use git-diff mode.",
    )
    args = parser.parse_args()

    all_fail_hits: list[tuple[str, int, str, str]] = []  # (file, lineno, kind, line)
    all_warn_hits: list[tuple[str, int, str]] = []       # (file, lineno, line)
    gitignore_missing: list[str] = []
    exit_code = 0

    # -----------------------------------------------------------------------
    # Choose files to scan
    # -----------------------------------------------------------------------
    if args.paths:
        files_to_scan = [Path(p) for p in args.paths]
        check_gi = False
    else:
        repo_root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True,
            ).stdout.strip()
        )
        files_to_scan = get_branch_changed_files()
        check_gi = True

        gitignore_missing = check_gitignore(repo_root)
        if gitignore_missing:
            for entry in gitignore_missing:
                print(f"FAIL  .gitignore is missing required entry: {entry!r}")
            exit_code = 1

    # -----------------------------------------------------------------------
    # Scan each file
    # -----------------------------------------------------------------------
    for path in files_to_scan:
        if not path.exists():
            continue
        fails, warns = scan_file(path)
        for lineno, kind, text in fails:
            all_fail_hits.append((str(path), lineno, kind, text))
        for lineno, text in warns:
            all_warn_hits.append((str(path), lineno, text))

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    if all_warn_hits:
        print("WARN  Possible AWS account IDs found (warn-only, not a failure):")
        for fpath, lineno, text in all_warn_hits:
            # Truncate very long lines for readability
            display = text[:120] + "..." if len(text) > 120 else text
            print(f"      {fpath}:{lineno}: account id candidate: {display}")

    if all_fail_hits:
        print("FAIL  AWS credentials detected — push BLOCKED:")
        for fpath, lineno, kind, text in all_fail_hits:
            display = text[:120] + "..." if len(text) > 120 else text
            print(f"      {fpath}:{lineno}: {kind}: {display}")
        exit_code = 1

    if exit_code == 0:
        total = len(files_to_scan)
        print(
            f"OK    safety-scan passed. "
            f"Scanned {total} file(s), "
            f"{len(all_warn_hits)} account-id warning(s), 0 credential failures."
        )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
