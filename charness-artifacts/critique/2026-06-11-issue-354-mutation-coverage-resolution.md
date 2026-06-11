# Resolution Critique — #354 mutation changed-line subprocess coverage

Date: 2026-06-11
Issue: #354 (scheduled mutation changed-line coverage reported blockers for
issue scripts even though the relevant tests exercised those paths).
Goal: `charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`
Packet Consumed:
`charness-artifacts/critique/2026-06-11-101503-packet.md`

## Execution

Fresh bounded subagent review used three code-critique angles
(problem framing, diagnostic/root cause, operational/checklist) plus one
separate counterweight pass.

- Fresh-Eye Satisfaction: parent-delegated.
- Target reference: code-critique / issue-resolution critique.
- Requested tier: high-leverage per repo adapter for issue closeout, with the
  reviewer-effort policy change in this same slice adding a routine medium tier
  for lower-risk future reviews.

## Change

The resolution fixes a CI-only changed-line false negative by making
`tests/quality_gates/support.py::run_script()` invoke `sys.executable` instead
of `python3` resolved through caller-provided `PATH`. A regression test shadows
`python3` with a fake executable and proves the helper still uses the current
interpreter.

The same slice updates the `nose 0.6.0` integration and advisory scanner command
surface, syncs plugin exports, removes stale issue/version anchors from reusable
public guidance, and documents a routine medium-effort reviewer path.

## Findings

- **Act Before Ship: none.** All three angle reviewers agreed the #354 fix
  targets the recorded failing path rather than an adjacent mutation-score
  symptom.
- **Bundle Anyway (folded): nose command-contract tests.** Reviewers found that
  fake nose tests could pass while the scanner regressed to removed legacy flags.
  This was folded before closeout: fake nose tests now assert `--min-size 24`
  and the absence of `--threshold`, `--min-lines`, and `--min-tokens`.
- **Bundle Anyway (folded): fake nose version alignment.** The fake CLI help had
  been updated to the 0.6 surface while `--version` still reported `0.4.0`.
  This was folded to report `nose 0.6.0`.
- **Valid but Defer:** `tests/control_plane/support.py` still invokes
  `["python3", *args]`. This is the same defect family, but it is outside the
  #354 failing quality-gate path and is not a blocker for this carrier.
- **Over-Worry:** broad conversion of every literal `python3`, clone refactors,
  changing `nose` itself, or rewriting historical provenance docs is not
  justified by this issue.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_nose_advisory.py | action: fix | note: folded assertions for `--min-size 24` and legacy flag absence.
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/tool_fakes.py | action: fix | note: folded fake nose version/help alignment to the 0.6 surface.
- F3 | bin: valid-but-defer | evidence: strong | ref: tests/control_plane/support.py | action: defer | note: same interpreter defect family remains outside the #354 failing path.
- F4 | bin: over-worry | evidence: moderate | ref: n/a | action: document | note: broad `python3` conversion, clone refactors, `nose` changes, and provenance rewrites stay out of scope.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium,
  service_tier=priority, agent_type=explorer, read-only prompts.
- Host exposure state: requested_fields_sent
- Application state: host accepted the spawn requests and returned completed
  reviewer notifications for `019eb62e-1a1f-7a10-9234-cdb3c0aa7451`,
  `019eb62e-1ac6-7cb3-98e4-eb625d2a98f1`,
  `019eb62e-1b0d-7062-9e0d-e8bc237dd692`, and
  `019eb632-f4c2-73e0-9330-72fbade48ab2`.

## Fresh-Eye Satisfaction

parent-delegated — bounded reviewers found no Act Before Ship blockers. The two
cheap Bundle Anyway items were folded and the counterweight pass confirmed no
remaining pre-ship action beyond normal deterministic verification and commit
closeout.
