# Agent Docs Policy

`setup` owns only the compatibility and routing boundary for host-facing docs:

- `AGENTS.md` is the canonical repository instruction file.
- `CLAUDE.md` may symlink to `AGENTS.md` when Claude compatibility is needed.
- A real, authored `CLAUDE.md` is a merge decision; never overwrite it silently.
- An existing `AGENTS.md` is preserved. Setup does not rewrite it to match a
  generated template.

For a new repo, the generated file contains a short `Skill Routing` block and,
when Charness goal routing is present, the compact `Commit Discipline` block.
Those are navigation and state-integrity aids, not a complete operating handbook.

Independent review, subagent selection, and host-specific spawn settings belong to
the skill or adapter that actually requests the review. Setup does not inject a
standing `Subagent Delegation` policy, inspect a critique adapter merely because
the word “review” appears, or create a recommendation queue for that policy.
When a material boundary needs a second observer, the owning skill records that
decision and its non-claim locally. A host that cannot provide the observer is an
explicit non-claim, not a reason to make every consumer carry extra root prose.

The normal reading path is `AGENTS.md` -> `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> -> the page that owns the
question. Active Goal Runs use their provider parent and cursor as live state;
there is no required session-start hook or standalone handoff file.

Use `normalize_host_docs.py --repo-root <repo> --execute` for the deterministic
create-or-symlink cases:

- no `AGENTS.md` and no `CLAUDE.md`: create `AGENTS.md` and `CLAUDE.md -> AGENTS.md`;
- existing `AGENTS.md` with no `CLAUDE.md`: create the symlink;
- existing correct symlink: leave it alone;
- real `CLAUDE.md`: report the merge decision and stop.

Keep detailed quality, release, review, and operator-acceptance contracts in their
own skills. Do not duplicate them in every consumer's root instruction file.
