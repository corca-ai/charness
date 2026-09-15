# Release Critique Artifact — charness 8.7.1 (patch)

- **Kind**: release critique record for publish boundary
- **Generated**: 2026-09-15
- **Release**: 8.7.1 (patch: muse lane workspace fix #814, mutation probe fixes #764)
- **Reviewed input**: range v8.7.0..98431a41c (two fix commits + one test-strengthening commit)
- **Substrate**: canonical file-backed worker (`run_review.py --range v8.7.0..HEAD`, codex_exec backend) with packet `charness-artifacts/critique/review-20260915T111832Z-2567909-packet.json`; two prior generic workflow rounds admitted reviewers but returned evidence-empty results and are recorded as method failure, not evidence
- **Reviewer verdict**: block (procedural only — no code defect found)
- **Worker records**: `charness-artifacts/critique/workers/review-20260915T111832Z-2567909/` (packet, receipt, partial-result.json with findings `release-evidence-not-bound-to-8.7.1` and `mutation-probe-runtime-unproven`)

## Findings (both procedural, neither a code defect)

1. `release-evidence-not-bound-to-8.7.1` (blocking): packet and receipts still identify 8.7.0; no 8.7.1 metadata, claims review, or bound quality receipt exists yet. Expected: critique runs before mutation. Satisfied by continuing prepare → quality → claims, not by code change.
2. `mutation-probe-runtime-unproven` (blocking): focused mapper/sampler tests must run at the final candidate head with preserved receipts. The tests were run green locally (199 passed across the mutation/changed-line area) but without bound receipts. Satisfied by the publish helper's quality run.

## Counterweight Disposition (parent)

- Triage bins `not-a-blocker` / `intended-tradeoff` / `already-honestly-bounded` accepted as written (muse single-workspace, round-robin tradeoff, 8.7.0 HTTP observation limit).
- No Act-Before-Ship code item exists. The two blocking findings demand exactly the next workflow steps (8.7.1 prepare, bound quality, claims review over the prepared record). Proceeding to publish `--execute` is the disposition, not a bypass: the claims round and bound receipts are still mandatory before publication completes.
- Non-claims (from the worker): direction of neither patch fix is rejected; historical 8.7.0 evidence is not treated as 8.7.1 proof.

## Fresh-Eye Satisfaction

worker-delivered — pass with no findings. A canonical file-backed worker (codex_exec backend, read-only boundary) reviewed the release content plus bound evidence and approved the release; the parent consumed the full result. Earlier rounds are disclosed as method history: two generic workflow rounds returned evidence-empty results and carry no weight; three worker rounds returned procedural and evidence-completeness findings only, each closed by the dispositions below and the bound probe artifacts.

## Second-Round Dispositions (parent counterweight)

- **F1 (basename over-match vs capped budget)**: FIXED in `e61e13959` — ambiguous stem-only matches now sort last (ordering only; recall unchanged). Verified: duplicate-stem negative control added (`test_ambiguous_stem_matches_spend_budget_last`); only 10 of 805 repo stems are duplicated and none belongs to this release's files, so the release probe selection (RR-40) is byte-identical before/after. Static imports were already path-precise.
- **F2 (real-Muse boundary proof)**: satisfied by the persisted lane roundtrip probe `charness-artifacts/probe/2026-09-15-v8.7.1-muse-lane-roundtrip.json` (final tree: single worktree workspace, trusted, shell+git usable, `probe-871.txt` at root committed `b10a94e3`, approval-eligible, exit 0). Delegation beyond the trust flag was not exercised, so the docs claim was narrowed to the observed log lines (`docs/agent-task-runs.md`).
- **F3 (sync + verification rebind)**: plugin manifests sync clean; focused suites (227 passed) + full Stryker dry-run green at the final head in `charness-artifacts/probe/2026-09-15-v8.7.1-verification-receipts.json`; full release quality is red on exactly one test — this artifact's own typed-value conformance, the item under resolution. Publish resume's bound gates re-verify before tag push.
- **F-round5 (evidence completeness, delegation claim, mutation staleness)**: delegation claim narrowed as above; verification receipts regenerated at the final head; full Stryker rerun bound in the receipts file. Residual changed-line debt for the old range measures 20 statement targets (down from 163), all in probe-unselected or layout-fallback lines; ordinary incremental debt, not a release blocker (release's own new lines are covered — pre-push changed-line gate passed on both fix pushes).

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: adapter file-backed-worker / codex_exec; configured worker selection
- Host exposure state: host-defaulted
- Application state: file-backed read-only worker delivered; no provider-confirmed model or effort application claim
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/review-20260915T115945Z-2867499/worker-report.yaml
- Worker report identity: e7abe932bf4710dc647ace310cf5561385770f94e2d660488932142af691af59
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 43936bb3092fecad6f665d30ad27c7c281aeb51ef63e953cd3dec5f400f79c7d
- Worker report input identity: 91d2e16a1d9643ccb8c240b74f509fbd1df696bcd7f1de6447855e43a085e61b
- Worker report parent receipt identity: parent-e2ff0689139e77c5c6e9e8b2e72546074133f56a388a2faa
- Worker report findings identity: 9ab4df41b504fed9cfe1b339917dbf9928b51b3985cd1b803f93151f01d834c4

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/review-20260915T115945Z-2867499-packet.json
- Packet path: charness-artifacts/critique/review-20260915T115945Z-2867499-packet.json
- Packet SHA256: 43936bb3092fecad6f665d30ad27c7c281aeb51ef63e953cd3dec5f400f79c7d
- Identity SHA256: 91d2e16a1d9643ccb8c240b74f509fbd1df696bcd7f1de6447855e43a085e61b

Verified current with:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/review-20260915T115945Z-2867499-packet.json --packet-sha256 43936bb3092fecad6f665d30ad27c7c281aeb51ef63e953cd3dec5f400f79c7d --identity-sha256 91d2e16a1d9643ccb8c240b74f509fbd1df696bcd7f1de6447855e43a085e61b
```

## Boundary Ownership

- **Producer:** `scripts/task_run/` lane-runner owners (muse workspace/trust invocation, receipt block) and `scripts/mutation/` sampler owners (budget sharing, match ordering, JS slice config)
- **Consumer:** parent orchestrators reading `task run` receipts and the scheduled mutation gate reading the sampler/mapper contract, plus operators reading `docs/agent-task-runs.md`
- **Owning surface:** task-run lane surface and mutation probe surface (implementation, tests, docs move together in this change; no producer-owned state encoded in a foreign layer)
- **Verdict:** `owned-correctly` — each fix lives with its owner (lane invocation with the lane runner, probe allocation with the sampler, match order with the mapper) and is consumed where that owner publishes.
