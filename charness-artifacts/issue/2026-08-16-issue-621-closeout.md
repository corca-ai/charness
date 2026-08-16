Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**This issue survived a full reproduction and no repair was owed.** Rather than closing
it on the strength of an earlier comment, the reported path was re-executed from a bare
`git init` tree: `init_lesson_ledger.py` followed by `check_lesson_ledger.py` both exit
0, and the next step the bootstrap emits resolves the seeder against the READING tree
instead of a hardcoded `scripts/...` path, which is what made the loop unreachable from
a clean repo.

**No residual is claimed for this issue.** Two seeder residuals were once attributed
here in error. They are not this issue's, and asserting them would claim defects it does
not have.

Behavior #621: the bootstrap and its checker were run end to end in a fresh repository,
and the emitted next step was read for the path it resolves.

Critique #621: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
