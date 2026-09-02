# Export boundary

> Status: current
> Source of truth: this page and [packaging_lib.py](../scripts/packaging_lib.py)
> Last verified: 2026-09-02

The plugin export ships the documented bundle trees: [README.md](../README.md), public skills
as `skills/`, shared skills as `shared/`, support skills as `support/`, plus
the declared profiles, presets, integrations, Claude agents, root bootstrap
shims, and host manifests. The complete `scripts/` tree is also exported.

`tools/` is authoring-repository infrastructure. It is never exported and is
not a consumer-facing command surface. Run a tool gate from the repository
root with its module spelling:

```bash
python3 -m tools.<name> --repo-root .
```

Moved tools import shared repository modules using `from scripts.<name> import ...`.
The root `runtime_bootstrap` and `yaml_output` shims remain bare imports;
the module runner places the repository root first on `sys.path`. Moved files
must not mutate `sys.path` or add another shim pair under `tools/`.

To inspect the clean export boundary:

```bash
python3 scripts/export_plugin.py --repo-root . --host claude --output-root /tmp/export-probe
find /tmp/export-probe/plugins/charness -maxdepth 1 -type d -name tools -print
```

The final command must print nothing. This probes the root `tools/` tree;
shipped data under `integrations/tools/` is a separate tree.
