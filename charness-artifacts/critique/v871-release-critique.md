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

worker-delivered — canonical file-backed worker admitted and completed with `delivery_state: findings-received`, `boundary_mode: read-only-worker`, packet/reviewed-input identities matched; findings in `charness-artifacts/critique/workers/review-20260915T111832Z-2567909/partial-result.json`. Two earlier generic workflow rounds are disclosed above as evidence-empty and carry no weight. A second worker round over the release content returned three substantive findings (F1 basename over-match risk, F2 real-lane proof, F3 evidence rebind) in `charness-artifacts/critique/workers/review-20260915T113134Z-2670374/partial-result.json`, dispositioned below; none is a code defect in the release content.

## Second-Round Dispositions (parent counterweight)

- **F1 (basename over-match vs capped budget)**: FIXED in `e61e13959` — ambiguous stem-only matches now sort last (ordering only; recall unchanged). Verified: duplicate-stem negative control added (`test_ambiguous_stem_matches_spend_budget_last`); only 10 of 805 repo stems are duplicated and none belongs to this release's files, so the release probe selection (RR-40) is byte-identical before/after. Static imports were already path-precise.
- **F2 (real-Muse boundary proof)**: satisfied by the persisted lane roundtrip probe `charness-artifacts/probe/2026-09-15-v8.7.1-muse-lane-roundtrip.json` (final tree: single worktree workspace, trusted, shell+git usable, `probe-871.txt` at root committed `b10a94e3`, approval-eligible, exit 0). Delegation beyond the trust flag was not exercised, so the docs claim was narrowed to the observed log lines (`docs/agent-task-runs.md`).
- **F3 (sync + verification rebind)**: plugin manifests sync clean; focused suites (227 passed) + full Stryker dry-run green at the final head in `charness-artifacts/probe/2026-09-15-v8.7.1-verification-receipts.json`; full release quality is red on exactly one test — this artifact's own typed-value conformance, the item under resolution. Publish resume's bound gates re-verify before tag push.
- **F-round5 (evidence completeness, delegation claim, mutation staleness)**: delegation claim narrowed as above; verification receipts regenerated at the final head; full Stryker rerun bound in the receipts file. Residual changed-line debt for the old range measures 20 statement targets (down from 163), all in probe-unselected or layout-fallback lines; ordinary incremental debt, not a release blocker (release's own new lines are covered — pre-push changed-line gate passed on both fix pushes).

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage` (release lock-in)
- **Execution mode**: `file-backed-worker` (codex_exec backend, read-only boundary)
- **Delivery state**: `findings-received` (verdict `block`, procedural only)
- **Application state**: `worker records committed beside the packet; packet and reviewed-input identities verified matched by the runner`

## Boundary Ownership

- **Producer:** `scripts/task_run/` lane-runner owners (muse workspace/trust invocation, receipt block) and `scripts/mutation/` sampler owners (budget sharing, match ordering, JS slice config)
- **Consumer:** parent orchestrators reading `task run` receipts and the scheduled mutation gate reading the sampler/mapper contract, plus operators reading `docs/agent-task-runs.md`
- **Owning surface:** task-run lane surface and mutation probe surface (implementation, tests, docs move together in this change; no producer-owned state encoded in a foreign layer)
- **Verdict:** `owned-correctly` — each fix lives with its owner (lane invocation with the lane runner, probe allocation with the sampler, match order with the mapper) and is consumed where that owner publishes.
