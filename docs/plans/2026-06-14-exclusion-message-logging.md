# Plan: route "Excluded prefix/suffix" messages through logging (quiet as a library, unchanged as a CLI)

> **Review status:** two-pass reviewed.
> 1. **Opus fact-check** (verdict **yes-with-fixes**): confirmed root cause, trigger paths,
>    the `download` claim, the CLI chokepoint, import-graph safety, and "no existing test
>    breaks." Its three fixes (autouse test-isolation fixture, corrected `cli.py` wiring,
>    tightened `PolicyDocument` attribution) are folded in.
> 2. **Codex adversarial review** (verdict **needs-attention**): flagged that the v1 design
>    left the CLI toggle as **sticky process-global state**, which leaks back into library
>    mode after in-process CLI use. Fixed in v2 — the toggle is now **scoped to the CLI
>    invocation and restored** via `ctx.call_on_close()`, with a dedicated embedded-CLI
>    regression test (see Change 2 and TDD item 5).

## Problem

When cloudsplaining is used **as a library** — parsing `get-account-authorization-details`
output via `AuthorizationDetails(...)`, constructing `PolicyDocument`, `RoleDetailList`,
`ManagedPolicyDetails`, etc. — it leaks lines like:

```
	Excluded prefix: /aws-service-role*
	Excluded suffix: ...
```

directly to stdout. These bypass the logging system entirely, so a library consumer
cannot silence them through standard `logging` configuration.

## Root cause

`cloudsplaining/shared/exclusions.py::is_name_excluded()` has three match branches that
are **inconsistent**:

| Line (approx) | Case            | Current emit                         |
|---------------|-----------------|--------------------------------------|
| 151           | exact match     | `logger.debug(...)` — silent default |
| 159           | prefix match    | `utils.print_grey(...)` — **always prints** |
| 164           | suffix match    | `utils.print_grey(...)` — **always prints** |

`utils.print_grey` is a raw `print()` (see `cloudsplaining/shared/utils.py:151-153`), so
the prefix/suffix branches always write to stdout regardless of log level.

This is noisy because `is_name_excluded` is called with hardcoded patterns during
**collection construction**, independent of any user-supplied exclusions config. The
prints originate in the `RoleDetailList` / `ManagedPolicyDetails` build loops — **not** in
`PolicyDocument.__init__` (which does not call `is_name_excluded` itself):

- `cloudsplaining/scan/role_details.py:68` → `is_name_excluded(this_role_path, "/aws-service-role*")` (per-role loop)
- `cloudsplaining/scan/role_details.py:246` → `is_name_excluded(self.path, "/aws-service-role*")`
- `cloudsplaining/scan/managed_policy_detail.py:66` → `is_name_excluded(this_policy_path, "aws-service-role*")` and `"/aws-service-role*"` (per-policy loop)
- `cloudsplaining/scan/managed_policy_detail.py:207` → `is_name_excluded(self.path, "/aws-service-role*")`

`AuthorizationDetails.__init__` (`scan/authorization_details.py:59,85`) constructs
`ManagedPolicyDetails` and `RoleDetailList` at build time using the **default**
`exclusions=DEFAULT_EXCLUSIONS`, so every service-linked role / AWS-managed policy hits
the prefix branch → a flood of grey lines on any parse. This fires for **all library
parsing of GetAccountAuthorizationDetails**, with no custom exclusions required.

### Note on `download`

The `download` **CLI command** (`cloudsplaining/command/download.py`) is pure boto3
(`get_account_authorization_details`) and does **not** construct the scan objects, so it
does not itself call `is_name_excluded`. If the user sees these lines "during download,"
it is coming from a wrapper that downloads *and then parses* (library construction of
`AuthorizationDetails`), or from `scan`. The fix below covers all of these paths
regardless of which command triggers construction. **(Reviewer confirmed: `download.py`
has no `AuthorizationDetails`/`is_name_excluded`/`Exclusions` reference — pure boto3.)**

## Constraint from the user

- **Library mode** (importing cloudsplaining, parsing authz details, building
  `PolicyDocument`s): must be **quiet by default** and silenceable/controllable via
  standard `logging`.
- **CLI mode** (`cloudsplaining scan`, `download`, `scan_multi_account`, etc.): must
  **behave exactly as it does today** — these grey lines still print.

### Why a naive swap fails

The CLI's default log level is `CRITICAL` (`cloudsplaining/__init__.py:79`,
`set_log_level(0)`). So simply swapping `print_grey` → `logger.debug` would make the
messages disappear from the **default CLI** too (only visible at `-vvv`), which violates
"CLI behaves the same." Bumping the CLI default to DEBUG is worse: it floods all ~20
other `logger.debug` lines and changes the format to timestamped log lines.

