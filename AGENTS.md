# Charness

`charness` is Corca's Claude Code/Codex plugin for efficient, auditable
software work. Keep this file short: it routes to the document that owns the
question; it is not a second operating manual.

## Start here

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
  parallel shape. Inspect the live host tool surface first, then fan out through
  whichever available lane fits the work: a host spawn/subagent for short,
  interactive or judgment-bound work, or `charness task run` for a bounded
  Codex lane that benefits from a named branch, isolated worktree, explicit
  path scope, or a durable result. Neither channel is a fallback for the other,
  and neither may be declared absent from memory. The parent agent owns intent,
  design, integration, and final verification; keep work sequential only when
  it is dependent or tiny.
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
