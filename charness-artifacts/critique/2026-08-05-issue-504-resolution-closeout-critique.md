# Issue 504 resolution closeout critique
Date: 2026-08-05

## Decision Under Review

Whether the already-landed goal-aware retro persistence repair is sufficient to
publish a #504 closeout, using a typed `local-only-by-contract` behavior
disposition for the unobservable live-agent invocation boundary.

The issue remains OPEN until its carrier, remote proof, and adapter readback
are completed. This critique decides the resolution boundary; it does not
pretend those later publication steps already happened.

## Diff Scope

The reviewed implementation is the shared retro persistence writer and CLI,
the achieve/retro caller contract, source/plugin mirrors, final achieve
consumer binding, and focused tests landed in `9768f95d` and `c655e9aa`.

## Capability at Stake

Issue #504's JTBD is that an achieve closeout must reject a wrong, missing, or
malformed owning-goal identity before the retro artifact or any derived
summary, lesson index, event, or output-directory write occurs, while ordinary
session and release retros remain goal-free.

## Failure Angles

- Problem framing: the repair satisfies the stated optional goal-aware writer
  contract; it must not be inflated into proof that every future live agent
  supplies `--goal-path`.
- Boundary ownership: the shared writer owns pre-write identity validation;
  achieve closeout remains a defense-in-depth consumer, and release/session
  persistence intentionally omits goal identity.
- Operator path: the documented achieve and retro contracts name the canonical
  `--goal-path` invocation, and the focused suite proves explicit matching,
  mismatch refusal, canonicalization, no-write behavior, and legacy mode.
- Closeout claims: the carrier must carry the typed local-only disposition,
  the distinct local behavior evidence, the critique binding, and the full bug
  ledger before any remote mutation.

## Counterweight Pass

The reviewers disagreed on whether the optional flag leaves a blocker. The
counterweight resolves that concern as valid but deferred: requiring a live
agent/prompt invocation roundtrip would expand this local write-boundary issue
into an unobservable host-integration guarantee. The carrier must state the
omission non-claim plainly, and must not call the behavior host-verified.

The surfaced CLI concern is also valid but deferred for this issue: expected
identity errors currently propagate as a nonzero Python failure rather than a
custom concise diagnostic, but the error is raised before any write and the
issue's acceptance boundary is write ordering and identity ownership. The
closeout must not claim process-level negative CLI coverage beyond the tests
actually run; CLI ergonomics can be a separate follow-up if it recurs.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/retro_persistence_lib.py:140-214; tests/quality_gates/test_retro_persistence.py:315-425 | action: document | note: Carry `local-only-by-contract` and the explicit host-agent omission non-claim in the #504 carrier.
- F2 | bin: act-before-ship | evidence: strong | ref: docs/prescribed-skill-closeout-contract.md; skills/public/issue/references/closeout-discipline.md | action: document | note: Publish a validated carrier with the bug ledger, bound critique, AI provenance, distinct Behavior disposition, and Close #504 keyword before remote mutation.
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/public/retro/scripts/persist_retro_artifact.py:58-73; tests/quality_gates/test_retro_persistence.py:347-425 | action: defer | note: Expected CLI validation failures could use a cleaner diagnostic and process-level negative test, but write safety and issue JTBD are proven without that new surface.
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/achieve/SKILL.md:114; charness-artifacts/issue/2026-08-04-issue-504-causal-review.md:34-40 | action: defer | note: Host-level proof that every live agent passes --goal-path is unavailable and remains an explicit non-claim, not a reason to force all session/release retros into goal mode.
- F5 | bin: over-worry | evidence: weak | ref: skills/public/release/scripts/publish_release_retro.py:160 | action: defer | note: Requiring universal goal identity would break the intentionally goal-free release/session sibling contract.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_context=false; adapter tier also declares fork_turns=none.
- Host exposure state: requested_fields_sent
- Application state: host application was not independently confirmed; no applied claim is made.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — four unnamed one-shot bounded reviewers ran distinct JTBD,
boundary-ownership, operator-contract, and counterweight lenses. The initial
spawn attempt returned the concrete host signal `agent thread limit reached`;
completed stale agents were closed, the required unnamed spawn was retried,
all four findings were received, and all four boundary verifications returned
`verdict: clean` with empty drift.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-05-issue-504-resolution-packet.md
- Packet path: charness-artifacts/critique/2026-08-05-issue-504-resolution-packet.json
- Packet SHA256: 35c7abd865f3330486731717ca4922669f082b687d1e21e1068ad984dae1ad5d
- Identity SHA256: 18fcab62141de992b51d0a650d51fd124c3ad4de27e68128eb2dd1fe40226aac

## Boundary Ownership

- Producer: `scripts/retro_persistence_lib.py` owns the goal-aware write
  boundary; the achieve/retro instruction contract supplies `--goal-path` for
  achieve closeout, while release/session callers intentionally omit it.
- Consumer: `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py`
  binds final evidence to the goal and rejects wrong-owner evidence as a
  defense-in-depth consumer.
- Owning surface: the shared retro persistence writer, with explicit caller
  mode and achieve final-consumer checks.
- Verdict: moved-to-owner.

## Pre-Merge Action

Create the #504 direct-commit closeout carrier only after rendering and
validating its exact shape. Include the causal review, this resolution critique,
the full bug ledger, the typed local-only behavior disposition, explicit
non-claims, and `Closes #504`; then push through the repository gate and read
the final GitHub state with `verify-closeout --expect-state CLOSED`.

## Defect Class Cross-Link

The recurring wrong-boundary lesson is recorded in
`charness-artifacts/retro/recent-lessons.md`: validate the semantic ownership
value at the write owner rather than relying on a transport shape or late
reader.

## Deliberately Not Doing

- No live-agent or installed-host invocation claim is made.
- No universal `--goal-path` requirement is added to session or release retros.
- No semantic lesson-quality gate, #496 work, release, PR, Cautilus run, or
  custom blocking CLI-error floor is added.
- No issue-close claim is made until the carrier and final adapter readback
  independently succeed.

## Next Move

Draft the closeout carrier from the live #504 read and this critique, run
`validate-closeout-draft`, publish through the approved direct-commit path, and
verify the issue's CLOSED state through the GitHub adapter. Render the separate
behavior disposition from the focused local test channel, not from the carrier
or tracker state.
