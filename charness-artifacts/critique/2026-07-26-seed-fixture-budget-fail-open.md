# Seed fixture budget gate: closing a fail-open without opening a fail-wedge
Date: 2026-07-26

## Decision Under Review

Closing the fail-open in
[check_seed_fixture_budget.py](../../scripts/check_seed_fixture_budget.py):
a `du` scan that failed classified as `advisory_only_pytest_temp_scan_failed`
and returned 0, so a permanently broken scan passed the gate forever without
grading a single byte. Named as blocker 3 of the previous handoff, together with
the 15 changed lines from `b12af528` that the pre-push changed-line mutation gate
would not let through.

The violation was reproduced before the guard was written: the pre-change
`main()`, handed `{"status": "unavailable", ...}`, printed a warning and returned
**0**. Post-change it returns **1**.

## Failure Angles

Two bounded read-only reviewers, spawned per the repo delegation contract, on
disjoint scopes:

- **Correctness** — exception ordering in the new `du` wrapper, retry accounting,
  exit codes on every path including `--json`, other consumers of the changed
  return shape, and whether making the gate blocking can wedge a legitimate push.
- **Test quality** — whether each new test can actually fail, real-machine
  coupling, `functools.cache` leakage across the shared module loader.

Parent-side worktree+index integrity was fingerprinted around both reviews
(`reviewer_boundary_fingerprint.py` snapshot/verify): `{"ok": true, "drift": []}`.

## What The Reviews Changed

The first design — retry three times, then hard-fail — was **wrong**, and both
the fix and its justification were rewritten because of the review:

- **The wedge (highest severity).** A second pytest run against the same repo
  shares `pytest-of-<user>`, and `du` exits nonzero continuously for the ~60s of
  that run. All three attempts inside a 0.5s window would fail, and the operator
  would be told to go debug `du` when nothing was wrong. Worse, with
  `PYTEST_DEBUG_TEMPROOT` unset the scan falls back to the shared `/tmp` tree,
  where *any other project's* pytest run could block this repo's push.
- **The portability wedge.** BusyBox `du` has no `-B` at all, so an Alpine CI
  container would fail every attempt and block permanently — with a remediation
  message telling the operator to run the same broken command. The `du_missing`
  carve-out did not cover it, because it keyed on the binary being absent rather
  than on the box being unable to do what was asked.

The redesign follows from the reviewers' own observation: `du` **keeps walking**
past a vanished entry and still prints the root total. So a nonzero exit is not
evidence of a failed measurement — the output is. The scan now drops
`check=True`, accepts any walk that printed the root's own total line (flagged
`partial`), retries only a walk that died before totalling, and classifies
absent / non-executable / `-B`-rejecting `du` as a capability gap that stays
advisory. `--advisory-on-scan-failure` is the narrow escape hatch; without it the
only way past was `git push --no-verify`, which disables all 82 gates to get past
one.

Also from the reviews: the total scan timeout is now capped **across** attempts
(three 30s attempts would have tripled the gate's worst case against its own
2000ms budget), `attempts` is reported on the success path too (a retry that
silently succeeded left no trace of a flaky box), and the tests gained the
boundary case (`>` not `>=`), `session_count`, the sleeps-only-between-attempts
invariant, and BusyBox/GNU option-error coverage.

Two further reviewer findings, both real and both fixed:

- **The exported gate was broken and had been.**
  `plugins/charness/scripts/check_seed_fixture_budget.py` hard-coded
  `skills/public/quality/...`, a path that does not exist in the flattened plugin
  layout; it died with a bare `FileNotFoundError` from `exec_module`. Reproduced,
  then fixed in canonical with the two-candidate resolution every sibling script
  already used. Pre-existing, unrelated to the fail-open, found only because the
  file's failure semantics were under review.
- **A load-bearing stale comment.** `run-quality.sh` still recorded this gate's
  failure mode as fail-open as the justification for its placement behind the
  pytest barrier. Anyone moving it back on the strength of that comment would now
  hard-fail the run. Rewritten, along with the gate's stale
  `attention-state-visibility.json` declaration.

## Counterweight Pass

Not everything the reviewers raised was acted on:

- The `subprocess`/`time` monkeypatch-scoping hazard was **real and fixed** (the
  stub now replaces the module attribute rather than mutating the shared stdlib
  module), but the reviewer's related worry about `pytest-randomly` ordering was
  correctly graded down by the other reviewer: the plugin is not installed here.
- The `total_bytes` fallback was **dead code**, not an untested branch — the
  quick scan never emits that key. Deleted rather than pinned with a test that
  would have documented a path that cannot execute.
- The dup ratchet's two new families are two-line
  `if <predicate>: return "<literal>"` classifier arms shared with four unrelated
  owners. Classified `intentional` in `dup-review.json` rather than extracted:
  each arm returns its own domain's constant and shares no behavior.

