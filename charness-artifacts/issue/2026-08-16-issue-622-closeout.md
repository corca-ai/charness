Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**What shipped.** Probes no longer report `triggered: false` for runs that never
happened, so an unconfigured or errored probe is distinguishable from one that ran and
found nothing. The retro trigger text and its reference now name the undetermined state,
which is the half of this defect that had shipped repaired in one surface and unrepaired
in another.

**How this verdict was reached, stated exactly.** This issue has NO fresh reproduction
in the slice that closes it. Its verdict rests on two recorded findings plus the
repairs made to its surfaces: F3 and F4 of
`charness-artifacts/critique/2026-08-14-issue-618-628-closeout.md`, which record the
probe discarding loader `errors` so a refused adapter rendered `not-configured` with exit
0 and then a guard re-shipping that same class, and F10 of
`charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md`, which records the
`retro` skill text still telling a reader to act on `triggered: true` with no undetermined
branch. That is weaker than an executed reproduction, and it is recorded here rather than
presented as equivalent.

Behavior #622: not verified by fresh reproduction in this slice; carried on the two
recorded findings and the surface repairs named above.

Critique #622: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