## Design: module-level toggle, scoped on by the CLI entrypoint

Add a process-level switch in `exclusions.py`. Library importers never flip it → quiet.
The CLI group callback flips it on **for the duration of the invocation** and restores the
prior value on context teardown → every subcommand prints exactly as today, with no sticky
state leaking into a later in-process library call.

### Change 1 — `cloudsplaining/shared/exclusions.py`

Add near the module logger:

```python
# When running as a CLI we surface exclusion-match messages on stdout (grey), matching
# historical behavior. As a library these go to logger.debug so consumers can control
# them via standard logging configuration. The CLI entrypoint flips this on.
_PRINT_EXCLUSION_MATCHES = False


def set_exclusion_output(enabled: bool) -> bool:
    """Toggle stdout printing of exclusion-match messages; return the PREVIOUS value so the
    caller can restore it. The CLI enables this so the grey 'Excluded prefix/suffix' lines
    still print; library usage leaves it off."""
    global _PRINT_EXCLUSION_MATCHES
    previous = _PRINT_EXCLUSION_MATCHES
    _PRINT_EXCLUSION_MATCHES = enabled
    return previous


def _report_exclusion(message: str) -> None:
    """Emit an exclusion-match message: print (CLI) or logger.debug (library)."""
    if _PRINT_EXCLUSION_MATCHES:
        utils.print_grey(message)
    else:
        logger.debug(message)
```

Replace the two `utils.print_grey(...)` calls in `is_name_excluded` (currently lines
159 and 164) with:

```python
                _report_exclusion(f"\tExcluded prefix: {exclusion}")
...
                _report_exclusion(f"\tExcluded suffix: {exclusion}")
```

Leave line 151 (`logger.debug(f"\tExcluded: {exclusion}")`) **unchanged** — exact-match
is already silent on the CLI today, and we are preserving current behavior. (Documented
tradeoff: the three branches remain non-uniform, but CLI output is unchanged.)

### Change 2 — `cloudsplaining/bin/cli.py`

The `@click.group()` callback `cloudsplaining()` (`bin/cli.py:17-22`: `@click.group()` at
line 17, `@click.version_option` at 18, `def cloudsplaining()` at 19) has an **empty body**
today and runs before every subcommand. There is no `invoke_without_command`, no
`chain=True`, and no `ctx` param, so stock Click semantics guarantee the group body runs
before any resolved subcommand. Add the import alongside the existing
`from cloudsplaining import command` / `from cloudsplaining.bin.version import __version__`
(lines 13-14).

**Scope the toggle to the CLI invocation — do NOT leave it sticky.** Enable printing for
the duration of the command, then restore the prior value when the Click context tears
down (which happens *after* the subcommand finishes). This closes the embedded-CLI leak
flagged by the Codex adversarial review (an in-process caller that runs the CLI and then
constructs scan objects as a library would otherwise keep printing forever):

```python
from cloudsplaining.shared.exclusions import set_exclusion_output

@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cloudsplaining(ctx: click.Context) -> None:
    """..."""
    previous = set_exclusion_output(True)
    ctx.call_on_close(lambda: set_exclusion_output(previous))
```

`ctx.call_on_close()` registers a teardown callback that Click runs when the context is
closed — for a group, that is after the resolved subcommand returns (or raises). It also
fires under `CliRunner`/`main()` (Click closes contexts in a `finally`), so the restore is
reliable for in-process callers, not just real shell processes that exit anyway.

All seven subcommands are registered via `add_command` (`cli.py:25-31`), including
`download` and `scan_multi_account` (which runs in-process — `scan_multi_account.py:258`
builds `AuthorizationDetails` directly, no subprocess — so the in-process toggle reaches
it). Library importers never invoke this callback, so `_PRINT_EXCLUSION_MATCHES` stays
`False` for them. **(Reviewer confirmed: group callback runs for every subcommand.)**

> **Rejected alternative — sticky global (original v1 of this plan):** calling
> `set_exclusion_output(True)` without restoring it is simpler but leaks: any process that
> invokes the CLI in-process and *then* uses the library keeps printing, violating the
> quiet-by-default library contract. The scoped restore above is the fix. A fully
> state-free design (thread the flag as a parameter) was considered and rejected — too many
> literal-pattern call sites (`role_details.py`, `managed_policy_detail.py`,
> `policy_finding.py`) call `is_name_excluded` directly to thread cleanly.

## TDD (write failing tests first, per repo standards)

