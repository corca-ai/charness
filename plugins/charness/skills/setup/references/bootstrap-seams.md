# Bootstrap Seams

Use this when setup detects an optional seam beyond the core README, AGENTS/CLAUDE,
and docs-index surfaces. Setup may seed a small adapter or pointer; runtime behavior
stays with its owning skill or command. Do not turn a convenient seed into a new
universal policy.

## Installable Surface Probe

When the repo ships an installable CLI, plugin, package, or agent-facing
integration, give the README or bootstrap doc one cheap, machine-readable probe.
Use `probe-surface.md` to distinguish binary healthcheck, command discovery, local
discoverability, and a real workflow. Do not call a healthcheck a workflow proof.

## Durable Retro Memory

When the repo explicitly wants durable retrospective memory, seed one adapter and
one digest:

- `<repo-root>/.agents/retro-adapter.yaml`
- `<repo-root>/charness-artifacts/retro/recent-lessons.md`

Use `seed_retro_memory.py`; later selection and updates belong to `retro`.

## Artifact Commit Policy

When a Charness workflow writes durable artifacts, treat meaningful
`charness-artifacts/` changes as repo state and commit targets. Current-pointer
helpers should no-op when canonical content has not changed.

## Announcement And Release Commit Bodies

When announcement or release-note workflows are actually used, meaningful behavior
commits should carry issue linkage, human-visible value, verification, and relevant
operator/apply notes. Keep release mechanics in `release`, not in setup.

## Skill Routing And Proof

When installed Charness skills are present, add a short discovery-first routing
block. Active Goal Runs point to the exact `/goal #<parent>` objective and provider
cursor; ordinary readers follow `AGENTS.md` -> `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> -> the owning page.

When the repo owns skills under `skills/public/` or `skills/support/`, the owning
quality/skill-validation workflow decides whether semantic changes need dogfood,
scenario, or other proof. Setup does not make review or changed-line proof a
universal requirement.

## Worktree And Hook Visibility

When the repo uses git worktrees plus a hook manager, seed
`<repo-root>/.agents/worktree-adapter.yaml` so the worktree command can reproduce readiness.
Keep runtime/cache paths outside the worktree where possible.

For Lefthook, use `hook-failure-visibility.md`: preserve raw output in a stable
stage-specific log and declare actionable failure text. Do not pipe a gate through
`tail` or `head`. Consumer hook configuration remains owned by the consumer.
