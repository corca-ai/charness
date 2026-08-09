# Quality Review
Date: 2026-08-09
Title: Remote CI Changed-Line Reconciliation Quality Review

## Scope

Target boundary: local focused changed-line selection and coverage versus the
GitHub broad changed-line mirror for the regenerable-facts failure range.

Ambient repo findings: the approved release, planned goal slice 5, unrelated
issues, and hosted CI publication remain outside this local repair review.

## Surface Contract Review

- semantic coverage: `partial` — local selection, executable coverage, and both local changed-line consumers are proven; hosted CI on the repaired SHA is unexamined.
- surface: original failure-range and branch-range changed-line verdicts
- owner: the shared selector owns reachability, tests own executable observations, and each changed-line consumer owns its verdict.
- projections: root selector, checked-in plugin mirror, focused wrapper output, broad lock receipt, and hosted CI log
- state scope: fixed old base range plus `origin/main..HEAD` at the local verification lock
- transitions: unmapped, mapped-and-blocking, dirty-tree unestablished, and clean
- proof boundary: exact old-range final consumer plus broad standing pytest and fresh branch changed-line readback
- unexamined axes: hosted runner/provider state and repaired-SHA CI result

## Current Gates

- Targeted mapper and regenerable-facts tests pass.
- The exact old failure range first reproduced all eight hosted blockers, then
  reached `status: clean` with no blocking or unmapped files after commit.
- `run_slice_closeout.py --base origin/main --verification-lock
  --produce-mutation-coverage` completed with broad standing pytest and the
  fresh changed-line consumer passing.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; local full profile. <!-- reproduction-source -->
- runtime hot spots: broad coverage-producing standing pytest was the dominant phase; no budget or speed claim is made.
- coverage gate: local fixed-range and branch-range consumers pass; hosted coverage remains unrun on the repaired SHA.
- evaluator depth: deterministic-gates-only because Cautilus is ask-before-run and no evaluator proof is needed for this source-line escape.

## Healthy

- One shared reachability repair feeds both focused consumers and its plugin
  projection, avoiding local/remote policy forks.
- Coverage is measured in-process for branches subprocess-only tests cannot
  make visible, while subprocess delivery tests retain their separate role.
- Truly unmapped files remain `UNPROVEN`; the repair removes false absence
  without turning selector uncertainty into a clean verdict.

## Weak

- Filename/stem matching can safely over-select same-basename tests, increasing
  local work or causing a false stop; tests pin that direction explicitly.
- The first clean-tree proof found one uncovered branch in the mapper repair,
  requiring a test-only follow-up before the final lock.

## Missing

- Hosted `Quality Core` readback on the repaired SHA; it requires explicit push
  approval and a different observer/channel from the push exit code.

## Deferred

- General AST data-flow for arbitrary aliases is deferred until a supported
  loader escape demonstrates that the bounded literal model is insufficient.

## Advisory

- structural review result: artifact: `charness-artifacts/critique/2026-08-09-remote-ci-changed-line-reconciliation-code-critique.md`; keep the existing selector → selected tests →
  changed-line consumer ownership chain; the repair belongs at reachability and
  observation, not in CI scope or mapper policy.
- prose review result: artifacts: `charness-artifacts/debug/2026-08-09-remote-ci-changed-line-reconciliation-debug.md` and `charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md`; goal, quality, and handoff also preserve the
  hosted-CI non-claim and name the approved-push boundary.
- inventory result: command: `python3 scripts/check_changed_surfaces.py --repo-root .`
  names the root/plugin sync and repo-Python verification obligations; all were
  exercised by the verification lock.

## Delegated Review

- Delegated Review: executed — three read-only failure angles, one separate
  counterweight, and one repaired-surface round found and closed evidence/test
  blockers; the final repaired-surface verdict was no blocker.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  the closeout-claims reviewer found no blocker. Existing-gate reuse keeps the
  old-range reproduction and branch lock complementary; broad coverage remains
  confined to the lock, and each focused fixture owns a distinct failure mode.

## Commands Run

- Targeted pytest over the mapper and regenerable-facts modules — 66 passed;
  reproduced in `/tmp/charness-remote-ci-targeted-final.log`. <!-- reproduction-source -->
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha ec67291e88c76c45e5604882152bc021a915458b --json` — final status clean.
- `bash scripts/run-quality.sh` — pre-commit aggregate passed with only the expected dirty-tree changed-line non-claim.
- `python3 scripts/run_slice_closeout.py --repo-root . --base origin/main --verification-lock --produce-mutation-coverage` — completed.

## Recommended Next Quality Moves

- active hosted-CI confirmation — capability_needed=provider readback; next_center=repaired branch SHA; transformation=push only with explicit approval and read `Quality Core` through GitHub; proof_boundary=hosted job conclusion and failed-log readback if red; enforcement_posture=existing-gate-reuse.
- passive arbitrary alias resolution — capability_needed=broader reachability only after another supported-loader escape; next_center=selector dependency model; transformation=extend from a recorded counterexample; proof_boundary=mapper fail-before plus changed-line consumer; enforcement_posture=no-gate because current supported loader families are covered.

## History

- [Prior proof-path quality review](./history/2026-07-19-portable-proof-path-learning-review.md)
