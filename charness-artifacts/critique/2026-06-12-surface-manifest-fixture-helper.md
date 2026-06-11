# Surface manifest fixture helper critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-223545-packet.md

## Decision Under Review

Extract repeated temporary `surfaces.json` fixture setup in
`tests/quality_gates/test_run_slice_closeout_surface_obligations.py` into
`demo_surface()` and `write_surface_manifest()` helpers.

## Failure Angles

- Problem framing: this could be abstraction churn if the helper hid the
  behavior under test. Verdict: call sites still name the behavior-specific
  fields (`derived_paths`, `sync_commands`, `verify_commands`, `notes`, and
  expanded `source_paths`) while removing repeated manifest schema boilerplate.
- Semantic drift: truthiness defaults such as `source_paths or ["README.md"]`
  would make explicit empty lists impossible in future tests. Verdict: fixed by
  using explicit `is not None` defaults for every optional list field.
- Verification: broad repo pytest is not required for the reviewer pass on a
  fixture-only refactor. Verdict: focused ruff, whitespace check, and focused
  pytest cover the changed file; parent closeout owns broader gates.

## Counterweight Pass

- Act before ship: none.
- Bundle anyway: the optional-list default fix has already been applied.
- Over-worry: schema boilerplate hiding is not a blocker because the helper is
  local to the test file and keeps the manifest shape visible near the tests.
- Valid but defer: broad repo-python gates belong to parent closeout.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_run_slice_closeout_surface_obligations.py:24 | action: fix | note: use explicit `is not None` defaults so future tests can intentionally pass empty lists.
- F2 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_run_slice_closeout_surface_obligations.py:44 | action: document | note: helper call sites retain behavior-specific fixture intent while removing repeated manifest boilerplate.
- F3 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/critique/2026-06-11-223545-packet.md:20 | action: defer | note: broad repo-python gates are parent closeout work; focused ruff and pytest are sufficient for this reviewer pass.

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
