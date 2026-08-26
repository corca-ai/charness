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

## 2026-08-27 follow-up — runner-neutral consumer universe seam

The consumer boundary now has an adapter-owned, optional
`runtime_budget_universe.command`. A configured repo-owned command emits one
runtime label per line; the generic reader reconciles that output with the
union of every top-level and profile budget block. This keeps consumer runner
syntax outside Charness while making the boundary observable when a consumer
chooses to provide it.

An absent command is `not-declared`/non-blocking for compatibility with older
consumers. A command failure, empty output, duplicate output, or budgeted label
missing from the emitted universe is an explicit configuration error. Labels
that are known by the runner but unbudgeted remain context only and do not
become a new gate. Conditional intent remains `execution_proven: false`; the
command proves membership, not trigger execution or budget firing.

## Follow-up verification — runner-neutral consumer seam

- Commit `459e3c084bcfd7d49ee6c3acf80c9b10e33e1ee7` — `feat(issue-546):
  reconcile consumer runtime label universes`; source and generated plugin
  mirrors are included.
- Focused consumer/adapter/runtime regressions: `87 passed`.
- Exact standing target
  `tests/quality_gates/test_runtime_budget_universe.py`: `35 passed`.
- Isolated changed-line proof from proof branch
  `proof/issue-546-consumer-universe-final-3`: `status: clean`,
  `consumer_returncode: 0`, `blocking: []`,
  `unmapped_changed_pool_files: []`; all `7` mapped changed source files were
  analyzed and every changed line was covered. The producer standing pytest
  also passed inside that receipt.
- Pre-commit for the implementation commit completed successfully; source /
  generated-mirror drift checks and documentation link checks passed.

## Accepted ownership boundary and successor non-claims

The Charness-owned portion of this work item is complete: the adapter declares
runtime-budget intent, the validator reconciles the complete budget label
universe, and the optional consumer-owned runner command makes membership
observable without inferring execution.

The following remain explicit successor non-claims and are not required for
this issue's completion:

- scheduler changes or scheduler-side trigger execution;
- hosted or installed-host enforcement;
- consumer-repository runner adoption, conditional-label schema, or command
  implementation;
- conditional trigger execution or budget firing; and
- profile-scoped unreachable-label and unbudgeted-command advisories becoming
  new gates.

The local evidence is deterministic and complete for this boundary: focused
consumer/adapter/runtime regressions passed, the exact runtime-budget target
passed, adapter validation passed, and the isolated consumer-universe
changed-line proof analyzed all mapped changed files with no blockers or
unmapped files. The implementation and generated mirror were checked for
parity. This is not a claim about remote CI, provider behavior beyond the
recorded local adapter seam, or installed consumers.

This accepted boundary is a completed Charness contract with the remaining
work intentionally handed to a successor issue or goal. No fresh-eye,
handoff, or micro-slice ritual is part of this closeout path.
