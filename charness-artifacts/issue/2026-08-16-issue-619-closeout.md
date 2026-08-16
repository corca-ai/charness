Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**What shipped.** Both reported instances are repaired and `charness init` runs clean.

**This closes on the two repaired instances, NOT on the class.** The carrier scan that
prevents the recurrence covers markdown, `.agents/` configs and Python argv. Shell
scripts and workflow `run:` steps are unscanned, so a flag deletion can still break the
broad gate and CI with `check-documented-command-flags` green. That gap is named here
rather than left for a reader to discover, and it is the reason this close is not a
claim about the whole defect class.

Behavior #619: `charness init` was executed against this tree and completed without the
producer rejecting the flag its caller passes.

Critique #619: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
