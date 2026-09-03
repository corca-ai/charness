# Charness

Charness is a plugin for Claude Code and Codex that routes ordinary requests
through auditable development workflows. It exists to reduce rework in the
repositories that consume it, and to make agentic development there fast.

It is deliberately opinionated. Every skill, gate, and document in it is shaped
by one governing idea — brief a capable judge, and keep teeth only where a wrong
answer escapes — written down in the
[design north star](./docs/design-north-star.md). If that taste matches yours,
Charness will feel like leverage; if it does not, it will feel like friction.
Read the north star first and decide.

It is battle-tested daily on Claude Code and Codex, and it is always under
development. Breaking changes can land at any time.

## Install

Make sure your machine has Python 3.10+ with the stdlib `venv` module, git, and
curl; add `gh` when using the [issue skill](./skills/public/issue/SKILL.md).

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

The [bootstrap script](https://github.com/corca-ai/charness/blob/main/init.sh)
creates or reuses a managed checkout at `~/.agents/src/charness`, bootstraps its
Python runtime, and runs `charness init`. That is what changes on your machine:

- the managed checkout at `~/.agents/src/charness`, with the Python
  environment it bootstraps under its ignored `.charness/` directory
- the `charness` CLI and an optional `claude-charness` wrapper at `~/.local/bin`
  (init does not edit your PATH)
- the exported plugin under `~/.codex/plugins/charness` and the personal
  marketplace at `~/.agents/plugins/marketplace.json`; when the Codex CLI is
  present, Codex itself records the plugin cache and enabled entry under
  `~/.codex/`
- Claude marketplace and plugin registration under `~/.claude/plugins` when
  Claude Code is installed, and a Grok Build copy at `~/.grok/plugins/charness`
- install, host, and version state under `~/.local/state/charness/`

Details are in [host packaging](./docs/host-packaging.md), under
[Repo-Root Install Surface](./docs/host-packaging.md#repo-root-install-surface).

Your own repositories are only modified when you ask a skill to modify them.

Hosts load the plugin at startup, so after `charness init` or `charness update`,
restart Claude Code or start a new Codex session before your first prompt. The
CLI prints the same instruction when it finishes.

`charness update` fast-forwards the managed checkout and reinstalls the
surfaces; `charness update all` also runs `charness tool update` for every
tracked external integration. `charness doctor` inspects the local install.
`charness uninstall` removes the install surface, with `--delete-checkout` and
`--delete-cli` for the checkout and the CLI.

The CLI is there so humans and agents can inspect local harness state instead of
guessing. `charness --help` lists the surface; the
[CLI Reference](./docs/cli-reference.md) documents every command.

## Use

Public workflows live under [`skills/public/`](./skills/public/). In Claude Code
invoke one as `/charness:<skill>`; elsewhere describe the work in an ordinary
prompt and let it route, as in [workflow routes](./docs/workflow-routes.md).

**First time in a repository.** Run [`setup`](./skills/public/setup/SKILL.md).
It inspects the repository's current operating surfaces and proposes the
adapters, linters, and operating documents that fit it, then asks for approval
before writing anything.

**A long objective.** Run [`achieve`](./skills/public/achieve/SKILL.md). It
interviews you until the decisions that could change the goal, its boundaries,
or its execution order are settled, then freezes the plan and binds it to a
provider-backed Goal Run. Activate it in a fresh session with `/goal #<number>`.
From there the run pulls in whatever other skills each slice needs — you do not
have to name them.

**Fast throughput.** `charness task` hands bounded slices to a cheaper model in
isolated worktrees, so a high-capability orchestrator can keep many of them in
flight at once. Recommended on a machine with resources to spare, and only with
a strong model as the main agent. If you find yourself repeatedly reintegrating
or redoing parallel work, that is the signal to steer: sharpen each task's
boundary before dispatching it, not after.
See [agent task runs](./docs/agent-task-runs.md).

**Quality.** Run [`quality`](./skills/public/quality/SKILL.md) to get the
repository's current health read back with concrete moves, then execute the ones
it proposes.

## What it is

- **Optimized for long workflows.** The interesting unit is a multi-session
  objective, not a single prompt.
- **Adapted, not adopted.** Adapters bend the workflows to your repository and
  your taste instead of asking you to accept the defaults.
- **Documentation treated as code**, with an obsession for progressive
  disclosure — [AGENTS.md](./AGENTS.md) is the worked example.
- **A public/support skill split**, so workflow names stay few and tool-specific
  knowledge stays underneath them.
- **A retro loop with lesson promotion and retirement**, so what a session
  learned reaches the next one and what stopped earning its place leaves.
- **An obsession with code quality**, including deleting what no longer pays for
  itself.
