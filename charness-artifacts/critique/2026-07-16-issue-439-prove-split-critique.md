# Critique Review
Date: 2026-07-16

## Decision Under Review

Issue #439 resolution (impl-first slice): split the public `impl` skill's
prove-and-close concept into a new public skill `prove` (slice verification +
closeout ledger owner; 130/200 lines), leaving `impl` the build loop
(140/200 lines) with a hard stop-gate pointer. Moves:
`references/verification-ladder.md`, `references/review-gate.md`,
`scripts/check_boundary_escalation.py`. Couplings updated across contract
pins, boundary tests, claim-fidelity specs/registry, validation/dogfood
registries, and the ownership allowlist.

## Failure Angles

- Stop-time and direct-prompt routing: prove never loaded at the stop gate, or
  colliding with `quality`/`hotl`/`critique` triggers.
- P2 dishonesty: load-bearing prose silently dropped or displaced instead of a
  genuine concept separation.
- Coupling incompleteness: stale anchors, dangling cross-references, registry
  gates unaware of the new public skill.
- Frozen impl consumer contract (reviewed dogfood case) silently broken.
- The eval specs mis-measuring after the reference move.

## Counterweight Pass

- Real pre-ship items (fixed in this closeout): the moved
  `verification-ladder.md` and `create-cli/references/quality-gates.md` still
  forwarded readers to "impl SKILL.md `## Closeout Vocabulary`", a section
  that moved to prove — the split's own two-way pointer was broken; the impl
  dogfood case's evidence trail still asserted impl owns the stop gate, so a
  dated move note was appended; the stale `debug/references/sibling-search.md`
  owner attribution was retargeted.
- Over-worry: routing collision (prove's intro explicitly disclaims
  quality/hotl/issue/release/critique and impl step 4 names only prove);
  P2 dishonesty (old steps 4–7, Output Shape, vocabulary, and the same-agent
  guardrail moved near-verbatim with only ownership labels changed); the
  cross-skill bootstrap dependency (files exist, allowlisted, fallback stated,
  single-plugin bundle ships both).
- Genuine but deferred: prove's dogfood case is `planned` (routing asserted,
  not yet demonstrated — promotion needs a real consumer run); the new
  prove-claim-fidelity spec has a form floor but no substance floor
  (outcome-assertions sibling); `charness-artifacts/skill-t-mechanism/`
  inventory drift is pre-existing (already missing achieve/hotl). Structural
  caveat worth remembering: prove inherited the growth-prone closeout
  machinery — the split bought headroom, not an end to accretion.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/prove/references/verification-ladder.md:82 | action: fix | note: token-home pointer said impl SKILL.md; retargeted to prove SKILL.md (both sites)
- F2 | bin: act-before-ship | evidence: moderate | ref: skills/public/create-cli/references/quality-gates.md:49 | action: fix | note: same dangling token-home pointer plus half-true ownership line; retargeted and split detection(impl)/closeout(prove) ownership
- F3 | bin: bundle-anyway | evidence: strong | ref: docs/public-skill-dogfood.json | action: fix | note: impl reviewed case evidence trail asserted impl owns stop gate/review-gate/verification-ladder; appended dated #439 move note
- F4 | bin: valid-but-defer | evidence: moderate | ref: evals/cautilus/prove-claim-fidelity/spec.json | action: defer | note: form floor only (RSF "Lint Gate"); substance floor (outcome assertions) deferred to the post-split follow-up
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/skill-t-mechanism/inventory.json | action: defer | note: pre-existing generated-inventory drift (missing achieve/hotl, lists find-skills); not a #439 regression
- F6 | bin: over-worry | evidence: strong | ref: skills/public/prove/SKILL.md | action: document | note: routing separation and P2 fidelity confirmed by both reviewers; 60/70-line headroom on impl/prove

## Reviewer Tier Evidence

- Requested tier: high-leverage (public-skill surface + issue-closeout review
  class).
- Requested spawn fields: repo standing request `gpt-5.6-terra` + `medium`
  effort is not exposed by this host's Agent tool (model enum is
  sonnet/opus/haiku/fable); spawned two typed `bounded-reviewer` agents
  (consumer-routing lens; coupling-completeness lens) with no model override.
- Host exposure state: host-defaulted
- Application state: both reviewers reported the read-only envelope bound
  (Read/Grep/Glob only), and the parent-side boundary fingerprint verify
  returned drift: [] after the reviews.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: `impl` (build loop, adapter file, verification survey) and `prove`
  (verification routing, closeout ledger, emittable vocabulary).
- Consumer: agents finishing impl/spec slices; validators substring-matching
  the emitted tokens; `create-cli`/`debug` references citing the ladder.
- Owning surface: the split itself is the ownership fix — one concept per
  skill surface, with prove's Non-Goals fencing quality/hotl/issue/release.
- Verdict: moved-to-owner
