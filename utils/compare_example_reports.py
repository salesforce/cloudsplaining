#!/usr/bin/env python3
"""Compare two example-iam-data.json reports and FAIL if any finding was dropped.

Used as a regression guard when regenerating example fixtures: additions are fine
(new techniques get onboarded), but removals mean we silently lost detections.

A finding's identity is ``(json-path-to-its-findings-list, finding-id)`` where
``finding-id`` is the PrivilegeEscalation ``type`` (e.g. "CreateAccessKey") for
privilege-escalation findings, or the action string for the other risk categories
(which store flat lists of actions). This identity is stable across incremental
regenerations of the same ``example.json`` (policy IDs do not change). If
``example.json`` itself is restructured so IDs change, everything will appear
added/removed and the diff should be reviewed manually.

Run: ``uv run ./utils/compare_example_reports.py --old OLD.json --new NEW.json``
Exit 1 if any finding was removed; 0 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def collect_findings(obj: Any, path: str = "") -> set[tuple[str, str]]:
    """Recursively collect ``(path, finding_id)`` for every findings list in *obj*."""
    found: set[tuple[str, str]] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "findings" and isinstance(value, list):
                for finding in value:
                    ident = finding.get("type") if isinstance(finding, dict) else finding
                    found.add((path, str(ident)))
            else:
                found |= collect_findings(value, f"{path}/{key}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, help="baseline example-iam-data.json")
    parser.add_argument("--new", required=True, help="regenerated example-iam-data.json")
    args = parser.parse_args()

    old = collect_findings(json.loads(Path(args.old).read_text()))
    new = collect_findings(json.loads(Path(args.new).read_text()))

    added = sorted(new - old)
    removed = sorted(old - new)

    if added:
        print(f"ADDED ({len(added)} finding(s) — expected when onboarding techniques):")
        for fpath, ident in added:
            print(f"  + {fpath}: {ident}")

    if removed:
        print(f"REMOVED ({len(removed)} finding(s) — REGRESSION, findings disappeared):")
        for fpath, ident in removed:
            print(f"  - {fpath}: {ident}")
        print("FAIL: report regression — findings were dropped.")
        return 1

    print(f"OK: no findings dropped ({len(added)} added, 0 removed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
