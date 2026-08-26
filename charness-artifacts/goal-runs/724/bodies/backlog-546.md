<!-- charness-work-item-key: backlog-546 -->
# Existing Work Item #546 — Explicit runtime-budget intent

## Purpose and premise

Make runtime-budget scheduling intent adapter-owned and explicit for every label:
always, conditional with a named trigger, or external/not locally enforceable.

## Owned change and acceptance

Validate the declared universe without inferring consumer intent; an unobserved
conditional execution remains an explicit non-claim and cannot read as a green
enforcement result.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_runtime_budget_universe.py`, then changed-line proof. This child does not change the scheduler or claim hosted enforcement.

## Executed verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_runtime_budget_universe.py` — `32 passed`.
- Isolated changed-line proof: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` — `status: clean`, `consumer_returncode: 0`, `ok: true`, `blocking: []`, `unmapped_changed_pool_files: []`; the clean proof commit analyzed only `scripts/check_runtime_budget_universe.py` and covered every changed line.
- Proof identity: parent `f4572226798eaf41902980ffc9894350694733f3`, isolated proof commit `72a8b2ca162a1c799289e0bc5bbc56c81631e432`; durable receipt: `charness-artifacts/goal-runs/724/observations/goal-run-546-changed-line-proof-20260827.md`.
- The parent worktree's broad run is a separate non-claim: standing tests passed, but the dirty cutover pool left 8 changed files uncovered and 16 unmapped, so that run was refused rather than cited as `#546` proof.
- This is local deterministic proof only; no scheduler change, hosted enforcement,
  installed-host behavior, issue closure, push, release, or tag is claimed.
- `Critique: not-required — the user-authorized implementation path omits forced
  fresh-eye execution; no fresh-eye result is claimed.`

## 2026-08-27 follow-up — adapter-owned scheduling intent

The runtime-budget contract now records adapter-owned scheduling intent for the
whole budget universe. Each label is classified exactly once as `always`,
`conditional` with a named trigger, or `external` with a named owner. The gate
checks the union of all top-level and profile budget blocks instead of inferring
consumer intent from samples or history. A conditional label is emitted as an
explicit `execution_proven: false` non-claim; this does not assert that its
trigger ran or that its budget fired.

The current Charness adapter declares all `35` budgeted labels: `26` always and
`9` conditional. The declaration reconciles with a runner universe of `109`
labels with no unknown, missing, extra, or validator errors. Older consumers
without the field receive a migration warning; a present incomplete or extra
declaration is invalid.

## Follow-up verification

- Focused adapter/universe tests: `53 passed`.
- Full standing pytest: `11439 passed in 104.36s`.
- Adapter validation: `16/16` resolvers and YAML files, `0` unreconciled keys.
- Isolated changed-line proof: `status: clean`, `consumer_returncode: 0`, `ok: true`, `4/4` changed mutation-pool files analyzed, no blockers or unmapped files; proof commit `a053a0e1e7bb5995d816a2a887065aea4177e440`.
- Targeted mutant proof at `check_runtime_budget_universe.py:159` failed the extra-label regression test when `errors.append(` was replaced with `errors.clear(`, then passed after restoration.
- Durable receipt: `charness-artifacts/goal-runs/724/observations/goal-run-546-runtime-budget-intent-20260827.md`.

## Remaining acceptance boundary

This child remains open. The scheduler was not changed, and no hosted or
installed-host enforcement is claimed. Conditional trigger execution remains
unproven, and consumer repositories still need their own runner-universe reader
and conditional-label schema. Existing profile-scoped unreachable-label and
unbudgeted-command advisories remain explicit non-claims rather than new gates.
