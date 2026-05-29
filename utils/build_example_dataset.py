#! /usr/bin/env python
"""Build the enriched example authorization-details dataset.

The demo report should be high quality: it needs both the realistic, real-world
IAM data already in ``examples/files/example.json`` AND the small, clear teaching
entities (the ``obama`` / ``userwithlotsofpermissions`` users, the ``admin`` group,
``MyRole`` / ``MyOtherRole``, etc.) that the frontend mocha tests assert against.

Those teaching entities live in source (authorization-details) format in
``test/files/example-authz-details.json``. This script merges that overlay into
``examples/files/example.json`` so a single ``just generate-report`` produces a
rich, dual-purpose dataset.

The merge:
  * appends overlay principals (users / groups / roles) that do not collide with
    an existing natural key (UserName / GroupName / RoleName) or Arn,
  * unions the managed-policy catalog by Arn (base wins on conflict).

It is deterministic and idempotent: running it again is a no-op. The result is
validated against the authorization-details schema before being written.

Usage::

    uv run ./utils/build_example_dataset.py            # enrich in place
    uv run ./utils/build_example_dataset.py --check     # fail if not already merged
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).parent.parent))

from cloudsplaining.shared.validation import check_authorization_details_schema  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
BASE_FILE = REPO_ROOT / "examples" / "files" / "example.json"
OVERLAY_FILE = REPO_ROOT / "test" / "files" / "example-authz-details.json"

# Each principal list and the natural key that must stay unique within it.
PRINCIPAL_LISTS = {
    "UserDetailList": "UserName",
    "GroupDetailList": "GroupName",
    "RoleDetailList": "RoleName",
}


def merge_authorization_details(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Return a new dict merging ``overlay`` principals/policies into ``base``.

    Principals are deduplicated by natural key and Arn; managed policies are
    unioned by Arn. Inputs are not mutated.
    """
    merged: dict[str, Any] = {key: (list(value) if isinstance(value, list) else value) for key, value in base.items()}

    for list_name, natural_key in PRINCIPAL_LISTS.items():
        entries: list[dict[str, Any]] = list(merged.get(list_name, []))
        seen_keys = {entry.get(natural_key) for entry in entries}
        seen_arns = {entry.get("Arn") for entry in entries}
        for entry in overlay.get(list_name, []):
            if entry.get(natural_key) in seen_keys or entry.get("Arn") in seen_arns:
                continue
            entries.append(entry)
            seen_keys.add(entry.get(natural_key))
            seen_arns.add(entry.get("Arn"))
        merged[list_name] = entries

    policies: list[dict[str, Any]] = list(merged.get("Policies", []))
    seen_policy_arns = {policy.get("Arn") for policy in policies}
    for policy in overlay.get("Policies", []):
        if policy.get("Arn") in seen_policy_arns:
            continue
        policies.append(policy)
        seen_policy_arns.add(policy.get("Arn"))
    merged["Policies"] = policies

    return merged


def _load(path: Path) -> dict:
    with open(path) as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the base file is not already fully enriched (CI guard).",
    )
    args = parser.parse_args()

    base = _load(BASE_FILE)
    overlay = _load(OVERLAY_FILE)
    merged = merge_authorization_details(base, overlay)

    check_authorization_details_schema(merged)

    already_enriched = merged == base
    if args.check:
        if already_enriched:
            print("OK    example.json already contains the teaching overlay.")
            return 0
        print(
            "FAIL  example.json is missing teaching entities. Run: uv run ./utils/build_example_dataset.py",
            file=sys.stderr,
        )
        return 1

    if already_enriched:
        print("example.json already enriched; nothing to do.")
        return 0

    with open(BASE_FILE, "w") as handle:
        json.dump(merged, handle, indent=4)
        handle.write("\n")

    added = {name: len(merged.get(name, [])) - len(base.get(name, [])) for name in (*PRINCIPAL_LISTS, "Policies")}
    print(f"Wrote enriched dataset to {os.path.relpath(BASE_FILE, REPO_ROOT)}")
    print(f"Added entries: {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
