# Early Close Report — 428-reviewer-boundary-enforcement-release

## Why early closeout was chosen

The goal closed at ~2.7h of a 6h timebox because the operator-requested
endpoint was fully reached and externally verified: the mutation-CI baseline
fix and the #428 two-rail enforcement shipped in v0.65.0 (pushed, tagged,
published with HTTP-200 distinct-channel readback, install refreshed), and
#428 is CLOSED with a verified per-acceptance-line carrier. The done-early
policy (`continue_next_improvement`) was evaluated and declined: the external
publish lane's approval was scoped to this bundle, so post-release
continuation would strand unpushed work or need a new approval, and both
high-value remaining items are structurally unsuited to this session — #430
requires a fresh session (typed agent definitions load at session start) and
#431 touches four gated public skill surfaces that deserve their own critique
and release train. The argparse-help debt stays pinned LAST/alone by handoff.

## What user decisions are needed

One queued decision: prove in a NEW session that the rail-2
`bounded-reviewer` envelope actually binds (attempt Bash/Edit/Write/Agent and
record the concrete denial or non-denial on #430). The installed plugin was
refreshed to 0.65.0, so sessions restart anyway. No other operator decision
blocks the next run; #429/#431/#432/#433 are ordinary backlog picks.

## Waste and retro

Bound retro: `charness-artifacts/retro/2026-07-10-428-reviewer-boundary-enforcement-release.md`.
Main waste: two failed publish attempts (~160s duplicate quality runs) from
the publish-helper/commit-msg-gate contract mismatch (#433); ~20 idle minutes
polling for background reviewer completion (host-owned signal,
accepted-risk); one probe round to discover the envelope did not bind
mid-session (#430). The structural lesson — ambient machine state must be
pinned, not inherited — produced the credentials fix, the identity-leak issue
(#432), and the sibling sweep recorded in the retro.
