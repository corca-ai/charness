# Issue #421 Scheduled Gate Red — Unguarded Credentials Copy in capture-skill-run.sh

Date: 2026-07-09

## Problem

The scheduled mutation workflow run 28986563107 (2026-07-09 01:11 UTC, head
`f84eb223`) posted FAIL to #421: coverage-baseline pytest failed before mutation
sampling. Thanks to the #422 fix, the summary named the blocking nodeid directly
— `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
— instead of misreporting a missing StrykerJS report. This is a NEW root cause,
unrelated to the 2026-07-08 RULE_DATE red
([2026-07-08-issue-421-nightly-mutation-gate-red.md](./2026-07-08-issue-421-nightly-mutation-gate-red.md)).

## Correct Behavior

- Given a machine with no `~/.claude/.credentials.json` and no
  `CLAUDE_CONFIG_DIR` (a CI runner),
- When the #423 behavioral test executes `capture-skill-run.sh` end-to-end with
  a PATH-shimmed fake `claude`,
- Then the script completes (exit 0) and the no-identity-leak assertions run.

## Observed Facts

- CI step log: `capture-skill-run.sh` returncode 1 with stderr
  `cp: cannot stat '/home/runner/.claude/.credentials.json': No such file or directory`;
  the test's `assert result.returncode == 0` fails.
- `scripts/agent-runtime/capture-skill-run.sh:125` is an UNGUARDED
  `cp "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.credentials.json" "$cfg/"` under
  `set -euo pipefail`; the adjacent `settings.json` copy on line 126 is guarded
  with `2>/dev/null || true`.
- The test (`tests/test_skill_efficiency_ab.py:320-326`) invokes the script with
  `env={**os.environ, ...}` — it inherits the operator's `CLAUDE_CONFIG_DIR`
  and real credentials, so it is green on any operator machine and red on CI.
- The test landed with the #423 fix (`7c09a8c`); this scheduled run was the
  first to execute it in a credential-less environment.

## Reproduction

- Local, exact CI failure (empty HOME, no CLAUDE_CONFIG_DIR):
  `FAKEHOME=$(mktemp -d) && env -u CLAUDE_CONFIG_DIR HOME="$FAKEHOME" python3 -m pytest tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view -x`
  → FAILED with the identical `cp: cannot stat ... .credentials.json` stderr
  and returncode 1. (If pytest lives in user site-packages, also pass
  `PYTHONUSERBASE=<real-home>/.local`.)
- Same nodeid with the ambient env → 1 passed (0.5s).

## Hypothesis

- Falsifiable claim: the unguarded credentials `cp` at line 125 aborts the
  script on any machine lacking the file | disconfirmer: run the test with
  `CLAUDE_CONFIG_DIR` unset and an empty `$HOME` — if it still passes, the
  cause is elsewhere.

## Verification

- result: confirmed — the env-stripped local run fails with the exact CI
  assertion and stderr; the ambient-env run passes.

## Root Cause

Environment-dependent hard failure: `capture-skill-run.sh:125` treats
`.credentials.json` as guaranteed input, and the #423 behavioral test inherits
the invoking machine's `CLAUDE_CONFIG_DIR`/`$HOME` instead of pinning a
hermetic config dir. Local-green/CI-red divergence was guaranteed the moment
the test landed.

## Fix Shape (for the resolving session)

- Make the test hermetic: pass a tmp `CLAUDE_CONFIG_DIR` containing a stub
  `.credentials.json` (the shimmed `claude` never reads it), so the test stops
  depending on operator machine state.
- Decide the script posture separately: a REAL capture without credentials
  fails later anyway at `claude` auth, so either keep the hard `cp` as an
  early loud failure (preferred: clearer signal than a mid-run auth error) or
  guard it like line 126. Do not silently guard it just to appease the test.
- Prove with both Reproduction commands (env-stripped and ambient — both must
  pass after the fix), push, and let the scheduled run auto-close #421.

## Detection Gap

- The #423 closeout proved the invariant on the authoring machine only;
  nothing exercised the new end-to-end test in a credential-less env before
  push. Smallest change: subprocess-spawning tests that execute host-reading
  scripts must pin every host-derived input (`HOME`, `CLAUDE_CONFIG_DIR`) to
  fixture state — check this at review time for any test that passes
  `**os.environ` to a script under `set -e`.

## Sibling Search

- Same axis: `capture-skill-run.sh` reads `settings.json` (guarded, line 126)
  and writes plugin manifests into its own `$cfg` (self-created) — no other
  unguarded ambient reads found in the script (`grep -n 'HOME\|CLAUDE_CONFIG_DIR'`).
- Test-suite axis: other
  [tests/test_skill_efficiency_ab.py](../../tests/test_skill_efficiency_ab.py)
  subprocess tests drive
  git/python against tmp fixtures, not host config; the behavioral test is the
  only one passing ambient `CLAUDE_CONFIG_DIR` through to a `set -e` script.

## Prevention

- Field confirmation for #422: the mutation summary named the failing nodeid
  as the blocking signal on first occurrence — 2026-07-08's detection gap is
  closed in practice, not just roundtrip-proven.
