# Critique Review

Date: 2026-08-06

## Decision Under Review

Lock Slice 2 as a source-checkout-only premise preflight that consumes the
actual `issue_tool.py read` envelope plus a candidate issue/tree identity,
refuses stale/duplicate/already-shipped/partial-repair premises with stable
reason codes, and persists semantically valid decisions without becoming a
provider, issue-state, runtime, or prose-duplicate source of truth.

## Failure Angles

- Contract-shape failure: two implementers could choose different envelope,
  hash, timestamp, decision-record, or exit-code semantics.
- Diagnostic/boundary failure: an offline captured-readback comparison could be
  mistaken for live provider freshness, or a tree check could miss index-only,
  worktree-only, symlink, or expected-missing partial repair.
- Operational failure: duplicate history, malformed JSONL, or an unrelated
  reachable marker could silently allow or refuse the wrong premise.
- Counterweight failure: a useful narrow identity preflight could expand into a
  semantic issue deduplicator, provider caller, or standing closeout gate.

## Counterweight Pass

The reviewers agreed the narrow offline seam is justified by the recurring
premise/already-shipped planning trap recorded in
`charness-artifacts/retro/recent-lessons.md`. They rejected semantic prose
duplicate detection, implicit GitHub calls, issue writes, runtime claims,
concurrency/rotation machinery, and release/PR marker conventions as
over-worry or valid-but-defer. The smallest honest contract is an explicit
adapter-envelope coherence check plus declared Git identity comparisons and a
single-process JSONL decision record.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `skills/public/issue/scripts/issue_read.py` envelope and contract schema | action: fix | note: bind outer/inner repository and number, `ok`, `comments_read`, comment count, body, ordered comment projection, state, and `updatedAt`; classify malformed shape as `invalid_issue_readback`, not stale evidence.
- F2 | bin: act-before-ship | evidence: strong | ref: protected tree comparison | action: fix | note: define captured `HEAD`, HEAD blob hashes, index/worktree byte checks, expected-missing paths, symlink refusal, and `stale_tree` precedence over `partial_repair`.
- F3 | bin: act-before-ship | evidence: strong | ref: offline/provider boundary | action: fix | note: rename stale semantics as captured-readback coherence and state that provider freshness requires a separate fresh adapter read; no current-provider claim is emitted.
- F4 | bin: act-before-ship | evidence: strong | ref: duplicate and shipped identity lifecycle | action: fix | note: prior accepted decisions block the stable premise ID; prior refusals permit retry with a generated attempt ID; the exact marker is a full line searched only in commits reachable from current HEAD.
- F5 | bin: act-before-ship | evidence: strong | ref: malformed JSONL persistence | action: fix | note: invalid history returns `invalid_decision_history` and does not append; only structurally valid semantic outcomes append.
- F6 | bin: bundle-anyway | evidence: moderate | ref: decision record and CLI contract | action: fix | note: define version/kind, observed identities, ordered reason codes, non-claim, persistence path, and exit codes; bind goal/slice identifiers without parsing goal prose.
- F7 | bin: bundle-anyway | evidence: moderate | ref: fixture matrix | action: fix | note: include same-count/different-comment, comments-omitted, index-only/worktree-only, symlink, expected-missing, moved HEAD, malformed log, refused retry, reachable/unrelated marker, and closed live issue fixtures.
- F8 | bin: over-worry | evidence: weak | ref: adjacent semantic/workflow surfaces | action: defer | note: no universal prose duplicate detector, provider invocation, issue mutation, runtime proof, or standing gate belongs in this slice.
- F9 | bin: valid-but-defer | evidence: moderate | ref: later publish-ledger slice | action: defer | note: provider freshness attestation, release/PR carrier markers, multi-process log locking, and installed/provider roundtrip remain later work.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- Host exposure state: requested_fields_sent
- Application state: unverified — the host accepted the requested spawn shape but exposed no provider-application confirmation.
- Delivery state: findings-received — four reviewers (three named angle reviewers plus one separate counterweight).

## Fresh-Eye Satisfaction

parent-delegated — four unnamed bounded reviewers completed distinct Minto,
Jackson, Weinberg, and counterweight scopes. Boundary fingerprint window
`slice2-spec-round1` verified clean after each returned review; no worktree,
index, or HEAD drift was observed. No same-agent substitute was used.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-06-033900-contract-final-packet.json`
- Packet SHA256: `f568bc1adcd3d668cd5134f900c91d4954e2584ca3c1376b2ab42b83f00a61a5`
- Packet Markdown SHA256: `a2c70d76a571644c036eb37d2e068a1f8dad9bcb47b72833cd644778f257ad35`
- Identity SHA256: `4bc23535eb7c4fa6f9a328255621b9918cb2e15e4c4c4b9bf9c56d4b705e9b4f`
- Reviewed path: `charness-artifacts/spec/2026-08-06-premise-preflight-contract.md`

## Boundary Ownership

- Producer: `issue_tool.py read` produces provider-facing issue readbacks;
  Git produces commit/index/worktree identities; the candidate record supplies
  the intended protected scope.
- Consumer: `premise_preflight_lib.py` compares those records and emits the
  local decision; later bundle and publish-ledger slices consume the decision
  without replacing issue or GitHub ownership.
- Owning surface: the preflight owns only structured local coherence and
  refusal semantics; it does not own issue content, provider freshness, or
  behavior proof.
- Verdict: owned-correctly — after the contract repairs below.

## Repairs Applied Before Implementation

- Added exact candidate, issue-envelope, hash, protected-path, marker, and
  decision-record semantics.
- Reframed `stale_issue` as captured-readback mismatch and recorded the live
  provider freshness non-claim.
- Defined `stale_tree` precedence, index/worktree partial-repair checks,
  expected-missing and symlink behavior, exact marker reachability, stable
  reason ordering, retry lifecycle, malformed-log refusal, and CLI exits.
- Expanded the acceptance matrix to cover the reviewers' axis-varying cases.

## Floor-Addition Restraint

Floor-Addition Restraint: keep/advisory — this is a user-requested, manually
invoked implementation-time preflight capability, not a new standing
commit/closeout gate. Its refusal output is persisted for the later bundle and
ledger consumers; no existing quality floor is weakened or widened here.

## Next Move

Regenerate the critique packet against the repaired contract, then implement
the library/CLI and fixtures. The implementation proof must include a second
bounded round over the repaired validator surface if the code renders verdicts
about the candidate or decision artifacts.
