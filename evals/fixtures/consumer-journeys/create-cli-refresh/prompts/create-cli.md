# Create-cli phase: migrate the existing cache scripts

Work in the consumer repository seeded beside this prompt. Read its
`AGENTS.md` and `README.md` first. Use the installed `create-cli` skill from
`CHARNESS_FIXTURE_PLUGIN_ROOT`; report the consumed skill path and package
version in your handoff. Resolve that skill's references from the exported
package root, never from host-installed Charness.

This is a build request, not a design-only request. Use the installed
`create-cli` skill to shape one coherent command contract and carry the work
through the installed `impl` skill because the user requested a build. Record
the concise, exact command contract in the consumer `README.md` so a fresh
implementation context can consume the same decisions without re-deriving
them. Use only the Python standard library and preserve the existing scripts.

The requested command surface is an executable repository-root `repoctl`:

```text
repoctl refresh SOURCE
repoctl doctor
repoctl version
```

Freeze and build these behaviors:

- `repoctl --help` and subcommand help are read-only and concise.
- `repoctl doctor` is a meaningful read-only readiness/status check; it must
  not create or rewrite `.state/cache.json`.
- `repoctl version` is a cheap read-only probe.
- `repoctl refresh SOURCE` parses SOURCE and, on success, writes exactly
  `.state/cache.json` with the existing refresh semantics. No second cache
  path or hidden state is allowed.
- `repoctl refresh --dry-run SOURCE` validates and reports what would happen
  without creating or changing any file.
- `--json` is an explicit machine-readable mode with stable structured output
  for the commands that report a result; default output remains concise human
  output.
- Unknown options, duplicate options, missing SOURCE or missing option values,
  and an option-looking SOURCE must be rejected before any write. Exercise
  representative inputs such as `--unknown`, repeated `--json`, no SOURCE,
  and `--looks-like-a-source.json`.
- The old invocation `python3 scripts/refresh_cache.py SOURCE` remains valid
  and writes the same `.state/cache.json` shape.

Carry the contract through implementation and tests, including help, doctor,
version, dry-run non-mutation, structured output, parser refusals, and legacy
compatibility. Update the README concisely; do not add a dependency, evaluator,
registry entry, or broad repository rewrite.
