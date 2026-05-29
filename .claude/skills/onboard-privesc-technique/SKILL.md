---
name: onboard-privesc-technique
description: Add a single AWS IAM privilege-escalation technique (e.g. from pathfinding.cloud) to cloudsplaining's detection. This skill should be used when the method name and required action list are already decided — it is a pure executor, not a planner. It updates constants.py with TDD, regenerates fixtures with a regression check, and updates the docs.
allowed-tools: Bash(uv run:*), Bash(just:*), Bash(git add:*), Bash(git commit:*), Edit, Read, Write
---

# Onboard Privilege-Escalation Technique

Add one privilege-escalation method to `cloudsplaining/shared/constants.py` and wire up its test,
fixtures, and docs. This is an EXECUTOR: the method name and action list are inputs (decided upstream
by `triage-github-issue` or `mega-pipeline` phase 0). Do no planning here.

## Inputs

- A PascalCase method name, e.g. `PassExistingRoleToNewECSService`.
- A list of exact lowercase IAM actions, e.g. `["iam:passrole", "ecs:registertaskdefinition", "ecs:createservice"]`.
  Source: `research/pathfinding-cloud/proposed-privilege-escalation-methods.py`.
- The originating pathfinding path id (for the docs link), if any.

(Below, `ACTIONS` denotes that action list.)

## Workflow (strict TDD)

1. **Verify policy_sentry recognizes every action.** Wildcard expansion only works for known actions:
   ```bash
   uv run python -c "from policy_sentry.querying.all import get_all_actions; known={a.lower() for a in get_all_actions()}; missing=[a for a in ACTIONS if a.lower() not in known]; import sys; print('MISSING: '+', '.join(missing)) if missing else print('all actions known')"
   ```
   If any action is missing, STOP — the policy_sentry datastore may need updating.

2. **Idempotency guard.** `grep -n "<MethodName>" cloudsplaining/shared/constants.py` and confirm no
   existing entry already has the same action set. If present, skip — already onboarded.

3. **RED — failing test first.** In `test/scanning/test_policy_document.py` (inside `TestPolicyDocument`),
   add a test: a policy granting exactly `ACTIONS` on `Resource: "*"` must yield
   `[{"type": "<MethodName>", "actions": ACTIONS}]` from `allows_privilege_escalation`. Run it; watch it FAIL.

4. **GREEN.** Append the entry to `PRIVILEGE_ESCALATION_METHODS` (or `ACTIONS_THAT_RETURN_CREDENTIALS` for
   credential-returning paths) in `cloudsplaining/shared/constants.py`. Re-run the test; it PASSES.

5. **Fix brittle assertions.** Adding a method can break tests that assert an exact privesc list for a policy
   whose actions are a superset of the new method. Run `just unit-tests`; for each failure, prefer converting
   the exact-list assertion to membership (`self.assertIn(expected_finding, results)`) rather than appending.
   See `research/pathfinding-cloud/INTEGRATION-ANALYSIS.md` §4c for the known list.

6. **Regenerate + regression-check.** Use the `report-regression-check` skill (snapshot → `just generate-report`
   → `just compare-reports` → dogfood). Confirm the new method's findings are ADDED and nothing is removed.
   Then `just test-js`; update `inline-policies-test.js` `expectedResult` only if it legitimately changed.

7. **Docs.** Add the technique to `docs/glossary/privilege-escalation.md` with its pathfinding.cloud link.

8. **Verify + commit.** `just unit-tests && just type-check && just test-js` all green; `just safety-scan`
   clean. Commit locally (no push).

## Notes

- Action lists must be exact lowercase `service:action` strings (matching policy_sentry's wildcard expansion).
- Method names become the finding `type` and a readthedocs URL anchor — keep PascalCase, matching existing entries.
- Skip "variant" combinations that are supersets of an existing method (they produce duplicate findings); see
  `INTEGRATION-ANALYSIS.md` §5.1.
