Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**What shipped.** The silent overwrite is PREVENTED across artifact families: a scaffold
now resolves its write path by subject identity rather than onto a record belonging to a
different subject.

**Detection is narrower than the issue asked for.** This issue asked for the
date-coherence check over every dated artifact. What shipped detects it in the quality
family only — a date-incoherent `debug` record still validates clean. Widening the
validator inside a release slice was DECLINED rather than forgotten, and this close is
scoped to what shipped: prevention repo-wide, detection for one family.

Behavior #620: an exit-0 validate of a date-incoherent `debug` record is what measured
the detection boundary, so the narrowing above is an executed finding rather than an
estimate.

Critique #620: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
