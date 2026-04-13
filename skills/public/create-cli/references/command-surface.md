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
- stable public subcommands should support `--help` with exit `0` and no side
  effects unless the repo documents a strong exception
- if wrappers or agents may probe the command surface, prefer an explicit
  machine-readable registry such as `commands --json` or
  `capabilities --json` instead of scraping help text
- do not collapse these probe layers into one overloaded command:
  - help / command existence
  - machine-readable command discovery
  - binary/runtime health
  - repo/install/materialized-surface readiness

Agent-facing rule:

- if an agent is expected to chain commands, provide `--json` and keep the
  payload stable enough to parse without scraping prose
- if local plugin, skill, or materialized runtime files are part of the usable
  surface, expose that discoverability as its own readiness check instead of
  hiding it inside generic health
