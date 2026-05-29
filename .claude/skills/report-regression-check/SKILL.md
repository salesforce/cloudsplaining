---
name: report-regression-check
description: Verify that regenerating cloudsplaining's example report does not silently drop findings. This skill should be used after changing PRIVILEGE_ESCALATION_METHODS or other constants, after editing examples/files/example.json, or before refreshing the committed example fixtures. It snapshots the current report, regenerates, runs a deterministic finding diff, and performs a dogfood visual comparison, failing if any finding disappeared.
allowed-tools: Bash(just:*), Bash(uv run:*), Bash(mkdir:*), Bash(cp:*), Bash(agent-browser:*), Read
---

# Report Regression Check

Regenerating `cloudsplaining`'s example fixtures (`utils/example-iam-data.json` and
`cloudsplaining/output/src/sampleData.js`) is easy to do but risky: a stale or wrongly
configured run can silently DROP findings. This skill guards against that. Additions are
expected (new techniques get onboarded); removals are regressions and must block.

## When to use

- After changing `cloudsplaining/shared/constants.py` (e.g. `PRIVILEGE_ESCALATION_METHODS`).
- After editing `examples/files/example.json`.
- Before committing any refresh of the committed example fixtures.

## Workflow

### 1. Snapshot the current (old) report

```bash
mkdir -p .report-snapshots/old
cp utils/example-iam-data.json .report-snapshots/old/example-iam-data.json
cp index.html .report-snapshots/old/index.html 2>/dev/null || true
```

`.report-snapshots/` is gitignored — never commit it.

### 2. Regenerate

```bash
just generate-report
```

This rewrites `utils/example-iam-data.json` and `cloudsplaining/output/src/sampleData.js`
from `examples/files/example.json`.

### 3. Deterministic diff (fails on dropped findings)

```bash
just compare-reports .report-snapshots/old/example-iam-data.json utils/example-iam-data.json
```

- Exit 0 → no findings dropped (any additions are listed and are fine).
- Exit 1 → a finding disappeared. STOP and investigate before committing: either the
  regeneration is wrong, or the change legitimately removes a detection (rare — confirm it
  is intentional and note it).

### 4. Dogfood visual comparison

Catch anything the deterministic diff cannot (layout, per-category counts, missing
principals/policies). Use the `dogfood` skill against the freshly generated report
(the regenerated root `index.html` via a `file://` URL), with scope:

> "Confirm every risk-category section renders, per-category finding counts are at least
> as high as the old report in `.report-snapshots/old/`, and no principals or policies
> present in the old report are missing from the new one."

### 5. Summarize

Report findings added, findings removed (should be zero), and the dogfood result. If
step 3 exited non-zero or dogfood found missing data, the regeneration is NOT safe to commit.

## Notes

- The deterministic diff keys findings by `(json-path, finding-id)` and is reliable for
  incremental regenerations (policy IDs in `example.json` are stable). If `example.json`
  itself is restructured so IDs change, everything appears added/removed — review manually.
- This skill never commits the `.report-snapshots/` snapshots.
- See `utils/compare_example_reports.py` for the diff implementation.
