# Retro persistence goal-aware design critique
Date: 2026-08-04

## Decision Under Review

The activation-ready goal
`charness-artifacts/goals/2026-08-04-retro-persistence-goal-aware.md`.
It proposes an opt-in `--goal-path` at the retro persistence boundary, exact
field-bound identity matching, fail-before-write behavior, and unchanged
ordinary session-retro behavior while resolving #504.

## Failure Angles

- Ownership/API: a slug-only or caller-supplied identity could drift from the
  canonical goal file, and the direct release caller could accidentally break.
- Write integrity: validating only the CLI or only four named outputs could miss
  direct-library writes, event append/rotation/deletion, or new directories.
- North-Star counterweight: a universal retro-quality gate, forced goal scope,
  #496 bundling, or early remote publication could add more teeth than the
  recorded failure warrants.

## Counterweight Pass

- Act Before Ship: define one exact `Goal:` metadata grammar and test malformed,
  missing, different, and incidental-prose cases; validate at the library
  boundary; snapshot the complete side-effect tree.
- Bundle Anyway: keep direct-library compatibility, the release caller's
  omitted-goal case, source/plugin mirror checks, and enabled t-events in the
  same proof bundle.
- Over-Worry: semantic judgment of lesson quality, a new general closeout gate,
  combining #496, and remote proof during implementation.
- Valid but Defer: automatically migrating every achieve producer beyond the
  known persistence boundary, unless caller inventory finds a real escape.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: goal Boundaries and Interview Decisions; #504 carrier | action: fix | note: pin exact field-bound identity and reject incidental prose
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/retro_persistence_lib.py and publish_release_retro.py | action: fix | note: validate in the library and preserve omitted-goal direct callers
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/t_events_emit_lib.py and goal Agent Verification Plan | action: document | note: snapshot the full output and enabled event trees before mismatch tests
- F4 | bin: over-worry | evidence: strong | ref: goal Non-Goals and Boundaries | action: defer | note: no semantic lesson-quality gate, #496 bundle, or early remote proof
- F5 | bin: valid-but-defer | evidence: moderate | ref: caller inventory in Slice A | action: defer | note: broaden producer migration only if a real unprotected achieve caller exists

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_context=false.
- Host exposure state: requested_fields_sent
- Application state: host application not independently confirmed; no applied claim made.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct lenses ran read-only: ownership/API,
write-order/integrity, and skeptical counterweight. Boundary window
`retro-goal-design-critique-1` verified clean. The reviewers found that the
initial draft needed exact identity grammar, direct-library proof, complete
side-effect snapshots, and a conditional second-review rule; those repairs are
folded into the goal before activation. Repair-read reviewer Huygens
(`019fcb8d-f776-7201-9dee-ced39a8ebbab`) returned Pass with no blockers, and
boundary window `retro-goal-design-critique-repair-read-1` verified clean before
this record was updated.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-04-065640-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-04-065640-packet.json`
- Packet SHA256: `ad23548cf05f1c07f0bb4103640d91e8593bc22accb372307e20434e8cd1503a`
- Identity SHA256: `12fcd363d23a131c175eedf8506edea66c2734bceff7ad0f6da58338607f5704`

## Boundary Ownership

- Producer: `scripts/retro_persistence_lib.py` and its CLI transport.
- Consumer: achieve closeout evidence binding, lesson readers, and release
  callers that intentionally remain in session mode.
- Owning surface: the persistence library's optional goal-aware write boundary.
- Verdict: moved-to-owner

## Deliberately Not Doing

No semantic validator for the quality of a lesson, no forced goal identity for
ordinary session retros, no #496 implementation, and no remote issue close or
push before the final gated bundle.

## Next Move

The repaired-packet fresh-eye read passed. Leave the goal draft inert and let
the user activate it with its exact `/goal @...` command. Implementation starts
only after activation and Slice A's caller/consumer map.
