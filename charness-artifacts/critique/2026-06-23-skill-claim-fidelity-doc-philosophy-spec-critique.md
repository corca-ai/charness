# Critique Review
Date: 2026-06-23

Packet Consumed: charness-artifacts/critique/2026-06-22-222623-packet.md
Spec Path:
charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md

## Decision Under Review

Lock the Skill Claim-Fidelity and Doc-Philosophy methodology spec so
implementation can classify quality's 39 references, choose #397 remediation
from that classification, and begin a small fan-out without reopening reference
pruning.

## Failure Angles

- Minto structure reviewer found the back half too loose: success criteria lacked
  matching checks, probe answers lacked write-back locations, and deferred
  decisions lacked reopen triggers.
- Jackson/Weinberg reviewer found two framing hazards: #397 could close on a
  coverage count without proving the reference-consulting phase, and
  `gate-sufficient` wording risked reopening deletion/pruning.
- Gawande reviewer found operational gaps: the builder acceptance command was
  not runnable as written, remediation lacked an artifact check, and fan-out /
  signal-separation checks were underspecified.

## Counterweight Pass

Act before implementation: strengthen #397 closeout to runtime consultation,
make `gate-sufficient` eval-local, add probe write-backs, add deferred reopen
triggers, replace the builder ellipsis with a runnable command, and map every
success criterion to a concrete check.

Bundle anyway: distinguish minimum #397 repair evidence from the full
methodology pilot, and preserve critique packet/result fields.

Over-worry: do not require a Cautilus `accept` verdict as the only success
signal, and do not treat the 39-reference pilot as scope creep because the active
goal explicitly chose it.

Valid but defer: builder-side validation for `referenceEngagement` and a fully
reusable all-skills schema should wait for the quality pilot plus 1-2 fan-out
samples.

## Fixed/Probe/Defer Coherence Result

Initial result: fail with narrow fixes. Folded fixes: each probe now names its
write-back destination, each deferred decision names a reopen trigger, #397
closeout requires runtime consultation of `quality-lenses.md`, and
`gate-sufficient` is no longer a deletion-candidate label.

## Acceptance Check Coverage Result

Initial result: partial. Folded fixes: SC1 maps to all-39 classification with
rationales; SC2 maps to a runnable builder smoke command plus a string-list
assertion; SC3 maps to a recorded remediation decision before behavior edits;
SC4 maps to separated validation report fields; SC5 maps to fan-out notes with
`fits poorly:` disposition.

## Pre-Impl Action

Complete. The spec has been patched before the next implementation slice
consumes it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md | action: fix | note: success criteria needed concrete acceptance coverage
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md | action: fix | note: #397 closeout needed runtime consultation evidence, not coverage count alone
- F3 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md | action: fix | note: gate-sufficient deletion-candidate wording risked reopening pruning
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/agent-runtime/build-skill-execution-observation.mjs | action: fix | note: builder acceptance check needed a runnable command with session tree, spec, and output
- F5 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md | action: fix | note: probe write-backs and deferred reopen triggers were cheap coherence fixes
- F6 | bin: over-worry | evidence: moderate | ref: charness-artifacts/goals/2026-06-23-skill-claim-fidelity-doc-philosophy.md | action: document | note: full 39-reference pilot is aligned with the active goal scope
- F7 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md | action: defer | note: reusable all-skills engagement schema waits for quality plus fan-out samples

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: reasoning_effort=medium
- Host exposure state: requested_fields_sent
- Application state: spawn accepted; three angle reviewers and one counterweight
  reviewer completed; provider application of tier metadata not externally
  confirmed.

## Fresh-Eye Satisfaction

parent-delegated. The host exposed `multi_agent_v1.spawn_agent`; three bounded
angle reviewers and one separate counterweight reviewer completed read-only
review tasks.
