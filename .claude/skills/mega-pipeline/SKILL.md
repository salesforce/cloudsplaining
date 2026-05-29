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

### 0. Frontload ALL decisions (`AskUserQuestion`)
Gather every interactive decision up front so phases 1–10 run without stopping to ask the user. Capture and
record a run config; later phases READ it and must NOT re-prompt:
- **Techniques:** method name(s) + action list(s) to onboard (from `research/pathfinding-cloud/proposed-privilege-escalation-methods.py`), and how to handle variant supersets / noisy single-action methods (`INTEGRATION-ANALYSIS.md` §5).
- **Live-account QA:** a specific AWS profile to scan (choose from `aws configure list-profiles`) **or** "skip live". If a profile is chosen, also capture whether to **auto-wipe** the live artifacts afterward (default: yes).
- **Codex adversarial review:** detect now whether a codex adversarial-review skill is installed. If it is NOT, ask here whether to pause-and-install (recommended) or continue without it — so phase 3 never has to stop.
- **PR base branch.**

### 1. Baseline
Create a clean branch off the base, then confirm green:
```bash
just unit-tests && just type-check && just test-js
```

### 2. Implement
For each decided technique, invoke the `onboard-privesc-technique` skill (executor). No re-planning here.

### 3. Code review
Run the `code-review` skill (review-only) on the diff. Then act on the **phase-0 codex decision**: run one
codex adversarial-review pass if it is available, otherwise skip with a ⚠️ note. Do NOT prompt here — the
install-or-skip choice was already made in phase 0.

### 4. Bug hunt
Run the `find-bugs` skill on the branch diff.

### 5. Security review
Run the `security-review` skill on the pending changes. Cloudsplaining is itself a security tool, so a dedicated
security pass over the diff (injection, unsafe parsing/eval, secret handling, path traversal, etc.) is warranted
before shipping.

### 6. Simplify
Run the `simplify` skill to apply reuse / simplification / efficiency / altitude cleanups to the changed code
(quality only — it does NOT hunt for bugs; that is phases 3-5). Because `simplify` MUTATES the working tree,
re-run the baseline afterward and confirm green:
```bash
just unit-tests && just type-check && just test-js
```

### 7. Example-data QA
Run the `report-regression-check` skill (snapshot → `just generate-report` → `just compare-reports` → dogfood).
It must show findings ADDED and none removed.

### 8. Live-account QA (opt-in)
Only if a profile was chosen in phase 0: run the `scan-live-account` skill, **passing it the phase-0 profile and
auto-wipe choice** so it does not re-prompt. It QAs via `qa-report` and wipes its output per that choice.

### 9. Pre-push safety gate
```bash
just safety-scan
```
Must exit 0; fail closed otherwise.

### 10. PR
Push the branch and open a PR with `gh pr create --base <base>` — NEVER `main` directly. Optionally run the
`iterate-pr` skill to drive CI/feedback green.

## Termination

Findings from phases 3/4/5/7/8 route back to phase 2 (re-implement) or phase 6 (re-simplify). After at most 2
iterations with unresolved findings, STOP and surface them via `AskUserQuestion` rather than looping further.
