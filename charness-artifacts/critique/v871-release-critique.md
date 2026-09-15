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

Canonical worker admitted and completed with `delivery_state: findings-received`, `boundary_mode: read-only-worker`, identities matched. Two earlier generic workflow rounds are disclosed above as evidence-empty and carry no weight.
