# Grok Build Host Notes

This file owns Charness-repository choices specific to a Grok Build
orchestrating session. The common operating contract stays in
[AGENTS.md](../AGENTS.md); Codex lane choices stay in
[codex-host.md](./codex-host.md); Claude-side notes stay in
[claude-host.md](./claude-host.md). Do not duplicate those here.

## Delegation and model policy

- Inspect the live tool inventory before selecting a channel. Hardcoding a
  host product name into a portable skill is not this file's job.
- Bounded, independent, reversible investigation or routine implementation
  uses the fast tier: pass `model` `grok-4.5` explicitly on
  `spawn_subagent`. Omitting `model` inherits the parent (`grok-4.6` in this
  runtime) and does not satisfy a fast-tier choice.
- Critical-path integration, architecture, ambiguous repair, and
  high-leverage review inherit the parent model, or pass `grok-4.6`
  explicitly.
- Independent writers use `spawn_subagent` with `isolation=worktree`. The
  parent integrates serially. `charness task run` is the Codex isolated
  lane; it is not this host's default carrier.
- Multi-agent fan-out that is a single bounded run may use the host
  `workflow` tool. Treat an idle or missing child report as unrun, not as a
  pass.
- The plugin-exported `charness:bounded-reviewer` type is available here.
  An absent review report is an unrun review. Do not budget a spawn as
  proof of a design or deletion boundary; verify the angle in the parent or
  say the review did not happen.
- Skill scripts run from this checkout. When the host reports an installed
  plugin path as the skill base directory, invoke
  `python3 skills/public/<skill>/scripts/<name>.py --repo-root .` from the
  working tree. The reason lives in
  [bootstrap-resolution.md](../skills/shared/references/bootstrap-resolution.md).

## Lane orchestration

Parallel channels, disjoint writers, proof floor, and integration order live in
[docs/parallel-execution.md](../docs/parallel-execution.md). Do not restate them
here.

Do not edit [AGENTS.md](../AGENTS.md) or its `CLAUDE.md` symlink from this
file's work; that change needs the operator's explicit approval.
