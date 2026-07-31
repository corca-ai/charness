# Slice 4 — The handoff chunker resolved cited paths against the wrong base
Date: 2026-08-01

## Decision Under Review

Resolve a cited path against the directory of the artifact citing it, instead of stripping relative prefixes and testing the result against the repo root.

Two bounded read-only review rounds, each bracketed by
`reviewer_boundary_fingerprint.py` snapshot/verify. Round 2 read the REPAIRS,
which is where this repo's measured pattern says the class recurs.

## Failure Angles

- Does the repaired predicate hold at its edges, or does it carry the class it repairs?
- Who does a newly-blocking condition refuse that it should not?
- Does every consumer of the changed verdict still render and consume it correctly?
- Does the repair state a claim over a scope it did not establish?

## Counterweight Pass

Findings binned below. `act-before-ship` items were fixed inside the slice and
re-verified; `over-worry` items are recorded with why they were not folded rather
than silently dropped. Every blocker was reproduced by the parent with a command
before being accepted — no finding here rests on a reviewer's reading alone.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_paths.py:36 | action: fix | note: round 1: a directory token lost its trailing slash under the new resolution, so `integrations/tools` (handoff side) stopped intersecting `integrations/tools/` (issue side) in the merger's exact-string boundary-token intersection — a merge that fired before silently stopped firing, in the invocation the slice enables
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_paths.py:20 | action: fix | note: round 1: `.resolve()` follows symlinks and this repo checks in current pointers, so a cited `latest.md` was rewritten to its frozen dated target. Resolution is lexical now
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_paths.py:110 | action: fix | note: round 1: the cross-style fallback could launder a stale citation into a different existing file, and could pull an out-of-repo citation back inside. An explicitly relative token now resolves against the artifact dir only, with no existence check
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_paths.py:116 | action: fix | note: round 2 (read the repairs): the blocker's own repair re-created that divergence with the BASE diverging instead of the slash — a bare `conventions/x.md` became `docs/conventions/x.md` on the handoff side. Bare tokens take the root base only now
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_parser.py:315 | action: fix | note: round 2: an anchor-only link normalized to the artifact DIRECTORY, so the drafter rendered `In scope: docs` — a goal claiming a whole top-level directory from a link that cites nothing
- F6 | bin: bundle-anyway | evidence: moderate | ref: tests/test_handoff_chunker_parse.py:619 | action: fix | note: round 2: the rewritten escape test still shipped a claim it could not establish, and the directory-slash test never reached the branch it named
- F7 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/parse_handoff_entries.py:96 | action: document | note: the `.git` walk can latch onto an unrelated ancestor repo. Bounded: it only chooses between two candidate base strings and never drops an entry

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, where this repo's contract uses typed `bounded-reviewer` agents with session-model inheritance rather than the Codex model/effort request
- Host exposure state: host-defaulted
- Application state: host-defaulted — typed `bounded-reviewer` spawns accepted; the adapter's Codex fields were not sent
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each reviewer was handed an inline slice packet naming the changed files, the pre-slice baseline command, the intent, and the reproduction. -->

## Boundary Ownership

- Producer: the handoff artifact's own citations
- Consumer: the staleness check, the drafter's Boundaries rendering, and the merge proposer's boundary tokens
- Owning surface: the `handoff` public skill owns citation canonicalization.
- Verdict: owned-correctly
