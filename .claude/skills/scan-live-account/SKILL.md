---
name: scan-live-account
description: Run cloudsplaining against a REAL AWS account for QA, writing all output to a gitignored directory and never committing live data. This skill should be used to validate detections end-to-end against real IAM data. It selects an AWS profile interactively, forces output under .live-scans/, QAs the report, and wipes the output afterward.
allowed-tools: Bash(uv run:*), Bash(just:*), Bash(mkdir:*), Bash(git check-ignore:*), Bash(aws configure list-profiles), Read
---

# Scan Live Account

Run a real-account cloudsplaining scan for QA. Real IAM data (account IDs, ARNs, policy
documents) is sensitive and must NEVER be committed.

## Safety invariants (read first)

- All output goes under `.live-scans/<profile>-<timestamp>/`, which is gitignored.
- Confirm `.live-scans/` is gitignored before writing anything.
- Never `git add -f` anything under `.live-scans/` or `dogfood-output/`.
- Wipe the output directory when done (mandatory teardown).
- Browser QA screenshots/videos of a live report contain sensitive data — keep them inside the
  gitignored directory and wipe them too.

## Workflow

1. **Select profile.** Run `aws configure list-profiles` and use `AskUserQuestion` to let the user pick
   one (offer a cancel option). Never hardcode credentials.
2. **Compute and guard the output dir** (use the shell for the timestamp):
   ```bash
   OUT=".live-scans/${PROFILE}-$(date +%Y%m%d-%H%M%S)"
   mkdir -p "$OUT"
   git check-ignore -q "$OUT" || { echo "ABORT: $OUT is not gitignored"; exit 1; }
   ```
3. **Download + scan** (verify exact flags against `uv run cloudsplaining download --help` / `scan --help`):
   ```bash
   uv run cloudsplaining download --profile "$PROFILE" --output "$OUT/authz.json"
   uv run cloudsplaining scan --input-file "$OUT/authz.json" --output "$OUT"
   ```
4. **QA.** Hand the generated report (`file://$PWD/$OUT/<report>.html`) to the `qa-report` skill, directing
   its artifacts inside `$OUT/dogfood/`.
5. **Mandatory teardown.** Use `AskUserQuestion` to confirm wiping `$OUT`. On yes, wipe via Python (the
   `Bash(rm -rf *)` deny rule blocks `rm -rf`):
   ```bash
   uv run python -c "import shutil,sys; shutil.rmtree(sys.argv[1])" "$OUT"
   ```
   Warn that any retained screenshots/videos contain sensitive data.

## Notes

- This skill produces NO committable artifacts; its value is the QA signal, not files.
- If the account is large, the scan can be slow — that is expected.
