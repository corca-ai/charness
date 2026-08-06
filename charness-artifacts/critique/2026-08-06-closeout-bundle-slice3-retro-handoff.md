# Closeout Bundle Slice 3 Critique

Date: 2026-08-06

## Decision Under Review

Lock the retro-to-handoff wiring slice as a deterministic local contract:
explicit goal/retro/handoff inputs, goal identity matching, repository-contained
retro citation, exact recurrence-marker coverage, source/plugin parity, and
honest non-claims about prose quality, disposition meaning, and external state.

## Failure Angles

- Identity and path safety: a retro must bind to the explicit goal, and a
  handoff link must resolve inside the repository without lexical or symlink
  escape.
- Markdown interpretation: fenced examples, direct blockquotes, lazy
  blockquote continuations, and wrapped bullets must not create false evidence
  or hide authored obligations.
- Surface ownership: the root validator, checked-in plugin copy, contract,
  tests, and durable goal/retro records must agree without mutating the current
  handoff before closeout.

## Counterweight Pass

- Act Before Ship items were repaired: the command requires all three reviewed
  paths explicitly; citation and marker extraction use logical authored bullets;
  fences, direct blockquotes, and lazy blockquote continuations are masked;
  relative escapes are rejected before normalization; and plugin execution uses
  the plugin-local handoff path helper.
- Bundle Anyway: no prose equality or semantic disposition predicate was added;
  those remain human claims-review boundaries. The unchanged current handoff is
  intentionally not rewritten by this slice.
- Valid but Defer: aggregate first-error authoring diagnostics are filed as
  deferred decision D52; final handoff refresh, claims/disposition review, and
  verification lock remain later closeout boundaries.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: [validator](../../scripts/validate_retro_handoff_wiring.py) | action: fix | note: design review required explicit inputs, normalized paths, exact markers, fence handling, and a no-marker citation case; all are represented in the contract and tests.
- F2 | bin: bundle-anyway | evidence: strong | ref: [validator](../../scripts/validate_retro_handoff_wiring.py) | action: fix | note: repaired-surface review found plugin import failure, blockquote spoofing, and lexical escape laundering; local import, authored masking, and pre-normalization refusal repaired them.
- F3 | bin: bundle-anyway | evidence: strong | ref: [wiring tests](../../tests/quality_gates/test_retro_handoff_wiring.py) | action: fix | note: the required second review found wrapped markers and lazy blockquote continuations; logical bullets and stateful authored-line masking now cover both with regressions.
- F4 | bin: valid-but-defer | evidence: strong | ref: [deferred decision D52](../../docs/deferred-decisions.md#d52-aggregate-closeout-bundle-authoring-diagnostics) | action: defer | follow-up: D52 | note: aggregate dry-run authoring diagnostics would improve repair-set visibility but would change diagnostic ownership and is not needed for the current fail-closed boundary.
- F5 | bin: valid-but-defer | evidence: strong | ref: [execution contract](../spec/2026-08-06-closeout-bundle-execution-contract.md) | action: defer | follow-up: final closeout claims/disposition review | note: this validator proves token and path wiring only; it does not prove human disposition quality, fresh handoff writes, or external state.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium,
  service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden; the host returned findings but did not
  expose applied model metadata
- Delivery state: findings-received; design, repaired-surface, and required
  second proof-surface round findings received

## Fresh-Eye Satisfaction

parent-delegated; the design reviewer supplied semantic findings but no boundary fingerprint and
is not counted as a clean approval. The repaired-surface reviewer and the
required second proof-surface reviewer each had a clean shared-worktree
fingerprint. The second reviewer found two blockers; their repairs are
accepted-unreviewed under the repository's two-round cap. No same-agent pass is
substituted for the bounded reviewers.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff-packet.json
- Packet path: charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff-packet.json
- Packet SHA256: 2980e2854fcb1b0cf20315f159c722500125266a3f66bffde0f6feafeec340f3
- Identity SHA256: cf045b8b5e219dfb6e9d005e8a11ea7cc869e2658641353f1c71062338b9c8d2

## Boundary Ownership

- Producer: `prepare_packet.py` produces the packet and reviewed-input binding;
  `persist_retro_artifact.py` owns retro persistence and lesson-index refresh.
- Consumer: `validate_retro_handoff_wiring.py` consumes explicit goal, retro, and
  handoff paths for deterministic identity/citation/marker checks; the later
  claims review consumes its report as one input, not as a semantic verdict.
- Owning surface: the validator owns only the mechanical wiring predicate;
  goal/retro state owns improvement disposition; handoff ownership remains with
  the final closeout workflow.
- Verdict: owned-correctly for the local deterministic slice; final closeout
  remains unproven until its distinct claims review, verification lock, and
  handoff update run.
