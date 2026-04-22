# Startup Probes

Agent-facing or installable CLIs should expose at least one cheap read-only
startup probe. Good defaults:

- `tool version`
- `tool --version` when supported
- `tool --help`
- a lightweight read-only inspect command such as `tool doctor --json`

Keep startup semantics explicit in the adapter:

- `label`: stable runtime-signal and budget key
- `command`: argv array to execute
- `class`: `standing` or `release`
- `startup_mode`: `warm`, `cold`, or `first-launch`
- `surface`: `direct`, `install-like`, or another explicit launcher surface
- `samples`: how many times to measure this probe in one run

Use `startup_probes` to say what should be measured. Use `runtime_budgets` to
say which labels have a standing budget.

Recommended split:

- `standing`: cheap, repeatable probes that should run in the normal quality
  path
- `release`: launcher- or packaging-sensitive probes that belong in release
  proof rather than every local gate

Do not collapse all of these into one "doctor passed" claim. A passing health
command is not the same thing as a fast enough startup path.
