# Command Surface

Prefer one top-level executable with a small set of stable verbs.

Good defaults:

- `init` or `install` for first-time setup
- `doctor` for read-only inspection
- `update` for state refresh
- `reset` or `uninstall` when the CLI owns local host state

Design rules:

- use verbs that match operator intent, not implementation details
- keep one obvious primary path and demote proof-only paths explicitly
- when the CLI owns multiple domains, use a namespace such as
  `tool doctor` instead of flattening every concern into the top level
- make `--help` usable without reading docs first

Agent-facing rule:

- if an agent is expected to chain commands, provide `--json` and keep the
  payload stable enough to parse without scraping prose
