Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**This issue survived a full reproduction.** The scaffold's verbatim output validates
clean in a ledger-less tree; the missing-line error names the whole key set together
with a copyable canonical line; and the planner reports the dated rules. All four of the
items this issue listed are met.

**One residual, disclosed rather than repaired.** A consuming repo still reads a literal
`<authoring-repo>` placeholder in the scaffold's North Star section. That is a real
consumer-facing defect and it is not fixed by this release.

Behavior #623: the scaffold was run and its output validated in a fresh, ledger-less
tree, and the error path was exercised to read what it names.

Critique #623: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
