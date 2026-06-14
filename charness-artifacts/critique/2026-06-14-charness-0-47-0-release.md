# Critique Review
Date: 2026-06-14

## Decision Under Review

Publishing charness release 0.47.0 (minor, 0.46.0 → 0.47.0): bundles the #362
aggregate doc-authoring preflight (`scripts/check_doc_authoring_preflight.py`),
the non-blocking `advise_doc_surface_preflight` slice-closeout advisory, the
discoverability doc sections, and the goal/retro/critique closeout artifacts.
Release-hygiene critique: is the bump level, update_instructions, generated
surfaces, operator risk, and issue-close hygiene honest and safe to publish?

## Failure Angles

- **Wrong bump level.** Patch would under-state new capability; major would
  over-state (no break). Either misleads operators on what to expect.
- **Stale/overclaiming update_instructions.** Calling the preflight a blocking
  gate, or claiming no consumer impact when the advisory ships in the plugin,
  would mislead the next maintainer/consumer.
- **Stale generated surface.** A bump that leaves packaging vs plugin manifests
  vs marketplace disagreeing, or a plugin mirror drifted from source.
- **Wrong issue-close hygiene.** Re-closing #362 (already closed) or closing
  the open follow-ups (#363/#364) prematurely.

## Counterweight Pass

- Bump: MINOR is the lightest honest level (new capability, no migration) —
  confirmed against the version policy. Not a concern.
- update_instructions: the entry explicitly frames the preflight as an
  affordance and the advisory as non-blocking — verified against the code. The
  one real softness (shipping-boundary disclosure) was the reviewer's nit #1 and
  is now fixed (see Structured Findings F1). Not a blocker.
- Generated surfaces: all surfaces consistently at 0.46.0 pre-bump; the single
  `sync_command` regenerates plugin + both marketplace files atomically; plugin
  mirrors byte-identical to source on HEAD. Not a concern.
- Issue hygiene: correctly NOT passing `--close-issue` (#362 already CLOSED;
  #363/#364 are genuine open follow-ups). Verified live. Not a concern.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: moderate | ref: .agents/release-adapter.yaml | action: fix | note: update_instructions wording "advisory only fires on charness's repo-root closeout" under-disclosed that run_slice_closeout.py + slice_closeout_advisories.py ARE byte-shipped in the plugin (an opt-in consumer running run_slice_closeout.py on a docs/*.md edit would see the stderr pointer; it never auto-fires on upgrade). Tightened the wording this run (commit fae62395) to the precise "does NOT auto-fire on charness update; opt-in only; non-blocking" framing.
- F2 | bin: over-worry | evidence: strong | ref: staged_commit_gate_plan.py | action: defer | note: consumer-visible-behavior-on-upgrade risk — none: no githooks are shipped/wired by the installer; the advisory is a pure non-blocking stderr print. No action.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage bounded fresh-eye reviewer (separate agent context, read-only).
- Requested spawn fields: release context, the five release-hygiene dimensions (bump level, update_instructions accuracy, generated-surface honesty, operator risk/publish boundary, issue-close hygiene), and a git-show-backed evidence requirement.
- Host exposure state: applied
- Application state: host-confirmed: subagent a96aecdbe3cb5ff25 completed; returned a per-dimension scored verdict (4.5–5/5 across all five) with git show citations and one actioned nit.

## Fresh-Eye Satisfaction

Reviewer verdict: **PUBLISH-WITH-NITS — no blockers.** Per-dimension: bump 5/5
(minor correct per version-policy), update_instructions 5/5 (no overclaim;
affordance/non-blocking framing verified), generated-surface 5/5 (byte-identical
mirrors, atomic sync, consistent pre-bump versions), operator risk 4.5/5 (no
upgrade-time behavior change; the only nuance is the opt-in shipped advisory
path — nit #1), issue-close hygiene 5/5 (#362 CLOSED, #363/#364 correctly left
open, no `--close-issue`). Nit #1 was applied this run (fae62395) so the
shipping-boundary disclosure is now strictly accurate.