Both gate failures hit mid-slice (`ruff` C901 on two functions, and
`check-python-lengths` on a file the reviewer had predicted would breach) were
treated as design signals, not obstacles: the `du` scan concern moved into
[pytest_temp_scan_lib.py](../../skills/public/quality/scripts/pytest_temp_scan_lib.py)
with its own retry policy and failure taxonomy, and the gate's `main()` split
into `classify_scan` and `collect_breaches`.

## Residuals

- **The `partial` flag is reported but not acted on.** A walk that lost entries
  under-counts, so a breach could in principle hide behind a partial scan. With a
  10 GiB budget against a ~1.2 MiB observed footprint the margin is four orders of
  magnitude, so this is recorded rather than gated.
- **BusyBox/BSD `du` behavior is inferred, not probed.** The usage-error token
  list is matched against strings those builds are documented to emit; no real
  Alpine or macOS run backs it. The failure mode if the tokens miss is a blocked
  push on that host, recoverable with `--advisory-on-scan-failure`.
- The reviewer's suggestion to route the unreadable-batch test through the CLI
  rather than calling `load_batch_records` directly is valid and unacted; the
  current test pins the library contract but not the `main()` wiring.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:55 | action: fix | note: retry-then-hard-fail blocks a legitimate push whenever a second pytest run churns the shared temp tree; `du`'s own output, not its exit status, is the discriminator
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:38 | action: fix | note: BusyBox `du` rejects `-B` outright, so an Alpine container would block permanently; the `du_missing` carve-out keyed on the binary being absent rather than on the box being unable to do what was asked
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_seed_fixture_budget.py:16 | action: fix | note: the plugin-exported gate hard-coded a `skills/public/` path the flattened export layout lacks and died with a bare FileNotFoundError; pre-existing and reproduced
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:610 | action: fix | note: the runner comment recorded this gate as fail-open as the justification for its placement, which would mislead the next person to move it
- F5 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:112 | action: fix | note: a per-attempt timeout would triple the gate's worst case against its own 2000ms budget; the cap is now across attempts
- F6 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:186 | action: fix | note: reporting `attempts` only on failure erased the evidence that a box's scan is flaky
- F7 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_seed_fixture_budget_gate.py:221 | action: fix | note: patching through `lib.subprocess` mutates the shared stdlib module process-wide; the stub is now scoped to the module under test
- F8 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_seed_fixture_budget_gate.py:144 | action: fix | note: no test sat on the budget boundary, so a `>` to `>=` mutation survived; `session_count` in the quick scan was likewise unasserted
- F9 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_seed_fixture_budget.py:112 | action: fix | note: the `total_bytes` fallback is dead from this call site, not an untested branch; deleted rather than pinned with a test for an unreachable path
- F10 | bin: over-worry | evidence: weak | ref: tests/script_main.py:13 | action: defer | note: `functools.cache` ordering leakage under pytest-randomly; the plugin is not installed in this repo and every mutation goes through monkeypatch
- F11 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:190 | action: document | note: a `partial` walk under-counts, so a breach could hide behind it; the observed footprint is four orders of magnitude under budget, so this is recorded rather than gated
- F12 | bin: valid-but-defer | evidence: contested | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:40 | action: document | note: the BusyBox/BSD usage-error tokens are inferred from documented output, not probed on a real Alpine or macOS host; a miss means a blocked push there, recoverable with --advisory-on-scan-failure
- F13 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_runtime_recorder.py:211 | action: defer | note: the unreadable-batch test calls `load_batch_records` directly, so it pins the library contract but not the `main()` wiring

## Reviewer Tier Evidence

- Requested tier: typed `bounded-reviewer` subagents (read-only: Read/Grep/Glob), session-model inheritance per the Claude Code host branch of the repo subagent contract.
- Requested spawn fields: `subagent_type: bounded-reviewer`, disjoint scope prompts (correctness angle; test-quality angle), no model or effort override.
- Host exposure state: applied
- Application state: host-confirmed: both reviewers independently reported the envelope bound with Read/Grep/Glob only and no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

Neither reviewer had Bash, so neither could run `git show HEAD:<path>` or execute
a test; both stated that limit explicitly, and every finding was re-derived here
against the running code before being acted on.

## Reviewed Input Identity

<!-- No prepared packet was consumed; both reviewers read the uncommitted worktree directly. -->

## Boundary Ownership

- Producer: `pytest_temp_scan_lib.pytest_temp_footprint_quick`, which decides whether a `du` walk measured anything.
- Consumer: `check_seed_fixture_budget.py` at the pre-push and broad-gate boundary, which turns that into a push verdict.
- Owning surface: the quality gate pair (scan library owns the failure taxonomy; the gate owns the blocking policy).
- Verdict: moved-to-owner
