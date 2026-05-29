"""Extract the pathfinding.cloud privilege-escalation path catalog and diff it
against cloudsplaining's existing detection constants.

Produces:
  - pathfinding-paths-catalog.yaml : faithful structured catalog of all paths
  - gap-analysis.json              : machine-readable coverage diff
and prints a human summary to stdout.

Run from repo root:  uv run python research/pathfinding-cloud/extract_catalog.py
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cloudsplaining.shared.constants import (
    ACTIONS_THAT_RETURN_CREDENTIALS,
    PRIVILEGE_ESCALATION_METHODS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PATHS_DIR = REPO_ROOT / "repos" / "pathfinding.cloud" / "data" / "paths"
OUT_DIR = Path(__file__).resolve().parent


def lc(action: str) -> str:
    return action.strip().lower()


def load_paths() -> list[dict]:
    records = []
    for yml in sorted(PATHS_DIR.rglob("*.yaml")):
        with yml.open() as fh:
            data = yaml.safe_load(fh)
        perms = data.get("permissions", {}) or {}
        required = [lc(p["permission"]) for p in (perms.get("required") or []) if p.get("permission")]
        additional = [lc(p["permission"]) for p in (perms.get("additional") or []) if p.get("permission")]
        parent = data.get("parent")
        rec = {
            "id": data.get("id"),
            "name": data.get("name"),
            "category": data.get("category"),
            "services": data.get("services") or [],
            "required_actions": required,
            "additional_actions": additional,
            "parent": (parent or {}).get("id") if isinstance(parent, dict) else parent,
            "parent_modification": (parent or {}).get("modification") if isinstance(parent, dict) else None,
            "description": (data.get("description") or "").strip(),
            "recommendation": (data.get("recommendation") or "").strip(),
            "limitations": (data.get("limitations") or "").strip(),
            "references": [
                {"title": r.get("title"), "url": r.get("url")}
                for r in (data.get("references") or [])
            ],
            "relatedPaths": data.get("relatedPaths") or [],
            "_file": str(yml.relative_to(REPO_ROOT)),
        }
        records.append(rec)
    return records


def coverage_for(required: list[str]) -> dict:
    """Classify a path's required-action set against existing cloudsplaining detection."""
    req_set = frozenset(required)

    # Existing PRIVILEGE_ESCALATION_METHODS, action sets.
    existing = {name: frozenset(lc(a) for a in actions) for name, actions in PRIVILEGE_ESCALATION_METHODS.items()}

    exact = [name for name, s in existing.items() if s == req_set]
    # A path is "already detectable" if some existing method is a subset of its required
    # actions (the policy granting all required actions would also satisfy that method).
    subset_existing = [name for name, s in existing.items() if s and s.issubset(req_set)]

    cred_hits = sorted(a for a in required if a in set(ACTIONS_THAT_RETURN_CREDENTIALS))

    if exact:
        status = "exact-match"
    elif subset_existing:
        # detectable today via a narrower existing method, but not as a named 1:1 method
        status = "detectable-via-existing"
    elif cred_hits and len(req_set) == len(cred_hits):
        # every required action already flagged as a credentials-returning action
        status = "covered-by-credentials-exposure"
    else:
        status = "new"

    return {
        "status": status,
        "exact_match_methods": exact,
        "subset_existing_methods": sorted(subset_existing),
        "credential_action_hits": cred_hits,
    }


def main() -> None:
    records = load_paths()

    # ----- catalog yaml -----
    catalog = {"source": "DataDog/pathfinding.cloud", "path_count": len(records), "paths": []}
    for r in records:
        cov = coverage_for(r["required_actions"])
        entry = {k: v for k, v in r.items() if not k.startswith("_")}
        entry["cloudsplaining_coverage"] = cov
        catalog["paths"].append(entry)

    catalog_path = OUT_DIR / "pathfinding-paths-catalog.yaml"
    with catalog_path.open("w") as fh:
        yaml.dump(catalog, fh, sort_keys=False, width=100, allow_unicode=True, default_flow_style=False)

    # ----- gap analysis -----
    by_status: dict[str, list[dict]] = {}
    action_universe: set[str] = set()
    for r in records:
        action_universe.update(r["required_actions"])
        cov = coverage_for(r["required_actions"])
        by_status.setdefault(cov["status"], []).append(
            {"id": r["id"], "name": r["name"], "category": r["category"],
             "required_actions": r["required_actions"], "parent": r["parent"], "coverage": cov}
        )

    # Existing actions referenced anywhere in PRIVILEGE_ESCALATION_METHODS
    existing_pe_actions = {lc(a) for actions in PRIVILEGE_ESCALATION_METHODS.values() for a in actions}
    new_actions = sorted(a for a in action_universe if a not in existing_pe_actions)

    gap = {
        "existing_pe_method_count": len(PRIVILEGE_ESCALATION_METHODS),
        "pathfinding_path_count": len(records),
        "status_counts": {k: len(v) for k, v in sorted(by_status.items())},
        "category_counts": {},
        "distinct_required_actions": sorted(action_universe),
        "required_actions_not_in_existing_pe_methods": new_actions,
        "by_status": by_status,
    }
    cat_counts: dict[str, int] = {}
    for r in records:
        cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
    gap["category_counts"] = dict(sorted(cat_counts.items()))

    gap_path = OUT_DIR / "gap-analysis.json"
    with gap_path.open("w") as fh:
        json.dump(gap, fh, indent=2)

    # ----- stdout summary -----
    print(f"Parsed {len(records)} paths from {PATHS_DIR.relative_to(REPO_ROOT)}")
    print(f"Wrote {catalog_path.relative_to(REPO_ROOT)} and {gap_path.relative_to(REPO_ROOT)}\n")
    print("Category counts:")
    for k, v in gap["category_counts"].items():
        print(f"  {k:22} {v}")
    print("\nCoverage status counts:")
    for k, v in gap["status_counts"].items():
        print(f"  {k:32} {v}")
    print(f"\nDistinct required actions across all paths: {len(action_universe)}")
    print(f"Required actions NOT already present in any PRIVILEGE_ESCALATION_METHODS entry: {len(new_actions)}")
    for a in new_actions:
        print(f"  - {a}")


if __name__ == "__main__":
    main()
