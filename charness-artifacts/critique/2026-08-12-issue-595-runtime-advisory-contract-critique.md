# Issue 595 Runtime Advisory Contract Critique
Date: 2026-08-12

## Decision Under Review

Make `latest_spikes` and runtime-visibility findings explicit advisory contracts
across human and structured runtime-budget output, without changing the enforced
recent-median verdict.

## Failure Angles

- A one-off contended sample could accidentally become a release-blocking failure.
- An advisory reason shown only in human output could disappear for JSON/YAML readers.
- Visibility gaps could be mislabeled as ignored gate inputs when the quality
  summary already owns their recommended action.

## Counterweight Pass

- Keep latest-only spikes non-failing: D54 and the live 108044ms/90895ms
  `pytest-release` observation support median enforcement; median drift remains red.
- Carry the same contract in `advisory_contracts` for detail, JSON, and summary
  output; this is a real reader, not merely a source comment.
- Retain weak visibility output and identify `render_runtime_summary.py` as its
  final consumer rather than introducing a false execution failure.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: document | note: latest-only spike now declares its advisory reason and recent-median enforcement basis in all output forms.
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/check_runtime_budget.py | action: document | note: summary output retains the advisory contracts for machine readers.
- F3 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_runtime_budget_gate.py | action: defer | note: converting a latest-only spike into a failure would reject contended one-off samples while the preserved median-drift test already proves the red path.
- F4 | bin: valid-but-defer | evidence: moderate | ref: docs/deferred-decisions.md#d54-should-a-per-gate-runtime-budget-measure-the-gates-own-work-rather-than-contended-wall-clock | action: defer | note: cross-host contention and per-host budget sizing remain unproven here.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: task_name `issue595_r1`; read-only scope; critique packet path; no model override.
- Host exposure state: metadata-hidden
- Application state: n/a — host exposes completion findings but no typed reviewer-tier confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-144548-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-144548-packet.json
- Packet SHA256: ff069a29fd198641bbf711314a8a5976841f88a21986e23321349af1c9094aa1
- Identity SHA256: 62f61abe81b05062b864562ac626e0d2e16df9b53f6120155007ccbcb6cf2115

## Boundary Ownership

- Producer: `runtime_budget_lib.evaluate()` derives spike and visibility observations.
- Consumer: `check_runtime_budget.py` exposes the advisory contract; `render_runtime_summary.py` consumes visibility recommendations.
- Owning surface: quality runtime budget/reporting seam.
- Verdict: owned-correctly
