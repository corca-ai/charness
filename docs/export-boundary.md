# Export boundary

> Status: current
> Source of truth: this page and [packaging_lib.py](../scripts/plugin_export/packaging_lib.py)
> Last verified: 2026-09-04

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
python3 scripts/plugin_export/export_plugin.py --repo-root . --host claude --output-root /tmp/export-probe
export_root=/tmp/export-probe/plugins/charness
root_tools_count=$(find "$export_root" -maxdepth 1 -type d -name tools -print | wc -l)
test "$root_tools_count" -eq 0
find "$export_root" -path '*/tools/*' ! -path '*/integrations/tools/*' -print
```

The root `tools/` count must be zero. Moved-tool basenames live in `MOVED_TOOL_BASENAMES` in [export_tools_reference_lib.py](../tools/export_tools_reference_lib.py); do not recopy that inventory here. The path probe matches a directory named `tools` while excluding shipped data under `integrations/tools/`.
