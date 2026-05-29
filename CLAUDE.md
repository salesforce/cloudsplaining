# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Cloudsplaining is an AWS IAM security assessment tool. It parses the output of `aws iam get-account-authorization-details`, identifies IAM policy violations of least privilege, and generates a risk-prioritized single-file HTML report. It uses [policy_sentry](https://github.com/salesforce/policy_sentry) for IAM action analysis.

## Commands

Uses [uv](https://docs.astral.sh/uv/) for Python and [just](https://github.com/casey/just) as the task runner.

```bash
uv sync --frozen          # Install dependencies
just unit-tests           # Run pytest with coverage
just type-check           # Run ty type checker
just build-package        # Build the Python package
just build-js             # Build Vue.js frontend (generates report assets)
just serve-js             # Dev server for the Vue.js report UI
just test-js              # Run mocha tests for the frontend
just generate-report      # Generate example IAM data + HTML report
just lint                 # Run CI's format/lint hooks; auto-fixes formatting in place
just pre-push             # Full local CI-equivalent gate; run before every push
```

Single test: `uv run pytest test/scanning/test_policy_document.py::TestPolicyDocument::test_method -v`

Lint: `just lint` runs the same hooks CI runs via `prek` (actionlint, `ruff-check`, `ruff-format`, `just fmt`). Note `ruff-format` and `just fmt` run on the **whole repo** (not just `cloudsplaining/`), so files under `.claude/`, `research/`, `utils/`, `test/`, and the `justfile` itself must be formatted too.

## Architecture

The tool has two halves: a **Python CLI** that scans IAM data and a **Vue.js SPA** that renders the HTML report.

### Python Side (`cloudsplaining/`)

- **`bin/cli.py`** - Click CLI entrypoint. Registers all subcommands.
- **`command/`** - Click subcommands: `download` (fetch IAM data from AWS), `scan` (analyze an authorization details JSON file and produce the HTML report), `scan_policy_file` (scan a single policy), `scan_multi_account`, `create_exclusions_file`, `expand_policy`.
- **`scan/`** - Core analysis engine. The class hierarchy mirrors AWS IAM structure:
  - `AuthorizationDetails` - top-level, holds the full account's IAM data
  - `ManagedPolicyDetails`, `RoleDetailList`, `UserDetailList`, `GroupDetailList` - collections of IAM principals/policies
  - `PolicyDocument` → `StatementDetail` - per-statement analysis. `StatementDetail` uses policy_sentry to expand wildcards, classify access levels, and flag risky patterns (privilege escalation, data exfiltration, resource exposure, infrastructure modification).
- **`output/`** - `HTMLReport` injects scan results as a `var iam_data = ...` JSON blob into a Jinja2 template alongside the compiled Vue.js bundle, producing a self-contained HTML file. `PolicyFinding` structures per-policy results with severity classification.
- **`shared/`** - `Exclusions` (YAML-driven allowlist/denylist for filtering results), `constants.py` (risk definitions, privilege escalation methods, data exfiltration actions), validation schemas.

### Vue.js Side (`cloudsplaining/output/src/`)

Vue 3 + Bootstrap + Chart.js. The report reads `iam_data` from the global scope (injected by Python). Utility modules in `src/util/` transform raw data for each report section. Built output goes to `cloudsplaining/output/dist/` and is committed to the repo.

The `vue.config.js` inlines all JS/CSS into the HTML via a custom `InlineSourcePlugin` so the report is a single file with no external dependencies (unless `--minimize` is used, which loads from CDN instead).

### Key Design Decisions

- **policy_sentry dependency**: All IAM action metadata (access levels, resource types, condition keys) comes from policy_sentry. Module-level calls like `get_all_actions()` and `get_all_service_prefixes()` run at import time.
- **Exclusions system**: YAML config controls what to skip. Supports glob patterns for roles/users/groups/policies and explicit include/exclude action lists. Default exclusions live in `shared/default-exclusions.yml`.
- **Risk categories**: Findings are classified as PrivilegeEscalation, DataExfiltration, ResourceExposure, InfrastructureModification, or CredentialsExposure. Definitions are in `shared/constants.py`.

## Testing

Tests live in `test/` mirroring the source layout. Test fixtures (JSON files with sample IAM data) are in `test/files/`. Tests use `moto` for mocking AWS API calls. Node 20 for frontend tests.

## Pipeline & Safety Standards

- **Never push to `main`.** Always branch + open a PR.
- **TDD:** no production code without a failing test first.
- **Never commit real-AWS scan outputs or credentials.** Live scans go to gitignored `.live-scans/`; browser QA artifacts to gitignored `dogfood-output/`; report snapshots to `.report-snapshots/`. Never `git add -f` them.
- **Run `just pre-push` before every push.** It is the full local CI-equivalent gate (`lint` → `unit-tests` → `type-check` → `test-js` → `safety-scan`) and catches the failures CI would: unformatted files, lint/type errors, broken JS tests, and leaked secrets. The git pre-commit hook is not installed by default, so nothing auto-formats on commit — run `just lint` (or `just pre-push`) yourself, or `uvx pre-commit install` once to enable the hook.
- **`just safety-scan`** (also part of `pre-push`) fails closed on AWS keys/tokens/account IDs in staged or tracked files.
- **Use `just` tasks** (`unit-tests`, `type-check`, `test-js`, `generate-report`, `build-js`, `lint`, `pre-push`, `safety-scan`, `compare-reports`) — don't hand-roll equivalents.
- **After changing `PRIVILEGE_ESCALATION_METHODS` / constants:** verify policy_sentry recognizes the new actions, guard against duplicate dict keys, regenerate fixtures with `just generate-report`, run `just test-js`, run the report regression check, and update `docs/glossary`.
- **`sampleData.js` and `example-iam-data.json` must stay in sync** — both are generated by `just generate-report`; `just check-sampledata-sync` (test `test/test_sample_data_in_sync.py`) enforces it.
- **The example dataset is enriched.** `examples/files/example.json` combines realistic IAM data with the small teaching entities (`obama`, `userwithlotsofpermissions`, `admin`/`biden` groups, `MyRole`, etc.) the mocha tests assert against. `utils/build_example_dataset.py` merges the teaching overlay (`test/files/example-authz-details.json`) into it (idempotent, dedups by name/Arn). Re-run it if `example.json` is ever rebuilt from a fresh realistic source, then `just generate-report`.
- **Prefer membership assertions** over exact-list assertions in privilege-escalation tests.
- **Skills** live in `.claude/skills/`; keep `skills-lock.json` in sync; don't edit vendored skills in place — wrap them.
- Pin dependency versions with `==`. Skill helper scripts use `uv run`.
