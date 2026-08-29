# Charness

`charness` is Corca's Claude Code/Codex plugin for efficient, auditable
software work. Keep this file short: it routes to the document that owns the
question; it is not a second operating manual.

## Start here

- Before planning, not after failing, read the lesson ledger:
  `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed <session-id>`.
- Read [docs/index.md](./docs/index.md), then only the owner page needed for
  the current request.
- Read [docs/development.md](./docs/development.md) for local work and
  [docs/operating-contract.md](./docs/operating-contract.md) before an
  irreversible boundary.
- When support or integration availability is unclear, run
  `charness catalog list --repo-root <repo>` as read-only inventory.
- `CLAUDE.md` is a compatibility symlink to this file. Do not create a second
  source of truth.

## Make changes

- Preserve authored parent-worktree changes. Use a clean named worktree for
  isolated mutation, with runtime caches and temporary output outside it.
- Make independent investigation, implementation, and review the default
  parallel shape. Inspect the current runtime's live tool inventory, including
  any discoverable deferred tools, before selecting a host spawn/subagent or
  `charness task run`. Only explicit inventory absence, invocation rejection,
  or a host error proves a lane unavailable; otherwise report it as unverified,
  not absent. The parent owns intent, integration, and final verification;
  serialize only dependent or tiny work. The task model is fixed to Luna;
  repo-local effort and lane choices live in
  [Codex host notes](./.agents/codex-host.md), and Claude-session
  delegation/model policy lives in
  [Claude host notes](./.agents/claude-host.md).
- Keep `skills/public/` canonical; exports and generated surfaces are updated
  by their producer. Prefer deleting stale rules, wrappers, gates, mirrors,
  tests, and docs over adding another layer.
- Use focused checks for ordinary changes. The owning quality or release
  contract decides when broader proof is warranted.

## Repository map

- [Documentation index](./docs/index.md) — current docs and owner map.
- [Workflow routes](./docs/workflow-routes.md) — intent-to-skill entry points.
- [CLI reference](./docs/cli-reference.md) — generated command surface.
- [charness-artifacts/](./charness-artifacts/) — dated evidence, plans, and
  retrospective memory; it does not silently override current docs.
