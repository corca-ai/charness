# Slice 2 Premise Preflight Implementation Review

## Decision Under Review

Whether the Slice 2 premise-preflight library, thin source/plugin CLIs, and
focused fixture suite are safe to lock as the offline verdict surface for
captured issue/tree premise identity.

The reviewed surface is:

- `scripts/premise_preflight_lib.py`
- `scripts/check_premise_preflight.py`
- `plugins/charness/scripts/premise_preflight_lib.py`
- `plugins/charness/scripts/check_premise_preflight.py`
- `tests/quality_gates/test_premise_preflight.py`
- `charness-artifacts/spec/2026-08-06-premise-preflight-contract.md`

## Failure Angles

The review tested false acceptance and unstructured failure across:

1. issue-envelope type, timestamp, body/comment identity, and state handling;
2. current `HEAD`, protected index/worktree, expected-missing paths, and Git
   index descendants;
3. exact reachable shipped markers and semantic reason precedence;
4. malformed or incomplete JSONL history, duplicate/retry behavior, and
   append failures;
5. path safety, symlink handling, source/plugin parity, CLI exit/output shape,
   and focused regression adequacy.

## Counterweight Pass

The prior-round findings were real and were repaired before this review:

- staged exact expected-missing paths are observed in the index;
- boolean issue numbers and non-RFC3339 timestamps are rejected;
- decision history is fully validated rather than trusted by shallow fields;
- marker matching requires the exact full line reachable from current `HEAD`;
- captured protected symlinks are rejected;
- decision-log parent failures become structured errors;
- the contract now names the actual issue envelope and its outer-repository
  authority.

The second round found three additional proof-surface escapes. They were
repaired locally and covered by focused tests; the operating contract caps this
class at two review rounds, so these repairs are explicitly accepted-unreviewed
and no third bounded round is claimed.

## Structured Findings

### Round 1

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: expected-missing observations now include index/worktree presence and drift fixtures.
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: boolean issue numbers are explicitly rejected with regression coverage.
- F3 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: timestamps require exact UTC RFC3339 with a `Z` suffix.
- F4 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: decision history is fully validated before duplicate/retry classification.
- F5 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: shipped markers require exact full-line matching from reachable current HEAD.
- F6 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: captured Git symlinks are rejected as non-regular protected blobs.
- F7 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/spec/2026-08-06-premise-preflight-contract.md` | action: fix | note: outer repository is authoritative and outer/nested issue numbers must agree.
- F8 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: decision-log parent creation failures become structured errors.

### Round 2 — repairs accepted-unreviewed under the two-round cap

- F9 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: decision-log symlinks are rejected before history read and append.
- F10 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: NUL-safe index inventory detects descendants below expected-missing directories.
- F11 | bin: act-before-ship | evidence: strong | ref: `scripts/premise_preflight_lib.py` | action: fix | note: protected read failures are classified as structured partial repair.

## Reviewer Tier Evidence

### Implementation round 1

- Requested tier: high-leverage bounded reviewer
- Requested spawn fields: `fork_context=false, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- Host exposure state: requested_fields_sent
- Application state: no separate provider-application confirmation was exposed.
- Delivery state: findings-received — four unnamed reviewers returned findings.

Four unnamed parent-delegated bounded reviewers inspected the first
implementation packet: Hume, Parfit, Boyle, and Averroes (counterweight).
The boundary window was `slice2-impl-round1`; its fingerprint was verified
clean after each reviewer return.

- Packet: `charness-artifacts/critique/2026-08-06-031648-packet.json`
- Packet SHA-256: `a7012957af92e20b6ca8f338b6eb7505670b881efb71d799d4a15dcafe861b7c`
- Reviewed-input identity: `e4ae0ef988cc91e0e3bb182d76aaf57bbe7fa67a748854b64ac9e9fc2c0f3068`

### Implementation round 2

- Requested tier: high-leverage bounded reviewer
- Requested spawn fields: `fork_context=false, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- Host exposure state: requested_fields_sent
- Application state: no separate provider-application confirmation was exposed.
- Delivery state: findings-received — four unnamed reviewers returned findings.

Four unnamed parent-delegated bounded reviewers inspected the repaired
surface: McClintock, Mill, Volta, and Maxwell (counterweight). The boundary
window was `slice2-impl-round2`; its fingerprint was verified clean after each
reviewer return. All prior defects were confirmed repaired. F9–F11 were the
remaining blockers found by this round and were repaired after the round.

- Packet: `charness-artifacts/critique/2026-08-06-032554-packet.json`
- Packet SHA-256: `d2937d0a71daedeca41c2b81f087b70ca52c1d4edd3123e59a975d7b8df7eb13`
- Reviewed-input identity: `944a12cc4d8ac63a7f4c7718cd882a9236a95b0598de2aa70dcd8a0178669c6b`
- Post-repair focused proof: `22 passed`.

## Fresh-Eye Satisfaction

parent-delegated — four unnamed reviewers completed the required two rounds.
The second round read the repaired
surface, and its review boundary remained clean. F9–F11 are recorded as
accepted-unreviewed because the operating contract permits at most two rounds
for a verdict-logic slice; no same-agent or same-agent-context substitute was
used.

## Reviewed Input Identity

The final closeout packet below binds the current post-repair surface. The
round-2 packet in Reviewer Tier Evidence is the distinct identity of the
surface fresh eyes actually read; F9–F11 repairs after that round are
accepted-unreviewed and are not presented as having received a third approval.

- Packet path: `charness-artifacts/critique/2026-08-06-036300-final-closeout-packet.json`
- Packet SHA256: `01968b92378274ef8e263ced598e82e33847c49177ed06dfc66664d6ac56ae73`
- Packet Markdown SHA256: `2459811591823a0894a8f4c5ad70eb43061d1ecd4cfe6cd5915cc8f14ee811da`
- Identity SHA256: `e78dbad3019307beb9ec6eedf4356388f3f27853ba14507dd7e32f5b32651b22`

## Boundary Ownership

The library owns offline coherence and semantic reason classification. The
issue adapter owns provider reads. Git owns repository identity. The JSONL log
owns preflight decision history only. The CLI owns shell-free structured output
and exit codes. No provider write, runtime behavior, installed-consumer
behavior, or remote CI claim is attached to this review.

- Verdict: owned-correctly — the preflight owns only local coherence and
structured refusal semantics; provider, Git, issue, and later publish owners
retain their boundaries.

## Proof-Surface Review

This is a proof surface because it renders accepted/refused verdicts about a
captured premise. The repaired implementation now tests the source and
checked-in plugin copies, rejects regular-file/symlink and history hazards,
observes both index and worktree state, and preserves the documented reason
ordering. The 22-test focused suite includes positive acceptance, every
semantic refusal class, malformed input/history, retry/persistence, marker
reachability, symlink cases, staged descendant drift, structured append errors,
and both CLI paths.

Fresh-eye pass: scripts/check_premise_preflight.py — proof surface; the two
bounded implementation review rounds checked shell-free exit/output behavior,
including structural-error and semantic-refusal paths.

Fresh-eye pass: scripts/premise_preflight_lib.py — proof surface; the two
bounded implementation review rounds checked false acceptance, reason
precedence, history, path, index, worktree, and symlink escapes.

## Floor-Addition Restraint

No standing quality gate or closeout floor was added. This remains a
user-requested, manually invoked preflight capability; later publish/ledger
work owns any decision about making it a mandatory workflow boundary.

## Next Move

Sync the plugin mirror after any final edits, bind the final proof packet after
the Slice 2 goal log is updated, run the strongest available closeout checks,
and commit the slice without pushing.
