Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**This issue reproduces as fixed end to end.** A lesson can be seeded into a ledger in a
fresh repository with no hand-edit of the append-only ledger, and the seeder is mirrored
byte-identically into the export, so a consuming repo receives it rather than only the
authoring repo having it.

**Two residuals, disclosed rather than repaired.** Nothing re-prompts the seeder after a
cold start, and the seeder script's file mode differs from its sibling's. Both belong to this issue,
and this comment states them here because they were once recorded against a different
one.

Behavior #625: the seed path was executed end to end in a fresh repository, and the
export copy was compared against the source rather than assumed to be in sync.

Critique #625: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