In `test/shared/test_exclusions.py` (uses `capsys`):

1. **Library default is quiet**: with the module default (`_PRINT_EXCLUSION_MATCHES`
   False), calling `is_name_excluded("/aws-service-role/foo", "/aws-service-role*")`
   returns `True` and produces **no** stdout. (Fails today: it prints.)
2. **CLI mode prints**: after `set_exclusion_output(True)`, the same call returns `True`
   and prints `Excluded prefix:` to stdout. Reset to `False` in teardown/finally.
3. **logger.debug path**: with output off and `caplog` at DEBUG on the `cloudsplaining`
   logger, the prefix message is emitted as a debug record.
4. (Optional) Same trio for the suffix branch.
5. **Embedded-CLI regression (the Codex finding)**: invoke the CLI **in-process** via
   Click `CliRunner` on a real subcommand (e.g. `scan` against a fixture, or even
   `--help`), then — in the same process, *after* the runner returns — call
   `is_name_excluded("/aws-service-role/foo", "/aws-service-role*")` (or construct
   `AuthorizationDetails` from a fixture) and assert **stdout is quiet** (and
   `exclusions._PRINT_EXCLUSION_MATCHES is False`). This proves the `ctx.call_on_close`
   restore actually fires and the flag does not stay stuck on after a CLI run. This test
   must be written to **fail** against the rejected sticky-global design.

Guard global state — **required, not optional** (defense-in-depth behind the runtime
restore): add a suite-wide **autouse** fixture in `test/conftest.py` that snapshots and
restores the toggle around *every* test. The `ctx.call_on_close` restore is the primary
mechanism, but the fixture protects against any test that flips the flag directly (or a
CLI test that bypasses normal context teardown) leaking state and causing order-dependent
flakiness:

```python
# test/conftest.py
import pytest
from cloudsplaining.shared import exclusions


@pytest.fixture(autouse=True)
def _reset_exclusion_output():
    prev = exclusions._PRINT_EXCLUSION_MATCHES
    yield
    exclusions.set_exclusion_output(prev)
```

A local `try/finally` in the new exclusion tests is **not** sufficient on its own, because
the leak can originate from any CLI-invoking test elsewhere in the suite.

## Risks / things the reviewer must fact-check

1. **No existing test asserts on this stdout.** Grep found no `capsys`/`capfd` capture of
   "Excluded prefix/suffix" in `test/`. Confirm switching the default to silent does not
   break an existing assertion (e.g. in `test/scanning/test_policy_document.py` or
   `test/shared/test_exclusions.py`).
2. **Click group callback semantics.** Confirm a group-level callback body runs on every
   subcommand invocation (it should, but verify there's no `invoke_without_command` or
   chaining quirk).
3. **Import cycle.** `bin/cli.py` importing `set_exclusion_output` from
   `cloudsplaining.shared.exclusions` — confirm no circular-import problem (cli already
   imports `cloudsplaining.command`, which imports scan/output → exclusions, so exclusions
   is already in the graph; should be fine).
4. **Global mutable state / test isolation.** Module-level toggle is process-wide
   (mirrors the existing global `set_log_level`). **Codex adversarial finding:** a sticky
   `set_exclusion_output(True)` leaks into later in-process library use. **Resolved** by the
   `ctx.call_on_close()` runtime restore (Change 2) plus the autouse `conftest.py` fixture
   as defense-in-depth, and verified by TDD item 5. No multi-threaded library usage exists
   in this repo today; if that changes, revisit the global in favor of a
   `contextvars`-scoped flag.
5. **`scan_multi_account`** may spawn work differently — confirm it still goes through the
   same `cloudsplaining` group callback (it's registered as a subcommand, so yes).
6. **Does the fix actually cover the user's reported paths?** Verify the prints originate
   from `is_name_excluded` (the only `print_grey` exclusion call sites) and that
   `RoleDetailList` / `ManagedPolicyDetails` / `PolicyDocument` construction routes
   through it. Confirm there is no *other* stray `print(...)` of exclusion info elsewhere.

## Verification (per repo `just` tasks)

- `just unit-tests` (new tests pass; nothing else breaks)
- `just type-check`
- `just lint`
- Manual library smoke: construct `AuthorizationDetails` from a fixture with
  service-linked roles and assert no stdout; then run `cloudsplaining scan` on the example
  data and confirm the grey lines still appear.

## Out of scope

- Unifying line 151 with the prefix/suffix branches (would change CLI default behavior).
- Reworking `set_log_level` / default verbosity.
- Converting other `print_green`/`print_red` helpers.
