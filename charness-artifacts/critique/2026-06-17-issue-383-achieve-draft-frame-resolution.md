# Issue 383 achieve draft-frame resolution
Date: 2026-06-17

## Decision Under Review

Resolve issue #383 by aligning `achieve` draft scaffold/default docs with the
adapter-contract draft lifecycle disposition, surfacing generic draft-frame
drift as a non-blocking `pursue-ready` warning, and keeping plugin mirrors and
dogfood evidence synchronized.

Packet consumed: `charness-artifacts/critique/2026-06-17-101456-packet.md`.

Success means the maintained consumer contract stays unchanged: `achieve`
still creates an inert draft artifact and `/goal @...` still owns activation;
the new warning is visible without becoming a new activation floor.

Out of scope: historical artifact migration, broad lifecycle redesign, and
release mechanics.

## Failure Angles

- Problem framing: the first diff fixed scaffold wording and warning visibility,
  but the adapter-contract YAML example accidentally nested `scaffold` under
  `auto_retro`, teaching the wrong adapter shape.
- Diagnostic/root-cause fit: the same nesting bug was the same drift class as
  issue #383 because a copied contract example would silently miss the
  adapter-owned draft frame and fall back to defaults.
- Operator interface: concise `charness goal check --pursue-ready` now surfaces
  `draft_frame_warning`; keeping the warning non-blocking avoids turning a
  visibility fix into another activation floor.

## Counterweight Pass

- Act Before Ship: none remaining. The YAML nesting concern was real and was
  fixed by making `scaffold` top-level in
  `skills/public/achieve/references/adapter-contract.md` and the generated
  plugin mirror.
- Bundle Anyway: the focused parser-backed regression was bundled in
  `tests/quality_gates/test_achieve_adapter_policy.py`; no broader markdown YAML
  parser sweep is justified by this slice.
- Over-Worry: do not make `draft_frame_warning` blocking. Tests preserve
  `pursue_ready is True` for a generic draft frame while surfacing the warning
  in helper JSON and concise CLI output.
- Valid but Defer: the detector is phrase-based. Extending acceptable lifecycle
  wording should wait until a concrete new phrase appears.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/references/adapter-contract.md:47 | action: fix | note: adapter-contract YAML nested `scaffold` under `auto_retro`; fixed by unindenting source and mirror docs
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_achieve_adapter_policy.py:87 | action: fix | note: parser-backed regression now asserts documented `scaffold` is top-level
- F3 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_goal_artifact_lib.py:134 | action: document | note: warning remains non-blocking; generic draft frames still report `pursue_ready`
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/scripts/goal_artifact_draft_frame.py:7 | action: defer | note: extend phrase-based disposition matching only when a concrete accepted phrase appears

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.5`, reasoning_effort `medium`, service_tier `priority`.
- Host exposure state: requested_fields_sent
- Application state: spawn tool returned reviewer agent ids `019ed514-2a20-70f1-915d-018a4f22b1ee`, `019ed514-2ae3-7c20-aac6-433fa6923913`, `019ed514-2b24-7490-aa19-1928863f784d`, and counterweight `019ed516-d289-7763-8c40-bdf2dac14665`; provider-side application is not separately visible.

## Fresh-Eye Satisfaction

parent-delegated. Three angle reviewers and one separate counterweight reviewer
ran through the host subagent tool. The angle reviewers found one real
act-before-ship blocker, it was fixed, and the counterweight found no remaining
act-before-ship work.
