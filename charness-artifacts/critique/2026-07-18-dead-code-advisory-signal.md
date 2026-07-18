# Dead-Code Advisory Signal Critique
Date: 2026-07-18

## Execution

Two distinct code-critique angles and one separate counterweight ran as read-only parent-delegated reviewers. Parent fingerprint verification reported `ok: true` and no drift after every reviewer.

## Packet Consumed

`charness-artifacts/critique/2026-07-18-133327-packet.md`

## Target

Code critique shaped by the diagnostic/implementation-integrity and problem-framing/compatibility angles.

## Decision Under Review

Reduce the dead-code advisory's false-positive review burden by classifying proven runtime-external conventions, while deleting repository-confirmed unused helper paths. Keep dynamic exports visible as review candidates.

## Capability at Stake

Maintainers need a credible attention list: framework dispatch and source-scanned contracts should not masquerade as deletable code, but a broad exception must not hide real dead code.

## Diff Scope

The diff adds AST role/provenance classification and focused tests, removes three obsolete helper surfaces and one unused setup constant, and synchronizes the checked-in plugin mirror.

## Failure Angles

- Diagnostic / implementation integrity: identifier-only source-scan exemptions and spelling-only framework recognition could suppress unrelated dead code.
- Problem framing / compatibility: helper deletion could solve advisory noise by breaking an undocumented consumer, or leave source/plugin mirrors divergent.

## Findings

- Both angle reviewers found the source-scanned exception over-broad. It now requires the declared `scripts/report_usage_product_review.py` path, with a negative same-name test for another file.
- One reviewer required import provenance for fixture and visitor conventions; the other judged it valid but deferrable because no lookalikes exist. The counterweight found the small provenance check proportionate, so the slice includes it and negative lookalike tests.
- Both angle reviewers found no checked-in consumer for the deleted helpers and confirmed source/plugin mirror parity.

## Counterweight Pass

- `Bundle Anyway`: retain the narrow path/name contract and import-provenance checks; both are small changes inside the touched classifier and close concrete suppression risks.
- `Over-Worry`: do not add compatibility shims for undocumented helpers with no repository consumer.
- `Valid but Defer`: direct-import-alias tests are absent, although the same binding helper implements that path; no observed defect justifies widening this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/run_dead_code_advisory.py | action: fix | note: resolved broad source-scanned identifier suppression by scoping the contract to its declared path and adding a negative test
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_dead_code_advisory.py | action: fix | note: resolved spelling-only fixture and visitor suppression with import provenance and lookalike tests
- F3 | bin: over-worry | evidence: moderate | ref: scripts/tool_recommendation_lib.py | action: document | note: no compatibility shim for undocumented helpers with no checked-in consumer

## Deliberately Not Doing

No general dynamic-export oracle or compatibility wrapper is added. The two remaining dynamic exports stay visible as advisory review candidates so human judgment remains the final decision.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`
- Host exposure state: requested_fields_sent
- Application state: host accepted the fields but did not independently expose provider-application confirmation.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: vulture findings plus the advisory's source-role classifier.
- Consumer: maintainer or agent deciding whether a candidate is removable.
- Owning surface: the quality advisory classifier; source-scanned membership remains anchored to the declaring path.
- Verdict: owned-correctly

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — validators must preserve judgment and avoid broad exemptions that manufacture a false clean state.

## Pre-Merge Action

Completed: narrow source-scanned membership, prove negative lookalikes, synchronize plugin mirrors, and rerun the focused advisory tests.

## Next Move

Run the repo-wide quality and locked closeout proofs, then treat release publication as a separate critique boundary.
