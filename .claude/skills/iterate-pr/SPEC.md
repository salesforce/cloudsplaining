# Iterate PR Specification

## Intent

The `iterate-pr` skill drives a pull request through actionable CI failures and actionable review feedback until the work is locally fixed, pushed, and rechecked.

Its purpose is CI and feedback iteration, not merge readiness. It must not wait indefinitely for human approvals, required review decisions, draft PR state changes, or other gates that an agent cannot resolve by editing code.

## Scope

In scope:

- Identifying the PR for the current branch.
- Fetching and categorizing PR review feedback.
- Fixing high and medium priority review feedback.
- Asking the user which low priority suggestions to address.
- Fetching CI checks, failed logs, and failure snippets.
- Fixing CI failures with local verification before pushing.
- Monitoring checks until they pass, fail, or reach a non-actionable stop state.
- Reporting draft/no-checks and human review/approval gates without polling forever.

Out of scope:

- Waiting for or requesting human approval.
- Marking draft PRs ready for review unless the user explicitly asks.
- Merging PRs.
- Rebasing branches without user direction.
- Treating Codecov, Dependabot, or other informational comments as review feedback.

## Users And Trigger Context

- Primary users: engineers and coding agents iterating on existing pull requests.
- Common user requests: fix CI on this PR, iterate on this PR until checks pass, address PR feedback, keep pushing fixes until green.
- Should not trigger for: creating a PR, writing commits without a PR, reviewing unrelated code, or monitoring merge approval state only.

## Runtime Contract

- Required first actions: resolve the current PR, read `isDraft` and `reviewDecision`, fetch current review feedback, and fetch current CI state before editing.
- Required outputs: concise progress updates, commits and pushes when fixes are made, and a final state that distinguishes passing CI from non-actionable review/draft/approval gates.
- Non-negotiable constraints: investigate failures before editing, verify locally before pushing, do not push known-broken fixes, do not wait for human approval, and do not treat draft PRs with no checks as pending forever.
- Expected bundled files loaded at runtime: `SKILL.md` and, when needed, scripts under `scripts/`.

## Source And Evidence Model

Authoritative sources:

- GitHub CLI PR and checks output.
- Sentry LOGAF review guidance.
- Repository-level agent instructions.
- Bundled script behavior documented in `SKILL.md`.

Useful improvement sources:

- positive examples: PRs where CI failures were fixed and checks passed after the loop.
- negative examples: PRs where the agent waited on draft status, required review, or approval gates.
- issue or PR feedback: reviewer comments about missing fixes, false positives, or feedback categorization.
- validation results: structural skill validation and script syntax checks.

Data that must not be stored:

- secrets
- customer data
- private URLs or identifiers not needed for reproduction
- full CI logs when small failure snippets are enough

## Reference Architecture

- `SKILL.md` contains the runtime workflow, script contracts, feedback handling rules, CI loop, and exit conditions.
- `SPEC.md` contains this maintenance contract.
- `references/` contains no files currently; add focused troubleshooting or evidence references only if runtime guidance becomes noisy.
- `references/evidence/` contains no files currently; use it for durable positive or negative PR-loop examples if regressions recur.
- `scripts/` contains non-interactive helpers for PR checks, PR feedback, check monitoring, and review-thread replies.
- `assets/` contains no files currently.

## Validation

- Lightweight validation: run `uv run skills/skill-writer/scripts/quick_validate.py skills/iterate-pr`.
- Script validation: run `uv run -m py_compile skills/iterate-pr/scripts/*.py` after script changes.
- Holdout examples: include a draft PR with no registered checks, a PR with `reviewDecision: REVIEW_REQUIRED` but passing checks, a PR with an actionable pending CI bot check, and a PR with failed CI logs.
- Acceptance gates: validator passes, scripts compile, draft/no-check states terminate with a report, human review gates are not treated as actionable pending CI, and actionable CI failures still route back to investigation and fixes.

## Known Limitations

- Human-gate detection depends on check names, states, and descriptions exposed by GitHub or CI integrations.
- Some repositories may intentionally model deployment or approval workflows as status checks; this skill reports those as blocked/non-actionable unless the user asks to manage that gate.
- The helper scripts use GitHub CLI output and can drift if `gh pr checks` changes its JSON schema.

## Maintenance Notes

- Update `SKILL.md` when the runtime loop, script contracts, feedback policy, or exit conditions change.
- Update `SPEC.md` when the skill's scope, validation expectations, or non-actionable gate policy changes.
- Add focused reference files only when repeated troubleshooting guidance would make `SKILL.md` hard to scan.
- Keep public inventories pointed at the canonical `skills/iterate-pr` skill, not mirrors or aliases.
