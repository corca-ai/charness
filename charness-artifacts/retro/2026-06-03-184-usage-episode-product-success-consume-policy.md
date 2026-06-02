# Retro: Issue 184 Usage Episode Product Success Consume Policy

Mode: session

## Context

This retro covers the #184 usage-episode consume-policy goal. The slice changed
the product-success baseline, usage episode reporting, focused tests, plugin
exports, and the active achieve goal artifact. The product decision from the run
is conservative: ship the policy/report improvement, but keep #184 open because
current evidence shows capture without satisfaction proof.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-184-usage-episode-product-success-consume-policy.md`
- Changed docs/code/tests:
  `docs/product-success-metrics.md`, `scripts/report_usage_episodes.py`,
  `scripts/usage_episode_product_evidence.py`, `tests/test_usage_episodes_report.py`,
  and plugin mirrors.
- Fresh-eye critique: Hooke, Turing, Bernoulli, plus counterweight Hume.
- Verification: focused usage-episode tests, ruff, docs checks, packaging,
  integration validation, usage-episode validation, attention-state visibility,
  secrets, and live `report_usage_episodes.py`.

## Waste

- I initially treated `first_value_ref` too much like user-value evidence. The
  user correctly pushed back that Charness almost always leaves artifacts, so
  artifact existence cannot stand in for satisfaction. The resulting design is
  better: first-value is only an evidence floor; satisfaction and friction are
  separate signals.
- I accidentally ran `upsert_goal.py` without `--date` when activating the
  existing 2026-06-02 goal. That created a duplicate 2026-06-03 goal artifact,
  which I had to delete before continuing.
- The first implementation copied the policy phrase "one emitter" into prose but
  only checked trigger and entry point in code. Fresh-eye review caught the gap;
  the final helper now checks `single_emitter`.

## Critical Decisions

- Keep #184 open. The slice proves that current data cannot support a strong
  product-success claim: 407 captured episodes, 0% feedback coverage, 0
  satisfaction signals, and veto gaps for missing feedback, no satisfaction,
  single emitter, single trigger type, and single entry point.
- Treat unclassified feedback as a veto gap, not as satisfaction. This keeps the
  schema flexible while preventing arbitrary strings from inflating feedback
  coverage.
- Extract `usage_episode_product_evidence.py` instead of continuing to grow
  `report_usage_episodes.py`; this removed the changed script from the length
  warning band.

## Expert Counterfactuals

- Gary Klein would have asked, "What evidence would make us regret closing #184
  tomorrow?" The answer is exactly the live report: all records have artifacts,
  but none have feedback or satisfaction evidence.
- Donald Norman would separate output from outcome: an artifact is a system
  output, while satisfaction requires observable user acceptance, reuse, or
  reduced friction. That distinction should have been the starting frame.

## Next Improvements

- workflow: when using `upsert_goal.py` on an existing dated artifact, pass the
  explicit `--date` from the artifact path. Disposition: applied in this run by
  deleting the accidental duplicate and continuing on the user-provided goal
  artifact; no code change needed unless this recurs.
- capability: keep product-evidence logic out of the main report script once it
  grows beyond a simple summary. Disposition: applied by extracting
  `scripts/usage_episode_product_evidence.py`.
- product: do not close #184 until maintainer/source-thread synthesis and
  feedback/baseline evidence exist. Disposition: applied by leaving #184 open
  and recording non-claims in the goal artifact.

## Sibling Search

The transferable waste pattern is "policy names a veto, implementation only
checks a weaker proxy." Sibling scan was limited to this changed surface:
`usage_episode_product_evidence.py` now checks feedback, satisfaction, emitter,
trigger type, and entry point; `docs/product-success-metrics.md` names the same
classes. No additional sibling surface was changed in this run.

## Persisted

Persisted: yes, via `persist_retro_artifact.py`.
