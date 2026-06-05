# Retro: Issues 299 300 and next improvements

## Context

This session ran an `achieve` goal for the user's next-improvement request plus
GitHub issues #299 and #300. #299 was already locally implemented and verified;
#300 was the new implementation slice. The user's report-quality feedback was
also in scope.

## Evidence Summary

- `gh issue view` for #299 and #300.
- `issue_tool.py resolve-invocation -- 299-300`.
- `issue_tool.py validate-closeout-draft` for #299 and #300.
- Focused setup/achieve/#299 tests: 19 passed.
- `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`.
- Fresh-eye review by Carson and follow-up critique artifact.

## Waste

- I initially put `normalize_host_docs.py --execute` in the generic setup
  bootstrap path. That would have made ordinary setup startup mutate host docs
  before mode detection. Fresh-eye review caught it; fixing it was necessary
  but avoidable.
- The goal artifact lagged behind the implementation for one slice. That
  created review churn because the issue draft claimed implementation while the
  goal still said the work was pending.
- I had to repair the closeout evidence chain after #300 draft validation failed
  on missing critique evidence. The validator did its job, but I should have
  created the critique artifact before drafting the closeout carrier.
- The previous habit of including routine push questions created user-facing
  noise. This goal changed the contract, but the waste was already paid in the
  earlier correction loop.

## Critical Decisions

- #299 was treated as carry/verify, not reimplementation, because local commit
  `9e2ca12b` and the existing closeout draft already verified the local
  implementation boundary.
- #300 stayed feature-class, not bug-class. There was no causal divergence to
  debug; the gap was a missing narrow execution path.
- The setup bootstrap command was kept dry-run by default; `--execute` belongs
  only after the explicit host-docs-only mutation path is selected.
- Broad pytest was not rerun during pre-lock closeout. Focused tests and the
  slice closeout rehearsal were the right proof level for this mutation set.

## Expert Counterfactuals

- A release-engineering reviewer would have treated the generic bootstrap line
  as a mutation hazard immediately and insisted that every bootstrap command be
  read-only unless labeled as the selected mutation.
- A technical-writing reviewer would have caught the report mismatch earlier:
  if the user asks for actual waste, the final response shape must reserve a
  waste section before implementation summary.

## Next Improvements

- Keep setup bootstrap examples dry-run/read-only unless the line is explicitly
  inside the selected mutation step.
- Update goal artifacts as soon as a slice moves from implementation to review,
  not only at final closeout.
- For issue closeout drafts, create or bind critique evidence before running
  `validate-closeout-draft` so the first validation pass is meaningful.

## Sibling Search

- Transferable pattern: unsafe mutation command in a generic bootstrap block.
- Searched sibling surfaces: setup bootstrap, setup agent-doc policy, generated
  setup plugin mirror, and closeout command docs. No other generic bootstrap
  line was changed to an unconditional mutation command in this slice.

## Persisted

yes — `charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md`
