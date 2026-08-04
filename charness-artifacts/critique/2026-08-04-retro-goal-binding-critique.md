# Retro Goal Binding Critique
Date: 2026-08-04

## Decision Under Review

Move achieve goal identity validation into the shared retro persistence write
boundary, expose it through optional `--goal-path`, preserve legacy session and
release callers, and synchronize the public skill/export surfaces.

## Diff Scope

The slice changes the persistence library and CLI, achieve closeout token
binding, retro/achieve instructions, source/plugin mirrors, and focused tests.
It does not add semantic lesson-quality judgment or combine #496.

## Failure Angles

- Jackson / problem framing: the initial design solved only late closeout
  evidence binding; the reviewers moved the contract to the actual write owner
  and required primary workflow instructions to invoke it.
- Weinberg / diagnostic ownership: the shared library is the producer of the
  first artifact and derived writes; achieve remains a final-consumer defense.
  The repair also aligned numeric-only goal binding with that consumer.
- Gawande / operational path: reviewers found and drove tests for relative paths
  from another CWD, absent/malformed identities, complete no-write trees,
  legacy mode, and adversarial Markdown fence/heading cases.
- Raskin / first reader: the main retro and achieve persistence instructions now
  state when to pass `--goal-path` and require one matching top-level `Goal:`;
  the persistence helper accepts a slug for compatibility but writes the
  canonical repo-relative path.

## Counterweight Pass

- Act Before Ship: exact metadata parsing, repo-root path resolution, workflow
  routing, numeric-goal consumer alignment, and the final fence grammar were
  strong findings and are repaired.
- Bundle Anyway: source/plugin parity, direct-library tests, CLI threading,
  and full-tree no-write snapshots are included in the slice proof.
- Over-Worry: a semantic validator for lesson correctness, broad dynamic
  Markdown semantics, and a universal requirement for session/release retros
  have no support in this issue and remain out of scope.
- Valid but Defer: richer retro schema parsing beyond the top-level preamble is
  a separate contract if a concrete consumer requires it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/retro_persistence_lib.py:60-116 | action: fix | note: validation belongs before every persistence side effect
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/retro/SKILL.md:104-107 | action: fix | note: goal closeout instructions must invoke the opt-in contract
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_retro_persistence.py:270-360 | action: fix | note: direct-library and CLI tests must vary identity, path, fence, and legacy axes
- F4 | bin: over-worry | evidence: weak | ref: charness-artifacts/issue/2026-08-04-retro-persistence-goal-binding.md | action: defer | note: semantic lesson validation and #496 remain separate
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/retro_persistence_lib.py:67-102 | action: defer | note: richer Markdown metadata parsing needs a concrete consumer before expansion

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: spawn calls accepted the requested fields; provider-applied model metadata was not independently exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three angle reviewers and one separate counterweight ran in
round 1; two repair-read reviewers ran in round 2; the round-2 verdict-logic
blocker permitted one final repair-read, which found no concrete blocker. A
separate current-record review then caught and repaired one stale pre-fix debug
statement; its replacement review found no concrete blocker. The final current
tree dogfood review found no concrete blocker after the chronology, non-preclaim,
quality-pointer, and wording repairs. A later pre-lock repair read found two
implementation blockers: Markdown-valid indented ATX headings could leave body
`Goal:` text in the preamble, and slug input was not canonicalized on output.
Those were repaired with all-width no-write coverage and canonical output; the
subsequent final repair-read found no blocker. Every review boundary fingerprint
verified clean before the parent wrote again. The first final-round spawn hit `agent thread limit
reached`; completed reviewers were closed and the unnamed spawn was retried
successfully.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/retro-goal-binding-final-causal-repair-read-packet.md`
- Packet path: `charness-artifacts/critique/retro-goal-binding-final-causal-repair-read-packet.json`
- Packet SHA256: `6d805a0e15495aab34c6dd4e60cdc7d086fb03e279ac55a301d52713d9be7df7`
- Identity SHA256: `851553af0dd37bbcd751521e6bf258e216fcb89b6ee668550e081a80b039eb21`

## Boundary Ownership

- Producer: `scripts/retro_persistence_lib.py` produces the artifact and derived
  persistence writes; the achieve closeout parser produces final evidence
  binding tokens.
- Consumer: artifact/summary/index/event readers and the achieve closeout
  evidence gate determine operator-visible success.
- Owning surface: shared retro persistence boundary, with achieve as the final
  consumer and source/plugin instructions as the transport contract.
- Verdict: moved-to-owner — the identity guard moved from late evidence-only
  validation to the shared write owner while final binding remains defense in
  depth.

## Pre-Merge Action

All Act Before Ship findings are repaired. The final repair-read also found no
concrete blocker after the heading-boundary and canonical-output repairs; the
remaining proof is the locked quality and closeout gate, not another same-agent
review.

## Defect Class Cross-Link

This slice carries the recurring wrong-boundary lesson in
`charness-artifacts/retro/recent-lessons.md`: validate the semantic value at
the owner, not a transport shape or a late reader.

## Deliberately Not Doing

No provider/live/release proof, no release or issue close, no semantic lesson
quality gate, and no #496 hollow-refill predicate work are claimed here.
