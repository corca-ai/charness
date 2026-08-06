# Slice 6 Publish-State Ledger Spec Critique

Date: 2026-08-06

## Decision Under Review

The Slice 6 contract adds an offline, repo-local publish-state ledger that
reconciles one captured manifest with source-owned JSON claim blocks in the
goal and handoff. The decision was whether the validator could establish a
bounded captured snapshot without copying provider facts, parsing prose, or
performing external writes.

Execution was parent-delegated bounded review: three independent failure-angle
reviews and one separate counterweight review ran read-only in the shared
worktree. The first fan-out hit the host signal `collab spawn failed: agent
thread limit reached`; the required reviewers were retried one at a time,
unnamed, and their findings were received. No same-agent substitute was used.
After the repairs, a refreshed final binding packet was prepared for the
repaired contract; the reviewers' findings below are not represented as a
claim that they re-read that refreshed packet.

## Failure Angles

- F1 — Source ownership: the initial contract treated goal/handoff values as
  ledger inputs without a machine-readable ownership boundary. Repair: the
  goal and handoff now own one exact marked JSON claim block each; the ledger
  stores only path, block ID, and digest locators, and the validator reads no
  arbitrary prose.
- F2 — Manifest-derived predicates: the initial CI/issue shape was too
  generic and risked duplicating provider facts in the ledger. Repair: the
  validator derives CI success, job completion/identity, and repository-wide
  zero-open-issue state from the existing manifest shape. Issue emptiness is
  explicitly a captured observation, not a causal SHA claim.
- F3 — Refusal semantics: the initial contract did not make first-failure
  order and field-addressed refusal stable. Repair: the spec now defines the
  refusal matrix with stable codes and fields for ledger, manifest, source,
  CI, and issue failures.
- F4 — Acceptance coverage: the initial acceptance checks did not prove
  source-block binding or human/JSON parity. Repair: deterministic one-factor
  fixtures cover stale SHA, pending/state drift, CI failure, open issues,
  digest drift, missing markers, and the two CLI renderings.
- F5 — Scope and defer boundary: reviewers checked whether the ledger was
  accidentally becoming a provider refresh, history database, plugin
  workflow, or prose parser. Repair: live refresh, automatic rewriting,
  multi-publish history, arbitrary prose parsing, and a public plugin consumer
  remain explicit non-goals.

## Counterweight Pass

- Act Before Ship: source-owned blocks, actual manifest predicates, no copied
  CI/issue fields, a deterministic refusal matrix, and criterion-to-check
  coverage were required before implementation.
- Bundle Anyway: the implementation must keep the producer/consumer split
  visible: manifest plus goal/handoff blocks produce facts, while the ledger
  validator consumes and reconciles them. Each refusal code is paired with a
  fixture and field assertion.
- Over-Worry: a generic claim framework, manifest normalization, plugin/public
  consumer work, and multi-publish history would add machinery without a
  recorded escape in this slice.
- Valid but Defer: provider refresh, external writes, automatic source
  rewriting, and history are deferred to separately authorized work.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md` | action: fix | note: source claims are bounded, source-owned, and digest-bound.
- F2 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md` | action: fix | note: CI and issue facts are derived from the captured manifest rather than duplicated in the ledger.
- F3 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md` | action: fix | note: refusal order, codes, and fields are explicit.
- F4 | bin: act-before-ship | evidence: strong | ref: `tests/quality_gates/test_publish_state_ledger.py` | action: fix | note: deterministic fixtures cover the repaired acceptance envelope.
- F5 | bin: valid-but-defer | evidence: strong | ref: `charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md` | action: defer | note: provider refresh, history, rewriting, and plugin consumer work are outside this captured-snapshot slice.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer.
- Requested spawn fields: model `gpt-5.6-terra`, medium reasoning, priority, unnamed
  one-shot reviewers, fork context disabled.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed that three angle reviewers and a separate
  counterweight returned full findings messages; provider-side application of
  model metadata is not independently exposed.
- Delivery state: `findings-received`.
- Parent boundary snapshots and verifies were clean for all four review
  windows; reviewers made no worktree or index changes.

## Fresh-Eye Satisfaction

`parent-delegated` — independent bounded reviewer contexts supplied three
failure-angle findings and a separate counterweight pass; the initial host
thread-limit failure was retried with the required unnamed shape.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-final-packet.json`
- Packet SHA256: `72d52b91769d59a459c30134f50bc407e613cacfd3ed6a2543cc4338f71617ff`
- Identity SHA256: `9411924a03ac586f14cd6efc9700fb096229be72adb49609bbbc484b738c85d2`
- Initial review packet path: `charness-artifacts/critique/2026-08-06-050405-packet.json`
- Initial review packet SHA256: `4f0ac9b48f956c16c6ca5788f3c1f778380ca8126b14cd0a078bc8224a618262`
- Initial review identity SHA256: `f2a07e9d43aea46bce4863b4d7953e68827fd14af1a9aa771665b3232becad32`
- The findings were folded into the revised contract before implementation;
  the refreshed packet binds the repaired current input without claiming a
  second reading by those initial reviewers.

## Boundary Ownership

- Producer: the checked-in manifest owns captured CI/issue facts; the goal and
  handoff own their marked source claim blocks.
- Consumer: the repo-local ledger validator and later operator consume the
  source locators and return the captured-snapshot verdict or a refusal.
- Owning surface: source-bound offline reconciliation.
- Verdict: `owned-correctly` after the repairs above.
- External providers remain state owners; this slice makes no freshness claim
  beyond the captured manifest.
