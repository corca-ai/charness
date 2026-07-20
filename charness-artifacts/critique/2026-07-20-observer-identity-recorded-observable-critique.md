# Critique Review
Date: 2026-07-20

## Decision Under Review

The user-approved plan for strengthening post-publication proof with observer
identity, not only channel diversity (handoff Discuss item). What shipped
locally: every rung-2 distinct-channel verification record now carries an
additive `observer` field naming its identity and distinctness limits — the
default HTTP probe records `unauthenticated-http (credential-free; same
host/process as publisher)`, the adapter probe records the operator-configured
shell locus, same-proxy-flagged and skipped records name themselves — and the
release-artifact markdown section renders the observer line so the rung-2
human audit can read observer distinctness where it reads the channel. The
publication-boundary reference states observer identity is a recorded
observable and that a machine-distinct observer is a separate surface a local
record must not claim. The machine-distinct CI-side observer is deliberately
NOT claimed locally; it is tracked as a filed follow-up issue with an
acceptance sketch (a durable post-publication record whose observer identity
is machine-distinct from the publisher).

Scouting also established that the unauthenticated-channel half of the
original Discuss item already existed (the credential-free HTTP probe with
same-proxy flagging), so this slice added only what was genuinely missing:
recorded observer identity and the tracked machine-distinct follow-up.

## Failure Angles

- Honesty: could any observer string overclaim distinctness (adapter probes
  that might reach remote machines; the HTTP probe's shared host/process)?
- Consumer safety: the observer-record validator, the JSON probe artifact
  persistence, and any exact-shape assertions on verification records.
- Test quality: network-free coverage of the blocked/adapter/skipped branches
  and the same-proxy observer string; stub scoping.
- Portability/ergonomics: issue anchors and host references must stay out of
  the portable package surfaces.
- Doc/handoff honesty: consistency with the render-not-declare (F2a) and
  distinct-observer (P4) doctrine; the RESOLVED-locally qualifier.

## Counterweight Pass (four-bin triage)

- K1 | act-before-ship (fixed): the reviewer found the release-artifact
  markdown renderer emitted status/channel/url/command but not `observer`, so
  the identity was persisted in JSON yet invisible on the primary surface the
  rung-2 audit reads. Fixed with an `Observer identity:` render line plus a
  render test; mirrors re-synced.
- K2 | over-worry (confirmed, no change): the observer-record validator
  requires only channel+status, so the additive field passes through and
  persists into the probe JSON verbatim; no consumer asserts an exact dict
  shape on these records; the urlopen stub is fixture-scoped and leaves no
  network dependency.
- K4 | valid-but-defer (no action): the adapter-probe label describes the
  invocation locus (child shell of the publish run), so an operator-configured
  genuinely remote probe would be under-credited, not over-credited — the safe
  direction the doctrine wants; refining locus-vs-landing wording can wait for
  a real remote-probe consumer.
- K4 | valid-but-defer (tracked): machine-distinct observation itself is not
  achievable from the publisher's environment by definition; it is tracked as
  the filed CI-side follow-up issue rather than partially claimed here.

## Recurrence Verdict

Observer distinctness is now a recorded observable at the publication
boundary, mirroring the confirmation-object pattern the issue-closeout
verifier gained in the sibling slice: claims carry their observer, channel,
and limits instead of relying on a reader to infer them. The remaining gap
(machine-distinct observer) is typed, tracked, and explicitly non-claimed, so
it cannot silently pass as done.

## Boundary Ownership

- Verdict: owned-correctly

The release package owns its verification-record vocabulary and rendering; the
observer-record schema stayed with `release_observer.py` (untouched,
additive-tolerant by design); the CI-side observer belongs to a separate
surface and was routed to the issue tracker instead of being absorbed here.

## Reviewer Tier Evidence

<!-- allowed Host exposure state enums only -->
- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, typed `bounded-reviewer`
  (Read/Grep/Glob) with session-model inheritance per the repo per-host
  subagent contract; no Codex model requested on this host, so the omission is
  contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: the host spawned the typed `bounded-reviewer` agent by
  name; the read-only envelope bound and the rail-1 reviewer-boundary
  fingerprint verified clean (no index/worktree drift) after the reviewer
  returned, so approvals are valid and the reviewer ran on the parent's
  session-inherited model.

## Fresh-Eye Satisfaction

parent-delegated — one high-leverage bounded reviewer over the uncommitted
slice (five angles, in-report counterweight); the one should-fix (markdown
renderer omitting the observer) applied and re-tested before commit; rail-1
reviewer-boundary fingerprint verified clean.
