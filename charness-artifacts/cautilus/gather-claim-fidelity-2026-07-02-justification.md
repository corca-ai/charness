# Gather claim-fidelity capture justification (2026-07-02)

## Behavior Source

- source-kind: issue-log
- source-ref: #411 (gather claim-fidelity floor redesign)
- failing-observation: charness-artifacts/cautilus/gather-claim-fidelity-slice7-2026-07-01/observed.current-spec-FAILED.v1.json
- failing-summary: the representative public-URL `/charness:gather` run scored
  outcome=FAILED, coverage 0/8 against the doc-open RCF floor — it opened ZERO of
  the 8 declared reference docs (including both RCF floors source-priority.md and
  capability-contract.md), while producing a faithful durable primary-source asset.

## What this run must verify

The redesigned honest floor for gather's public-URL default is the artifact/substance
instrument added this session (evals/cautilus/gather-claim-fidelity/outcome-assertions.json,
commit 3b650cb6), not the refuted doc-open RCF. This capture observes a real
`/charness:gather` public-URL run and grades it against that substance floor to verify
the instrument grades a genuine run correctly (durable primary-source asset produced,
honest access-mode + capture-vs-confirmation accounting, no search-widening substitution)
before the capture-gated RCF flip rides.
