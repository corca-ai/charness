# Charness

Charness is a plugin for Claude Code and Codex that routes ordinary requests
through auditable development workflows. The [host packaging contract](./docs/host-packaging.md)
describes the supported host surfaces.

## Install

Make sure your machine has Python 3.10+, git, and curl; add `gh` when using the [issue skill](./skills/public/issue/SKILL.md).

Install the managed CLI and host plugin:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

The [bootstrap script](https://github.com/corca-ai/charness/blob/main/init.sh) creates or reuses the managed checkout at
`~/.agents/src/charness`, bootstraps its Python runtime, and runs `charness init`.
Init materializes the host plugin surface, registers the Codex
marketplace entry, installs the CLI, and creates the Claude wrapper/marketplace
surface when available; see [Repo-Root Install Surface](./docs/host-packaging.md#repo-root-install-surface).

Use `charness doctor` to inspect the local install. Run `charness uninstall` to
remove the managed install surface; add `--delete-checkout` to remove the
managed checkout and `--delete-cli` to remove the installed CLI. These paths
are owned by the `charness` CLI, documented in the [CLI reference](./docs/cli-reference.md).

The CLI is there so humans and agents can inspect local harness state instead
of guessing. Use `charness update all` when tracked external tools and bundled
support skills need refreshing.

## Use

The public workflows live under [`skills/public/`](./skills/public/). In Claude
Code invoke one directly as `/charness:<skill>`; elsewhere use an ordinary
prompt and let the workflow route it, as described in [workflow routes](./docs/workflow-routes.md).

The first prompt can be:

```text
Use charness to initialize this repo.
```

That prompt routes to [setup](./skills/public/setup/SKILL.md), which inspects the
repository's current operating surfaces, proposes the appropriate setup plan,
and requires approval before writing changes.
