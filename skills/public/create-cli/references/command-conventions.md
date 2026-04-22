# Command Conventions

Portable baseline for repo-owned multi-command CLIs:

- prefer a small set of stable subcommands over many top-level mode flags
- keep lifecycle verbs explicit: `init`, `doctor`, `update`, `reset`,
  `uninstall`, `version`
- treat `version` as the canonical version surface
- allow top-level `--version` as an ergonomic alias when the CLI already has a
  stable top-level parser
- reserve `-v` for `verbose`, never `version`
- support `-h` / `--help` as read-only help probes on the top level and stable
  public subcommands
- keep `--json` exclusively for machine-readable output
- prefer explicit long flags for destructive confirmations or irreversible
  behavior

When a CLI diverges from this baseline, make the reason product-shaped, not
stylistic. "The parser happened to allow it" is not a reason.

Read-only probe surface:

- `tool --help`
- `tool version`
- `tool --version` when supported
- `tool doctor --help`
- cheap command-discovery surfaces such as `tool commands --json`

Do not overload probe surfaces with mutations, background refresh, or install
side effects.
