# Critique Review
Date: 2026-07-17

## Decision Under Review

Issue #442 resolution (four slices on main: `d312aa6b`, `9faef3b9`,
`cc71dbb1`, `c07a575c`, plus the closing commit): cap-headroom dedups for the
three cap-pinned public skills — spec 194→185 (contract-finalization stop
routed through the sibling `prove` stop gate, verdict enum single-homed in
`prove`, bootstrap merge, worktree-readiness fold), critique 194→188 (spawn
enforcement cited to the shared fresh-eye reference), announcement 194→182
(bootstrap listings merged, delivery mechanics cited to
`references/delivery-seams.md`) — plus prove hardening: the claim-fidelity
substance floor `evals/cautilus/prove-claim-fidelity/outcome-assertions.json`
and the dogfood repo-shape classification, with the planned→reviewed
promotion honestly blocked on a concrete host signal.

## Failure Angles

- P2 honesty: shave-or-displace risk — did any dedup silently drop
  load-bearing behavior or displace core prose to duck the cap?
- Coupling completeness: stale anchors, mirror drift, consumers that no
  longer resolve the moved contracts, eval wiring.
- Substance-floor quality: does the new assertion set actually catch a
  hollow token-echo run, without overfitting or penalizing honest runs?

## Counterweight Pass

- K1 | bundle-anyway (fixed): the assertion set's `_comment` overclaimed —
  on the deterministic-only path (no `--judge-cmd`) the grader excludes
  skipped judge rows from the denominator, so a hollow run reads pass_rate
  1.0 (scored 1/1, skipped 4). The comment now states the substance verdict
  requires the live judge; a deterministic transcript marker substitute was
  rejected as echo-gameable.
- K3 | bundle-anyway (fixed): the prove-promotion blocker lived only in a
  commit message; the handoff refresh now carries it explicitly as the first
  post-restart action.
- K2 | over-worry: no "could not run" carve-out on `executed-verification` —
  the fixture hands a runnable pure-Python subject; a carve-out would reopen
  the narrated-confidence escape the assertion exists to close.
- K4 | over-worry: critique's 12-line headroom plus the recorded
  remaining-weight-is-pinned-contract diagnosis is the honest disposition;
  demanding a larger number is scope creep against real contract weight.
- P2 open item closed by the parent: the merged spec bootstrap rg pattern was
  verified token-by-token as the exact union of the two removed groups.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: evals/cautilus/prove-claim-fidelity/outcome-assertions.json | action: fix | note: `_comment` now names the deterministic-only pass_rate-1.0 collapse and requires the live judge for the substance verdict
- F2 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md | action: fix | note: prove-promotion blocker recorded on the first-read pickup surface, not only in a commit message
- F3 | bin: over-worry | evidence: strong | ref: evals/cautilus/prove-claim-fidelity/outcome-assertions.json | action: document | note: executed-verification carve-out and deterministic transcript marker both rejected — each would reopen the hollow-run escape
- F4 | bin: over-worry | evidence: strong | ref: skills/public/critique/SKILL.md | action: document | note: remaining weight is pinned contract (six contract pins + forbidden snippets); 188/200 with diagnosis is the honest disposition
- F5 | bin: valid-but-defer | evidence: strong | ref: docs/public-skill-dogfood.json | action: defer | note: prove dogfood promotion + review_required_skills addition deferred to the first post-update session (host signal: `Unknown skill: charness:prove`)

## Deliberately Not Doing

- No second skill split: every diagnosis found honest within-skill dedup
  sufficient; a new public skill surface stays an operator decision if a
  future diagnosis demands one.
- No deterministic transcript-substance check in the prove assertion set
  (echo-gameable; substance stays judge-kind by design).
- No `review_required_skills` addition for prove while its case is `planned`
  (the validator correctly requires `reviewed` status first).

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout review class).
- Requested spawn fields: adapter `reviewer_tiers.high-leverage` —
  `gpt-5.6-terra`, `medium` reasoning effort, `fork_turns: none`, priority
  tier — not exposed by this host's Agent tool (model enum is
  sonnet/opus/haiku/fable); three typed `bounded-reviewer` angle agents
  (P2 honesty; coupling completeness; substance floor) plus one counterweight
  spawned with no model override.
- Host exposure state: host-defaulted
- Application state: read-only envelope asserted by agent type
  (Read/Grep/Glob); parent-side boundary fingerprint verify returned
  `drift: []` after the angle pass and after the counterweight pass.

## Packet Consumed

n/a (fix-unit diff inlined per angle; the prepare-packet run for this session
is charness-artifacts/critique/2026-07-16-220649-packet.md)

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: spec/critique/announcement SKILL.md surfaces (the deduped
  pointers); prove, the shared fresh-eye reference, and delivery-seams.md
  (the receiving canonical owners).
- Consumer: agents running the three skills; validators and tests
  substring-matching the moved tokens; the A/B grading harness consuming the
  new assertion set.
- Verdict: moved-to-owner (coupling angle: verdict enum + slice ledger →
  `prove`, spawn enforcement → shared fresh-eye reference, delivery
  mechanics → `delivery-seams.md`; every consumer was verified to reach the
  new owner — rewired AC9 test, resolvable `../prove/SKILL.md` link,
  glob/sibling auto-discovery for the eval set).
