---
name: mega-pipeline
description: Closed-loop pipeline that takes a decided change (e.g. onboarding a pathfinding.cloud privilege-escalation technique) through implementation, code review, bug-hunt, report QA (example data and optionally a real AWS account), a pre-push safety scan, and a PR — never pushing to main. This skill should be used to drive a privesc-onboarding change end-to-end with minimal mid-run gates.
allowed-tools: Bash(just:*), Bash(uv run:*), Bash(git add:*), Bash(git commit:*), Bash(git checkout:*), Bash(git switch:*), Bash(git push:*), Bash(gh pr create:*), Edit, Read, Write
---

# Mega Pipeline

A closed loop for shipping a cloudsplaining change safely, tuned for onboarding
pathfinding.cloud privilege-escalation techniques. NEVER pushes to `main`; ends at a PR.

## Principles

- **Frontload decisions** (phase 0) so the loop runs with minimal interruptions.
- **Pure executor inside** — planning happens in phase 0 / `triage-github-issue`, not mid-loop.
- **Fail-closed safety** before any push.
- **Bounded** — at most 2 feedback iterations, then surface to the user.

## Phases

### 0. Frontload decisions (`AskUserQuestion`)
Gather everything up front: which technique(s) to onboard (method name(s) + action list(s) from
`research/pathfinding-cloud/proposed-privilege-escalation-methods.py`), how to handle variant supersets and
noisy single-action methods (`INTEGRATION-ANALYSIS.md` §5), AWS profile or "skip live", and the PR base branch.

### 1. Baseline
Create a clean branch off the base, then confirm green:
```bash
just unit-tests && just type-check && just test-js
```

### 2. Implement
For each decided technique, invoke the `onboard-privesc-technique` skill (executor). No re-planning here.

### 3. Code review
Run the `code-review` skill (review-only) on the diff. Then check for a codex adversarial-review skill:
- If installed, run one adversarial pass.
- If NOT, use `AskUserQuestion`: "Pause to install codex adversarial review first (recommended — it
  materially improves results) or continue without it?" Honor the choice.

### 4. Bug hunt
Run the `find-bugs` skill on the branch diff.

### 5. Example-data QA
Run the `report-regression-check` skill (snapshot → `just generate-report` → `just compare-reports` → dogfood).
It must show findings ADDED and none removed.

### 6. Live-account QA (opt-in)
If a profile was chosen in phase 0, run the `scan-live-account` skill (it QAs via `qa-report` and wipes its output).

### 7. Pre-push safety gate
```bash
just safety-scan
```
Must exit 0; fail closed otherwise.

### 8. PR
Push the branch and open a PR with `gh pr create --base <base>` — NEVER `main` directly. Optionally run the
`iterate-pr` skill to drive CI/feedback green.

## Termination

Findings from phases 3/4/5/6 route back to phase 2. After at most 2 iterations with unresolved findings, STOP
and surface them via `AskUserQuestion` rather than looping further.
