# Agent document policy

`setup` owns only the host-facing compatibility boundary:

- `AGENTS.md` is the canonical repository instruction file.
- `CLAUDE.md` may symlink to `AGENTS.md`; a real file is a merge decision.
- The normal reading path is `AGENTS.md` -> the consumer-owned `<repo-root>/docs/index.md` (not vendored with this skill) -> the owner page.
- Existing authored `AGENTS.md` content is preserved unless the user explicitly
  approves the compact replacement.

The generated greenfield file is intentionally small and points at the
consumer-owned `<repo-root>/docs/index.md` (not vendored with this skill). It may carry one short
parallel-routing cue for independent work, including the portable fast-tier
default and continuity of an explicit repository/user model choice. It does not
inject provider model ids, session hooks, handoff state, detailed subagent
delegation, standing root policies, commit-discipline prose, artifact
bookkeeping, or a skill catalog.
Those are owned by the workflow or adapter that actually needs them.

Use `normalize_host_docs.py --repo-root <repo>` for a plan and
`normalize_host_docs.py --repo-root <repo> --compact --execute` only after an
approved plan to replace an overgrown root file. The command never overwrites a
real `CLAUDE.md` or a symlinked `AGENTS.md`.
