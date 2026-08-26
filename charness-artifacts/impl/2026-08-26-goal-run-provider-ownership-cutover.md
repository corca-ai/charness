# Goal Run Provider Ownership Cutover Closeout

Date: 2026-08-26 Asia/Seoul
Status: implemented

## Implemented

Implemented the #726 adapter-resolved Goal Run provider boundary as a
file-backed, one-operation-at-a-time surface:

- `goal-run-preflight` validates the full requested provider closure before
  mutation.
- `goal-run-read` reads the exact parent and normalized real child graph.
- `goal-run-apply` owns typed body update, create/reuse, list, relation add and
  remove, and local observation operations.
- `goal-run-close` is a separate guarded ingress; generic close refuses a
  Goal Run metadata carrier.
- immutable started/terminal observations bind each attempted operation to the
  frozen draft, immutable binding, parent, target, and provider outcome.
- create recovery performs exact discovery before any retry, so provider/index
  races do not cause a second create.

The command surface is implemented in the canonical issue skill and generated
plugin mirror. Primitive tracker commands remain only as compatibility and
diagnostic surfaces used by existing consumers.

## Source of truth and paths

- implementation contract: `charness-artifacts/goal-runs/724/bodies/goal-run-provider.md`
- approved plan: `charness-artifacts/goal-runs/724/approved-plan.json`
- immutable binding: `charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json`
- final graph expectation: `charness-artifacts/goal-runs/724/bootstrap-final-graph.json`
- operation files and immutable observations: `charness-artifacts/goal-runs/724/operations/` and `charness-artifacts/goal-runs/724/observations/`
- exact external readback: `charness-artifacts/goal-runs/724/final-graph-readback.md`

## Local verification

- `pytest -q tests/quality_gates/test_issue_goal_run.py tests/quality_gates/test_issue_tracker.py tests/quality_gates/test_issue_tracker_observation.py tests/quality_gates/test_issue_tool_runners.py tests/quality_gates/test_issue_skill.py` — 82 passed.
- `python3 scripts/check_skill_contracts.py --repo-root .` — passed.
- source/plugin provider `py_compile` — passed.
- source/plugin parity for provider scripts and issue docs — passed.
- `bash scripts/check-docs.sh` — passed; existing advisory inline-code warnings remain non-blocking.
- `python3 scripts/check_python_lengths.py` over the provider surface — passed with one advisory warning: `issue_close.py` at 332 code lines, below the hard limit.
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --changed-skill-md skills/public/issue/SKILL.md` — passed with 123 core lines and 37 remaining lines.

## Live provider evidence

- full `goal-run-preflight` against `corca-ai/charness#724` — `status: ready`,
  all nine Goal Run operations available, all ten required backend operations
  present, no template errors, no mutation.
- parent update — `verified-write`; readback body SHA-256
  `653e372e8fee23449cdc0f9e798ad6c76af72d24300e422d5eadec5fedd6e980`.
- 26 existing child body cutovers — 26/26 `verified-write` terminal receipts;
  the three already-closed children were preserved and no routine progress was
  copied into the parent.
- create attempts initially returned `unverified-write` after mutation because
  immediate provider discovery returned zero rows. A distinct read-only
  discovery later found exactly #734 and #733 with byte-identical bodies and
  titles. Recovery attempts returned `already-exists` with no second mutation.
- relation adds — #734 and #733 each `verified-write` with relationship
  readback.
- relation removal — #3 `verified-write` with relationship readback.
- final exact graph — 31 children, 3 completed, 28 open, missing 0, unexpected
  0; see the dedicated readback artifact.

## Boundary decisions and non-claims

- `Critique: not-run operator-directed exception`. The user explicitly
  directed this implementation to use the `impl` contract and closeout format
  without forced fresh-eye review, handoff update, or micro-slices. No fresh-eye
  approval is claimed.
- `Handoff: not-updated operator-directed exception`; `docs/handoff.md` was not
  changed.
- `/goal #724` clean-consumer pickup was not run. The parent marker remains
  `bootstrap_verification: pending-target-roundtrip`.
- `goal-run-close` was not invoked; #724 remains `OPEN` with open children.
- no child issue was closed, and no push, release, tag, remote-CI, or
  installed-host mutation was performed.
- this closeout proves the selected live provider operations and exact graph
  readback; it does not prove installed-host adoption or clean `/goal` runtime
  behavior.

## Residuals

- The first create attempts remain preserved as honest `unverified-write`
  receipts; the later exact discovery/reuse receipts are the recovery proof.
- The worktree contains pre-existing and current uncommitted changes. No
  `--no-verify` commit was made. The normal commit/boundary gate remains a
  separate owner decision.
- Orchestration clean pickup and the evidence-consumer census/cutover remain
  the next approved child sequence; they are not silently marked complete by
  this provider closeout.

## 2026-08-27 provider contract completion

The implementation landed in commit
`35240a200ea77e82a64d9e719d9ae14f2f2e5518`. The standing provider target passed
`8` tests and the combined provider/runner/pickup/binding/lineage target passed
`65` tests. Pre-commit also passed the provider py_compile, Ruff,
skill-contract/evaluation, bootstrap-shim, standalone-import, mirror-drift, and
boundary-bypass checks. The exact command output is retained in the local
verification logs and summarized in the Goal Run provider body.

The live adapter readback was re-run after the implementation commit:
`goal-run-preflight` returned `ready` with all nine Goal Run operations and all
ten backend operations; `goal-run-read` returned parent #724 with `31` children,
`3` completed, and `28` open. No mutation was invoked by either read.

The repo-wide changed-line mutation wrapper was deliberately not treated as a
blocking gate for this provider implementation after the goal's friction-reset
amendment. Its clean named-worktree attempt exposed uncovered lines in the whole
provider mutation pool and is recorded as a non-claim, not as a provider defect.
The guarded-close proof remains focused on the open-child and generic-carrier
refusal paths. No fresh-eye, handoff, or micro-slice result is claimed.
