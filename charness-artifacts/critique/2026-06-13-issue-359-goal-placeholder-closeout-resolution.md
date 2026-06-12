# Critique Review
Date: 2026-06-13

## Decision Under Review

Issue #359 resolution: add an `achieve` complete-state section-placeholder floor so a goal cannot claim `Status: complete` while a goal-artifact section's first body line still carries a scaffold or closeout-pending placeholder.

Packet consumed: `charness-artifacts/critique/2026-06-12-231947-packet.md`.

## Failure Angles

- Michael Jackson / problem framing: the initial gate blocked completion but did not prove `upsert_goal` surfaced the same specific section/line diagnostic as `check_goal_artifact.py`.
- Gerald Weinberg / diagnostic: the initial `Pending` matcher was too broad and could reject legitimate completed prose starting with a non-placeholder `Pending <noun>` phrase.
- Atul Gawande / operator checklist: the initial scanner did not catch the shipped template's label-prefixed first line, `Retro dispositions: TODO ...`, so a no-improvement retro plus valid evidence could leave the real scaffold untouched.

## Counterweight Pass

- Act before ship: add complete-only CLI coverage, tighten `Pending` to `Pending until` / `Pending:`, detect label-prefixed placeholder values, and add template-shape tests.
- Bundle anyway: surface the specific `section_placeholders` summary in `upsert_goal` refusal output because the status-flip path is a common operator entry point.
- Over-worry: none. These are current template and complete-gate risks, not speculative future consumers.
- Valid but defer: none. The fixes are narrow and inside the current diff's blast radius.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_goal_artifact_lib.py | action: fix | note: add CLI coverage proving section-placeholder checks are complete-only
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_section_placeholders.py | action: fix | note: tighten Pending matching and detect label-prefixed TODO/TBD/FIXME placeholder values
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_lib.py | action: fix | note: include section/line/marker summary in upsert refusal output

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: applied
- Application state: host-confirmed: spawn_agent returned reviewer ids `019ebe22-90f9-7e40-91ef-ab78f4058179`, `019ebe22-aca9-75f1-b4fc-931da3c5d026`, `019ebe22-c7bf-7552-9335-ce17ca0f0a16`, and counterweight id `019ebe24-2f30-7f72-bc0c-c35e28cebd2e`.

## Fresh-Eye Satisfaction

parent-delegated. Three bounded angle reviewers and one separate counterweight reviewer completed; the Act Before Ship and Bundle Anyway findings were folded into the diff before final validation.
