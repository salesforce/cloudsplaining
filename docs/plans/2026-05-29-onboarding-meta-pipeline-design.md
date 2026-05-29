# Design — pathfinding.cloud onboarding meta-pipeline (v2, post-critique)

> Status: **APPROVED v2 (post-critique). Proceeding to writing-plans.**
> Date: 2026-05-29

## Goal

A closed-loop "meta-pipeline" of Claude skills (in `.claude/skills/`) that takes a proposal — e.g. a
[pathfinding.cloud](https://github.com/DataDog/pathfinding.cloud) privilege-escalation path — and drives
it end-to-end: frontload decisions → baseline tests → implement (TDD, executor) → code review → bug hunt
→ report generation + browser QA (example data **and**, optionally, a real AWS account) → pre-push safety
scan → PR. **Never pushes to main.** First application: onboarding pathfinding.cloud techniques into
cloudsplaining.

## Locked decisions (from user)

1. **Scope:** cloudsplaining-tuned, phases structured for later reuse.
2. **Browser QA:** QA the example-data report, **and** run + QA against a real AWS account (profile via
   `AskUserQuestion`). **Never commit real-account artifacts.**
3. **Autonomy:** frontload decisions; minimal mid-run gates; secret + AWS-account-ID + credential scan before push.
4. **PR strategy:** #580 ships first standalone; everything else (skills + CLAUDE.md + docs) in one mega PR;
   technique *data* additions happen afterward, produced by the pipeline.

## Critique resolutions (what changed in v2)

| Critique finding | Resolution in v2 |
|---|---|
| Live-account report/screenshots leak real IAM data; gitignore insufficient | Hardened safety model (below): forced output paths, `just safety-scan` over `.live-scans/` + tracked + staged, mandatory wipe-with-confirmation, screenshot/env-var warnings |
| Nesting `brainstorming`/`writing-plans` in an autonomous loop is a category error | Inner skill is a pure **executor**; all planning is frontloaded (phase 0 / `triage-github-issue`) |
| Over-fragmentation (9 new skills) | Lean to **3 core skills + 2 thin orchestrators**; safety scan becomes a `just` recipe; docs/example-data folded into the executor |
| JS tests + 8 brittle assertions unmodeled | `just test-js` in baseline; explicit fixture-regen + assertion-fix + `policy_sentry` coverage + idempotency steps |
| Undefined loop termination | Max 2 feedback iterations, then surface via `AskUserQuestion`; exit when no new ≥medium findings |
| `codex:adversarial-review` doesn't exist | Use **`code-review`** (review-only); then detect a codex adversarial-review skill — if absent, `AskUserQuestion` to pause+install (recommended; plans are substantially better with it) vs continue |
| MVP: cut `mega-pipeline`/`triage-github-issue` | **Overridden per user** — kept, but built thin on the executor core |

## Skill architecture (`.claude/skills/`)

**Tier 0 — vendored (present):** `agent-browser`, `dogfood`, `find-bugs`, `iterate-pr`. Don't edit in place.

**Core skills (new — built first):**
- `onboard-privesc-technique` — **executor** (no planning). Given a technique id (e.g. `ecs-001`): verify
  `policy_sentry` recognizes its actions; guard against duplicate dict keys (idempotency); append entry to
  `PRIVILEGE_ESCALATION_METHODS` (or `ACTIONS_THAT_RETURN_CREDENTIALS`) in `constants.py`; write a
  failing-first TDD unit test; fix any brittle exact-list assertions (prefer membership assertions);
  run `just generate-report` + `just test-js`, updating `sampleData.js`-driven `expectedResult`; update
  `docs/glossary/privilege-escalation.md`.
- `qa-report` — open a generated report (`file://` or `just serve-js`) and run `dogfood`, scoped to the
  PrivilegeEscalation section.
- `scan-live-account` — `cloudsplaining download` + `scan` for an `AskUserQuestion`-selected AWS profile,
  forcing output into `.live-scans/<profile>-<ts>/`; asserts the path is gitignored before running.
- `report-regression-check` — snapshot the old example report, regenerate, then diff OLD vs NEW
  **deterministically** (`utils/compare_example_reports.py`, fail on dropped findings) **and via dogfood**
  (visual/semantic comparison) so regenerating fixtures never silently loses findings. Added after Phase 0
  revealed the committed fixtures are ~75k lines stale.

**Orchestrators (new — thin, via `/skill-creator` + `/skill-review`):**
- `mega-pipeline` — composes the phases below.
- `triage-github-issue` — front door: fetch issue → research → frame options → `AskUserQuestion` decisions →
  plan in `docs/plans/` → optionally invoke `mega-pipeline`.

**New `just` recipe (not a skill):** `just safety-scan` — secret + AWS-account-ID + credential scan.

## `mega-pipeline` phases

0. **Frontload** — `AskUserQuestion`: which technique(s) (and how to handle the 4 variant supersets /
   noisy single-action methods per INTEGRATION-ANALYSIS.md §5), AWS profile or "skip live", PR target branch.
1. **Baseline** — `just unit-tests` + `just type-check` + **`just test-js`** all green before changes.
2. **Implement** — invoke `onboard-privesc-technique` (executor; plan already decided).
3. **Code review** — `code-review` skill (review-only). Then detect whether a codex adversarial-review skill is
   installed; if **not**, `AskUserQuestion`: pause to install it first (recommended — our experience shows plans
   are substantially better when checked through it) or continue without. If installed, run one adversarial pass.
4. **find-bugs** — on the branch diff.
5. **Example-data QA** — `just generate-report` → open report → `qa-report`/`dogfood`.
6. **Live-account QA (opt-in)** — if a profile was chosen: `scan-live-account` → `qa-report` → **wipe
   `.live-scans/` with confirmation**. Never commit.
7. **Pre-push safety gate** — `just safety-scan` (AKIA/ASIA keys, 40-char secrets, session tokens, 12-digit
   account IDs; scans staged + tracked + `.live-scans/`). Fail closed.
8. **PR** — branch + PR (never main); optional `iterate-pr`.
**Termination:** findings in 3/4/5/6 route back to phase 2, max 2 iterations, then `AskUserQuestion`.

## Safety & secrets (hardened)

- Forced paths: live scans → `.live-scans/<profile>-<ts>/`; dogfood artifacts for live runs → inside that dir.
- `.gitignore`: `CLAUDE.local.md`, `.live-scans/`, `dogfood-output/`.
- `just safety-scan` scans staged + tracked files **and** `.live-scans/`; fails closed on any hit. Never `git add -f`.
- Mandatory phase-6 wipe of `.live-scans/` with `AskUserQuestion` confirmation.
- Warnings: dogfood screenshots/videos of a live report contain sensitive data (image content, regex can't
  catch — keep in gitignored dir, wipe after); env-var creds (`AWS_ACCESS_KEY_ID`) are process-scoped, not file-scanned.
- AWS profile via `AskUserQuestion` over `aws configure list-profiles`; never hardcode creds.

## CLAUDE.md standards (proposed)

Never push to `main` (branch + PR). TDD (failing test first). Never commit real-AWS outputs/creds (gitignored
`.live-scans/`; never `git add -f`). Run `just safety-scan` before every push. Use `just` tasks
(`unit-tests`, `type-check`, `test-js`, `generate-report`, `build-js`). After constants changes: regenerate
fixtures via `just generate-report` + run `just test-js`; verify `policy_sentry` recognizes new actions;
guard against duplicate dict keys; update `docs/glossary`. Prefer membership over exact-list assertions in
privesc tests. Skills live in `.claude/skills/`; keep `skills-lock.json` in sync; don't edit vendored skills
in place. Don't mention Claude in commits/PRs. Pin deps with `==`. Skill scripts use `uv run`.

## docs updates

`docs/glossary/privilege-escalation.md` → reference pathfinding.cloud as source of truth + cross-link new
techniques. Docs updates are part of **both planning and execution** for every technique onboarded.

## PR plan

- **PR A:** #580 sts:assumerole fix (small, first).
- **PR B (mega):** skills (vendored + 3 core + 2 orchestrators) + `just safety-scan` + CLAUDE.md + `.gitignore`
  + docs. No technique data changes.
- **PR C:** refresh + lock the example fixtures for a high-quality demo report (Phase 6) — re-sync
  `sampleData.js` with `example-iam-data.json` via `just generate-report`, add a drift-prevention test,
  repair the JS mocha tests, dogfood-QA. Large diff, kept separate.
- **Subsequent PRs:** produced by `mega-pipeline` as techniques are onboarded.

## MVP alternative (critic's recommendation, for reference)

If we later decide the orchestrators are overkill: keep only the 3 core skills + `just safety-scan`, and
document the pipeline sequence as a CLAUDE.md procedure instead of `mega-pipeline`/`triage-github-issue`.
We are **not** taking this path now (user wants the orchestrator skills), but it's the documented fallback.
