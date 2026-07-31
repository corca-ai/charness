# Sweep S11 delegated review substantiation

Date: 2026-07-31

## Decision Under Review

Close triage-sweep row S11 by requiring an `executed` `## Delegated Review` status
to substantiate itself in `scripts/validate_quality_artifact.py`, instead of
certifying any section whose text contains the substring `executed`. The section
under repair is the one that discloses whether a different agent context read the
work, so a fail-open there is the harness certifying its own fresh-eye claim.

## Failure Angles

- **A floor that fails the repo's own corpus.** Any bar above how this repo
  already writes delegated review is the bar-moving shape; 110 checked-in quality
  artifacts are the measurement.
- **A bag of words wearing a floor's clothes.** S3's lesson was that a coarse
  counter-check is defeated by filler. A vocabulary list is the same shape.
- **The guard becoming the gate's own counterexample.** Authoring guidance
  planted in the template is text the validator then reads.
- **A false refusal on honest disclosure.** The section's job is to record scope
  limits; a rule that refuses "no reviewer saw the post-fix tree" teaches authors
  to delete the honest sentence.
- **Portability.** The validator ships to consuming repos; every marker is
  English while `language:` is a mandated adapter field.
- **A repair carrying the class it fixes.** Every arm here is a matcher edit;
  either direction of a tightening can widen or narrow the wrong thing.

## Counterweight Pass

- **Real blockers, fixed before shipping:** the fill guard's own text tripping
  the contradiction arm (a false refusal on the prescribed authoring path) and
  simultaneously satisfying the substantiation arm; the guard's `slow-gate` and
  `executed` words scoping every scaffolded artifact as a runtime review; the
  `no reviewer` arm refusing three phrasings that are checked-in text today; the
  same arm defeated by inserting one adjective; the evidence arm cleared by
  `` `n/a` ``; line-by-line comment stripping defeated by one line wrap.
- **Withdrawn rather than shipped:** the bare `\bno reviewers?\b` denial arm.
  Adjacency cannot separate a denied event from a negative result of one, and the
  measurement was three real sentences it would have refused.
- **Over-worry:** that narrowing the denial arm re-opens S11's stub. It does not
  — negation-aware substantiation catches `executed (no reviewer, no findings)`
  on the other arm.
- **Accepted and recorded, not closed:** the floor reads only the artifact, the
  same channel the author wrote. It raises the cost of a stub; it does not prove
  a reviewer ran.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/scaffold_quality_artifact.py | action: fix | note: the new fill guard contained the literal `no review ran`, so filling the template's own executed slot was refused — reproduced end to end through the scaffold before the repair
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: the same guard listed the whole substantiation vocabulary, so any scaffolded artifact cleared the floor on boilerplate; comments are now stripped before the section is read as author claims
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: the guard's `slow-gate` wording scoped every scaffolded artifact as a runtime review that must name three lens ids; the slow-gate scope now reads stripped text
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: `\bno reviewers?\b` refused "no reviewer identified a blocker", "no reviewer saw the post-fix tree", and "no reviewer-attributable worktree change" — all checked-in critique text; replaced with a verb-anchored, modifier-tolerant denial arm
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: the original denial arm was defeated by one adjective (`no bounded reviewer ran`); the modifier is now inside the pattern
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: S11's stub survived by naming markers it also negated; substantiation now blanks negated markers before the presence test
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: the language-neutral arm matched any backticked slash token, so `` `n/a` `` substantiated; it now requires a path shape (slash plus extension)
- F8 | bin: act-before-ship | evidence: strong | ref: scripts/validate_quality_artifact.py | action: fix | note: `re.DOTALL` was inert against a per-line strip, so a wrapped guard restored both round-1 defects; stripping now runs over the joined text
- F9 | bin: act-before-ship | evidence: moderate | ref: scripts/validate_quality_artifact.py | action: fix | note: stripping comments would have bought back a `not run` written inside one, and would have refused a `host signal:` written inside one; both now read raw text
- F10 | bin: act-before-ship | evidence: moderate | ref: tests/test_quality_delegated_review.py | action: fix | note: the language-neutral test cited a path containing `critique`, a substantiation marker, so it passed with the arm it tested deleted; fixture repathed
- F11 | bin: valid-but-defer | evidence: strong | ref: scripts/validate_quality_artifact.py | action: document | note: `declared_delegated_review_status` takes the earliest status token on the first status-bearing line, so `not_applicable for X; executed for Y` skips the floor; recorded in the sweep record rather than fixed, because the scaffold's own line carries all three tokens and an ambiguity refusal would refuse the template
- F12 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/standing-gate-verbosity.md | action: document | note: round 2 argued the rule's home is a narrowly-triggered on-demand reference while the rule is universal; the scaffold guard carries it at write time, and re-homing the contract is a skill-surface slice, not this one
- F13 | bin: over-worry | evidence: moderate | ref: scripts/validate_quality_artifact.py | action: defer | note: narrowing the denial arm does not re-open S11 — the negation-aware substantiation arm covers the stub shape

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only Claude Code subagent).
- Requested spawn fields: subagent_type bounded-reviewer, session-model inheritance, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: all four reviewers reported seeing only Read/Grep/Glob and no Bash/Edit/Write/Agent tool.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

Two rounds, two reviewers each. Round 1 produced F1 and F2 — a blocker the first
cut shipped in its own guidance text, found independently by both reviewers.
Round 2 read the repairs and produced F3 through F10, including two false
refusals against checked-in artifact text (F4) and a test that could not fail
(F10). Round-2 repairs are accepted-unreviewed under the two-round cap.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with `- Packet consumed: <packet-path>` plus three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. That `Packet consumed:` line is what turns the binding floor on. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: `scripts/validate_quality_artifact.py` decides whether a quality
  artifact's delegated-review disclosure is admissible.
- Consumer: every `quality` closeout in this repo and in any repo vendoring the
  plugin export.
- Owning surface: the quality artifact validator, with its authoring contract in
  the scaffold's fill guard and `references/standing-gate-verbosity.md`.
- Verdict: owned-correctly

## Non-Claims

- **The floor does not prove a reviewer ran.** It proves the section names an
  unnegated English review word, or cites a path-shaped token whose existence is
  never checked. `executed — foundational sweep` passes on `found` inside
  `foundational`.
- **It reads the same channel the author wrote.** No independent observer is
  consulted: not the reviewer's returned text, not
  `reviewer_boundary_fingerprint.py` output, not any checked-in critique record.
  Wiring one of those in is the next slice, not this one.
- **Its incentive gradient is uncomfortable:** the denial arm can only fire on an
  author honest enough to write that nothing ran. A vague stub clears both arms.
- Measurement scope: 71 declared-`executed` sections across
  `charness-artifacts/quality/**` pass, which proves the floor broke no existing
  artifact — not that those 71 reviews happened. No consuming repo was exercised.
- The non-English path was probed with one constructed Korean section, not with a
  real non-English consumer artifact.
- The sibling `slow_gate_scope` branch still keys on the bare substring
  `executed`; left unnarrowed so this slice could not weaken an existing rule.
- Boundary fingerprints were snapshotted before each round and `verify` returned
  `ok: true` with every drift parent-attributed; all four reviewers were
  read-only by their own report.
- **Inherited, not caused, not fixed:** `check_dup_ratchet.py` hard-blocks on
  three duplicate families at HEAD `cddb0c42`, none of whose members this slice
  touched. Reproduced in a clean worktree at HEAD before the slice was staged.
