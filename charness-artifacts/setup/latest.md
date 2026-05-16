# Setup Review
Date: 2026-05-16

## Scope
Normalize the mature Charness operating surface after the operator requested
`setup` plus full quality.

## Result
- Repo mode: `NORMALIZE`.
- Core surfaces present: `README.md`, `AGENTS.md`, `CLAUDE.md` symlink to
  `AGENTS.md`, `docs/operator-acceptance.md`, and `docs/handoff.md`.
- `docs/roadmap.md` remains adapter-acknowledged missing.
- Added compact `## Skill Routing` block to `AGENTS.md`.

## Proof
- `python3 skills/public/setup/scripts/inspect_repo.py --repo-root .` reports
  `recommended_action: leave_as_is`.
- `skill_routing.has_skill_routing: true`.
- `skill_routing.matches_compact_block: true`.

## Deferred
- No new roadmap scaffold; adapter policy already acknowledges the missing
  roadmap surface.
- No worktree adapter seed; setup inspection found no hook-manager evidence
  requiring it.

## Next Move
Continue with the gather acquisition repair contract before further acquisition
implementation.
