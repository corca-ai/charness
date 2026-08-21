# Retro Portability Boundary R2
Date: 2026-08-21

## Decision Under Review

Repair #685's documented artifact-name stem diagnostics and #686's installed
retro planner command carrier, then make an unavailable required skill probe
produce a typed not-ready envelope rather than an `ok: true` claim.

## Failure Angles

- A normal `.md` normalization could still look like caller failure on stderr.
- An installed planner could emit an authoring-checkout path or claim readiness
  while its required skill probe is unavailable.
- A source-only test could leave the checked-in plugin mirror or the final
  consumer's readiness channel unproven.
- Optional repo-owned validators could be accidentally promoted to false
  readiness blockers while repairing the required skill packet.

## Counterweight Pass

The ownership reviewer found no remaining same-class source/export defect: the
stem remains normalized with an explicit structured path, and the trigger probe
is owned by `$SKILL_DIR`. The retry operator reviewer independently confirmed
that `required: true` plus `available: false` yields `ok: false`,
`readiness.status: not-ready`, and the named blocking packet, while the
repo-owned validator remains optional and does not poison readiness.

The second bounded round read the repaired verdict surface and found three
consumer blockers: parent receipt case preservation, report-to-artifact
packet/input cross-binding, and stale final-packet binding. The first two are
repaired below. The final repair was made after round 2 and is explicitly
accepted-unreviewed under the two-round cap; no fresh-eye approval is claimed
for that repair.

Managed cache refresh, publication, and real-host consumer execution remain
release-boundary work. The temporary lack of a usable temp directory inside the
reviewer was requalified by the parent focused test run and is not treated as
code proof.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/retro/scripts/plan_retro_run.py:106-120,386-416 | action: fix | note: shipped skill probes now use `$SKILL_DIR`, carry `required: true`, and drive a typed readiness result instead of hiding unavailability behind `ok: true`.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_retro_installed_plan_path.py:14-66 | action: fix | note: source/export packet shape and the missing-required-probe negative branch are both exercised.
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/retro_persistence_lib.py:186-200 | action: fix | note: stem normalization remains successful, silent on stderr, and explicit in structured artifact path output.
- F4 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/skills/retro/scripts/plan_retro_run.py | action: fix | note: source and checked-in export copies are byte-identical after sync.
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md | action: defer | note: managed install/cache refresh and public or real-host readback remain release-lane non-claims.
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/critique_reviewer_evidence.py, scripts/critique_reviewed_input_binding.py | action: fix | note: worker-delivered evidence now preserves parent receipt case and joins report packet/input identities to the artifact's own Reviewed Input Identity.
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/reviewed_input_identity.py | action: fix | note: explicit validator repo-root propagation and artifact-layout-first fallback prevent nested .git ancestors from turning an existing packet into a false missing-path failure.
- F8 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_critique_enforcement_scope.py, tests/quality_gates/test_reviewer_delivery_state_machine.py | action: fix | note: mixed-case exact joins, malformed receipt IDs, foreign packet/input bindings, and producer-side error normalization are covered.
- F9 | bin: act-before-ship | evidence: moderate | ref: skills/public/critique/SKILL.md, skills/public/prove/SKILL.md | action: document | note: accepted-unreviewed-under-round-cap is a typed non-approval disposition for round-2 repairs and cannot be consumed as fresh-eye approval.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewer.
- Requested spawn fields: adapter-selected file-backed worker; `codex_exec`; read-only workspace; 900-second adapter timeout; no caller model/effort overrides.
- Host exposure state: metadata-hidden
- Application state: worker receipt confirms `execution_mode: file-backed-worker` and `backend: codex_exec`; model/effort application was not exposed.
- Delivery state: findings-received — round-2 validator, consumer, and counterweight findings are durably recorded; the post-round repair is accepted-unreviewed under the cap.

## Fresh-Eye Satisfaction

accepted-unreviewed-under-round-cap round-2 verdict-surface repairs were made
after the bounded reports below; the cap forbids a third fresh-eye run. This is
not fresh-eye approval and must remain a residual non-claim.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.json
- Packet path: charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.json
- Packet SHA256: 6345ed07ebe8a4cdf5c5c57651d522f6474aa9c493c6fcb9adf483f29f06170f
- Identity SHA256: af504394d553642db9aa4f9bbd38d6f2d1c9d0f06c56052dea4914f3b8148150

## Boundary Ownership

- Producer: `skills/public/retro/scripts/plan_retro_run.py` builds the skill and repo command packets and computes planner readiness.
- Consumer: the retro operator reads the packet command, availability, readiness status, and process exit code; critique/prove consumers read the typed fresh-eye disposition without upgrading the cap state to approval.
- Owning surface: the retro planner's skill-root carrier and readiness envelope, mirrored into `plugins/charness`.
- Verdict: owned-correctly
