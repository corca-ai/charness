# Retro: #280 Corca-internal last-seen product review

## Mode

session

## Context

This retro covers the #280 goal slice that added a Corca-internal last-seen
product-review reporter for usage episodes. The work changed a checked-in
plugin export surface, product-success docs, quality attention-state metadata,
and reporter tests.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`
- Fresh-eye critique: three parent-delegated bounded reviewers covering
  privacy/product semantics, CLI failure modes, and packaging/validation.
- Focused tests: `pytest -q tests/test_usage_episodes_report.py
  tests/test_usage_episodes_schema.py` passed with 63 tests.
- Closeout rehearsal: `python3 scripts/run_slice_closeout.py --repo-root .
  --skip-broad-pytest --ack-cautilus-skill-review` passed.
- Verification-lock closeout: `python3 scripts/run_slice_closeout.py
  --repo-root . --verification-lock --ack-cautilus-skill-review` passed,
  including broad pytest in 277.4s.

## Waste

- The first reporter version reached fresh-eye review with several privacy and
  execution edge cases still open: empty windows read as `usage_observed`,
  `classification_skipped` alone could become actionable, target refs could be
  posted into mutating comments, and `gh`/window errors were not structured.
  The critique caught these before commit, so this was not shipped waste, but
  it did push the slice through another implementation/test/sync loop.
- The public-skill dogfood acknowledgement surfaced only at
  `run_slice_closeout`. That was the right gate, but the attention-state
  reference edit made `quality` dogfood review predictable earlier from the
  changed-surface map.

## Critical Decisions

- Keep last-seen as a review-window field and emit `no_usage_observed` for empty
  windows instead of interpreting inactivity.
- Post at most one combined GitHub comment per execute run, with target refs
  redacted by default, so mutating side effects are easier to reason about.
- Treat the `quality` public-skill change as deterministic attention-state
  coverage, not a new evaluator scenario; freeze that in
  `docs/public-skill-dogfood.json`.

## Expert Counterfactuals

- Gary Klein: run the premortem against the mutating path first. The likely
  failure modes were "wrong signal becomes action" and "private context leaks
  into a durable external comment"; testing those before the happy path would
  have reduced the post-critique loop.
- Daniel Kahneman: separate dashboard evidence from action-trigger evidence in
  the data model earlier. That would have made `classification_skipped` and
  empty windows obviously non-actionable before code review.

## Next Improvements

- workflow: for reporter scripts that can mutate external state, write edge
  fixtures before broad happy-path tests: empty window/no data, missing binary,
  partial/multi-action failure, and privacy redaction. Disposition: applied in
  `tests/test_usage_episodes_report.py` for this reporter.
- capability: no new gate needed. Existing fresh-eye critique plus
  `run_slice_closeout` caught the issue before commit; the right improvement was
  targeted tests and the dogfood registry note, both committed in this slice.
- memory: record in the goal artifact that the privacy review findings were
  applied, not deferred. Disposition: applied in the goal slice log.

## Sibling Search

Searched `scripts`, `tests`, and `docs` for `gh issue comment`,
`execute_comments`, `target_refs`, `classification_skipped`,
`no_actionable_packets`, and broad `--execute` usage. No sibling reporter path
posts thresholded product-review packets or carries the same
last-seen/identity-redaction risk. Existing release/helper execute surfaces have
their own release or support-tool tests and were not changed by this slice.

## Persisted

yes `charness-artifacts/retro/2026-06-03-280-corca-internal-usage-last-seen-product-review.md`
