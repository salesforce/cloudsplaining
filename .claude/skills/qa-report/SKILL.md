---
name: qa-report
description: Open a generated cloudsplaining HTML report and QA it with the dogfood skill, focused on the Privilege Escalation findings. This skill should be used to visually verify a report renders correctly after onboarding a new technique or refreshing fixtures. It writes browser artifacts to a gitignored directory and never persists auth state.
allowed-tools: Bash(agent-browser:*), Bash(just:*), Bash(mkdir:*), Read
---

# QA Report

Visually QA a generated cloudsplaining report in a browser via the `dogfood` skill.

## When to use

- After `just generate-report` or `scan-live-account`, to confirm the report renders correctly.
- As the QA leg of `report-regression-check` and `mega-pipeline`.

## Inputs

- A report to open, one of:
  - a local file, e.g. the generated report `file:///<abs path>/index.html` (from `just generate-report`) or a `cloudsplaining scan -o <dir>/` output
  - the dev server: `just serve-js` (serves the Vue report at the printed localhost URL)
- An output directory for browser artifacts. Default to a **gitignored** location:
  - example-data runs → `dogfood-output/`
  - live-account runs → inside the scan's `.live-scans/<...>/dogfood/` directory

## Workflow

1. Ensure the report exists (`just generate-report` for example data, or it was produced by `scan-live-account`).
2. Invoke the `dogfood` skill against the report URL. Pass:
   - **Output directory:** the gitignored path above, so screenshots/videos never land in tracked paths.
   - **Scope:** "Focus on the Privilege Escalation section: every finding's method name (`type`) and its IAM `actions` render; the readthedocs links resolve; severity badges and per-category counts are correct; the summary chart matches the findings."
3. Do NOT run `agent-browser ... state save` or persist `auth-state.json` — the report is static and needs no login.
4. Summarize the dogfood findings (rendering bugs, missing data) and where the artifacts were written.

## Notes

- Never write browser artifacts into tracked repo paths. `dogfood-output/` and `.live-scans/` are gitignored.
- For a regression comparison of old vs new reports, use the `report-regression-check` skill (which calls this one).
