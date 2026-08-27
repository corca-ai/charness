# Optional bootstrap seams

Use this reference only when setup detects a seam beyond README, AGENTS, and
`docs/index.md` <!-- not vendored: consumer-repo path -->. A seam is opt-in or evidence-triggered; setup should not turn
it into a universal root policy.

## Installable surface probe

When the repository ships an installable CLI, plugin, package, or agent-facing integration,
give the README or bootstrap doc one cheap machine-readable probe. Keep binary
health, command discovery, local discoverability, and a real workflow distinct.
Use `probe-surface.md` for the details.

## Retro memory

When the repository explicitly wants durable retrospective pickup, seed one
adapter and one digest with `seed_retro_memory.py`. Later selection and updates
belong to `retro`; setup only reports that the optional seam exists.

## Worktrees and hooks

When a repository uses git worktrees plus a hook manager, seed
`<repo-root>/.agents/worktree-adapter.yaml` so the worktree command can reproduce
readiness. Keep runtime/cache paths outside worktrees where possible.

Preserve existing hook managers. Hook failure visibility and exact hook scope
belong to `quality` and the consumer's own hook configuration.

## Not setup-owned

Quality gates, release and communication mechanics, artifact commit policy,
skill routing, and independent review are owned by the workflow that executes
them. Do not copy those contracts into every consumer root file.
