# Quality bootstrap output/rendered-diff split critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-222543-packet.md

## Decision Under Review

Extract bootstrap output/rendered-diff logic from
`scripts/quality_bootstrap_lib.py` into `scripts/quality_bootstrap_render.py`,
preserving the existing `quality_bootstrap_lib.render_bootstrap_adapter` import
surface and syncing the plugin mirror.

## Failure Angles

- Problem framing: this could be line-moving churn if the extracted code lacked
  a real boundary. Verdict: the split leaves adapter detection/state/write
  orchestration in `quality_bootstrap_lib.py` while moving YAML emission and
  rendered-output write-suppression comparison to a one-way dependency.
- Diagnostic: this could break fresh checkouts if the new render module or its
  plugin mirror are not committed. Verdict: no import cycle or mirror mismatch
  was found; the remaining pre-merge action is including both new render files
  and the critique packet artifacts in the commit.
- Test sufficiency: direct private-helper tests would duplicate the existing
  public bootstrap path coverage. The defaulted-only short-circuit is already
  exercised by the focused bootstrap tests.

## Counterweight Pass

- Act before ship: stage the new source render module, plugin mirror render
  module, and critique packet artifacts with the modified bootstrap lib files.
- Bundle anyway: use "bootstrap output/rendered-diff logic" wording, not
  "render-only"; `diff_is_defaulted_only` is write-suppression policy coupled to
  rendered output.
- Over-worry: direct unit tests for the moved helper are unnecessary unless the
  helper becomes a public support API.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/quality_bootstrap_render.py:1 | action: fix | note: include the new source render module in the commit.
- F2 | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/quality_bootstrap_render.py:1 | action: fix | note: include the regenerated plugin mirror render module in the commit.
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_bootstrap_render.py:80 | action: document | note: describe the boundary as bootstrap output/rendered-diff logic, not render-only.
- F4 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap.py:276 | action: document | note: direct tests for the moved private helper would duplicate public-path bootstrap coverage.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: inherited parent model; no explicit model override sent
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted two bounded angle reviewer requests and one counterweight reviewer request; host did not confirm provider-side application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent spawned two bounded angle
reviewers and one separate counterweight reviewer through `multi_agent_v1`;
all completed read-only review. No same-agent substitute was used.
