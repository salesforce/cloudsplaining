---
name: triage-github-issue
description: Take a GitHub issue or proposal, research it against this repo, frame 2-3 options, and help the user decide — then emit a plan and optionally launch the mega-pipeline. This skill should be used to turn an incoming proposal (e.g. a pathfinding.cloud privesc path) into a decided, planned, ready-to-execute change.
allowed-tools: Bash(gh issue view:*), Bash(gh api:*), Bash(uv run:*), Bash(just:*), Read, Write
---

# Triage GitHub Issue

Turn a proposal into a decision plus a plan, then hand off to execution.

## When to use

- A GitHub issue proposes a change (e.g. "add these pathfinding.cloud techniques").
- The user wants help deciding scope/approach before building.

## Workflow

1. **Fetch the issue.** `gh issue view <n> --json title,body,labels,comments` (or accept the proposal text directly).
2. **Research context.** Read the relevant code/docs. For privesc proposals: `cloudsplaining/shared/constants.py`,
   `research/pathfinding-cloud/INTEGRATION-ANALYSIS.md`, and `research/pathfinding-cloud/proposed-privilege-escalation-methods.py`.
   Determine what is already covered vs new (the analysis already classifies this).
3. **Frame options.** Use the `superpowers:brainstorming` skill to develop 2-3 concrete approaches with trade-offs
   (which techniques to onboard first, how to handle variant supersets and noisy single-action methods, whether to
   refresh fixtures now).
4. **Decide.** Use `AskUserQuestion` for each genuine decision; record the choices.
5. **Plan.** Write a short decision summary + step plan to the configured plans directory (`docs/plans/`).
6. **Hand off.** Offer to run the `mega-pipeline` skill with the decided technique list, or stop at the plan.

## Notes

- This skill decides and plans; it does not implement. Implementation is `mega-pipeline` → `onboard-privesc-technique`.
- Keep decisions frontloaded so `mega-pipeline` can run with minimal gates.
