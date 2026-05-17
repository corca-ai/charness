# Critique: Issue #171 Usage Episodes Final Follow-Up

Execution: completed with parent-delegated bounded fresh-eye reviewers.

Fresh-Eye Satisfaction: parent-delegated

Packet Consumed:
`charness-artifacts/critique/2026-05-17-issue-171-final-branch-critique-packet-packet.md`

Target: code critique

Change: final branch critique of `origin/main..HEAD`, covering `f05c779`,
`82e58ac`, and `836e4d1`.

## Counterweight Triage

### Act Before Ship

- Fix incomplete consumer `integrations/usage-episodes/` shadow directories.
  The validator should not choose a consumer schema directory unless both schema
  files exist; otherwise an empty product-side directory can traceback before
  reporting `no_adapter`.
- Add sibling issue links before closing #171: `corca-ai/ceal#102`,
  `corca-ai/crill#10`, and `corca-ai/cautilus#45`.
- Keep the final critique packet as durable critique state rather than leaving
  it untracked.

### Bundle Anyway

- Clarify setup wording so product repos know validation comes from the
  Charness/plugin-provided validator.
- Add plugin validator smoke coverage, not only checked-in file parity.

### Valid But Defer

- Invalid adapter error formatting can be made friendlier later. Current output
  is structured, non-traceback, and status-classified.

### Over-Worry

- Do not add Ceal/Crill emit hooks, dashboards, cross-product aggregation, or
  automaticity scoring in this slice.

## Pre-Merge Action

The act-before-ship and cheap bundle concerns were remediated in the follow-up
patch after this critique.
