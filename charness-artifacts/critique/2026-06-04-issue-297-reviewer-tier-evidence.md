# Issue 297 Reviewer Tier Evidence Critique

## Execution

Fresh-eye code critique ran before the direct-commit closeout for issue #297.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`

## Packet Consumed

charness-artifacts/critique/2026-06-04-113737-packet.md

## Target

Code critique

## Diff Scope

Critique prepare packets now include adapter-resolved reviewer-tier evidence,
and critique artifact validation requires reviewer-tier evidence for
parent-delegated or packet-consuming critique artifacts.

## Change

Success means the artifact records requested tier and host exposure state
without claiming provider application unless the host confirms it.

## Angles

- Evidence honesty: the packet correctly records requested tier and
  `pending-parent-spawn`; actual review artifacts record `requested_fields_sent`
  rather than `applied`.

## Findings

- Act Before Ship: initial validator only checked reviewer-tier evidence when
  present. Folded fix: parent-delegated and packet-consuming critique artifacts
  now require the section.
- Bundle Anyway: `applied` originally accepted any application text containing
  `host-confirmed`. Folded fix: `applied` now requires
  `Application state: host-confirmed: <signal>`.
- Over-worry: provider-internal proof is outside this slice.
- Valid but defer: historical critique artifacts are not backfilled unless
  touched; future omission is the prevention target.

## Counterweight Triage

- Act Before Ship: none after required evidence enforcement.
- Bundle Anyway: none after stricter `applied` grammar.
- Over-Worry: no provider-internal application proof.
- Valid but Defer: no historical artifact migration.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py | action: fix | note: require reviewer-tier evidence for parent-delegated or packet-consuming critique artifacts
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/validate_critique_artifacts.py | action: fix | note: require host-confirmed application-state grammar before using `applied`
- F3 | bin: over-worry | evidence: moderate | ref: https://github.com/corca-ai/charness/issues/297 | action: document | note: provider-internal proof is out of scope

## Deliberately Not Doing

This slice does not prove provider internals, change host config, or require a
host to honor reviewer tiers. It records the request and the host-visible state.

## Next Move

Proceed with direct commit for #297 after public-skill dogfood review and
pre-lock closeout pass.
