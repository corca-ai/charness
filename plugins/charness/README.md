<!--
generated_file: true
source_path: README.md
derived_path: plugins/charness/README.md
generator: python3 scripts/sync_root_plugin_manifests.py --repo-root .
sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .
-->

# Charness

`charness` is Corca's Claude Code/Codex plugin for efficient, auditable
software work. It turns repo instructions, skills, scripts, and checks into a
single progressive workflow.

## Quick start

Install the managed CLI and host plugin:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

Make sure your machine has Python 3.

Start a fresh Claude Code or Codex session in the target repository and ask:

```text
Use charness to initialize this repo.
```

Review setup's proposed diffs before committing them. For day-to-day use:

```bash
charness doctor
charness update
```

Use `charness update all` to refresh tracked external tools and bundled
support skills. Commands emit one YAML result; add `--detail` when diagnosis
needs the full receipt.

The CLI is there so humans and agents can inspect local harness state instead of guessing.

## Read next

- [Documentation index](https://github.com/corca-ai/charness/blob/main/docs/index.md) — the current owner map.
- [Workflow routes](https://github.com/corca-ai/charness/blob/main/docs/workflow-routes.md) — ask in ordinary product language.
- [Development](https://github.com/corca-ai/charness/blob/main/docs/development.md) — repo-local work and dogfood.
- [CLI reference](https://github.com/corca-ai/charness/blob/main/docs/cli-reference.md) — complete command surface.
- [Host packaging](https://github.com/corca-ai/charness/blob/main/docs/host-packaging.md) — install and export layout.

Public skills live under [`skills/public/`](./skills/); the index routes
intent to the appropriate one. `skills/public/` is canonical and plugin-host
surfaces are generated from it.
