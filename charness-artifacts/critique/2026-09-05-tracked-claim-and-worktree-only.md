# Critique: tracked-claim ephemeral carrier and worktree-only retention

Date: 2026-09-05

## Decision Under Review

Ship the class fix for a tracked public claim whose only on-disk proof lives in
hidden runtime (#764 sampler baseline), plus the #797 keep_worktree sibling
already in this tree.

## Verification Scope Decision

- Claim under test: a clean clone validates `worker-delivered` critiques, and a useful worktree-only lane candidate survives as a lane-branch commit.
- Changed surfaces: `skills/shared/scripts/reviewer_worker_carrier_support.py`, `skills/public/critique/scripts/run_review_support.py`, `scripts/task_run/task_run_completion.py`, `charness-artifacts/critique/workers/`; consumers are `--all` on a clean clone and `charness task run` parents.
- Minimum sufficient proof: hidden-runtime refusal fixture; promote/overwrite tests; retargeted 2026-09-04 critiques pass `--paths`; live-corpus `--all`; task-run persist tests.
- Deliberately omitted checks: hosted mutation budget after sampler green.
- Verifier contract: `scripts/review/validate_critique_artifacts.py` (unchanged) and standing pytest on the changed modules.
- Failure classification: subject-defect
- Negative control: command: `python3 scripts/review/validate_critique_artifacts.py --repo-root . --paths charness-artifacts/critique/2026-09-04-impl-debug-route.md` | expected refusal: worker report carrier is hidden runtime or does not exist inside the repository | observed result: exit 0 after retarget to `charness-artifacts/critique/workers/impl-debug-route-final-3/worker-report.yaml` | receipt: validator stdout `Validated 1 critique artifact(s).` in this session
- Subject identity: sha256:f7cd6251b6c2994aead133c7efd5095dddcb87ccf7e5c0772d64e795113491a6
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:4b60b6dea73eb55be3335e3b28ca3e466046ba657f3075c04f3e59b2ca5ef38d
- Failure identity: stable:tracked-claim-ephemeral-carrier
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:55dc0637c6f2d80fb06a8150e5c8fa69a73dc42ffe267d35550786e4de05bc20

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: typed bounded-reviewer
- Host exposure state: host-defaulted
- Application state: n/a
- Delivery state: findings-received
- Execution mode: typed-subagent
- Worker report: none (typed-subagent path; findings text reached the parent context)

## Fresh-Eye Satisfaction

parent-delegated; two bounded reviewers (contract/behavior of `_report_path`,
simplification/operability of promotion). Act-before-ship items applied:
public carrier refuses hidden runtime; nested receipt/ledger/output still
`allow_hidden=True`; emitted `paths.report` rewritten to the durable copy;
durable dest refuses overwrite; only `approval_eligible: true` reports are
promoted. Bundle-anyway absolute-path fixture added. Deferred: mutation job
budget.

## Boundary Ownership

- Producer: `run_review` runtime dir and critique artifacts that cite a carrier.
- Consumer: `validate_critique_artifacts.py --all` on a clean clone; task-run
  parent integrating a useful candidate.
- Owning surface: `reviewer_worker_carrier_support._report_path` and
  `task_run_completion.persist_incomplete_candidate`.
- Verdict: owned-correctly

## Counterweight

- Act Before Ship: applied as above.
- Bundle Anyway: absolute hidden-path fixture landed.
- Over-Worry: attempt-id traversal; plugin export already contained the shared
  helper after standing pytest.
- Valid but Defer: mutation `timeout-minutes` vs mutant ceiling; killed-lane
  `status=running` persistence (`follow-up: deferred #797 third`).
