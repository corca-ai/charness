# Binary Preflight

## Binary Preflight Philosophy

Public skills must not silently assume non-baseline binaries. If a Bootstrap
step calls a tool outside `CHARNESS_BASELINE` (`sh`, `git`, `python3`, `sed`,
`find`, `awk`, `grep`, and basic coreutils), declare it inline with
`# Required Tools: <name>` and point to `../../../shared/references/binary-preflight.md`.

Preflight is lazy, not eager: only trigger it when a command fails with exit 127
or emits `MISSING_BIN: <name>`. Explain the missing binary, propose the mapped
install command, and wait for explicit consent. Auto-install is forbidden.
Silent skip is forbidden.

Non-interactive callers use `CHARNESS_BINARY_PREFLIGHT=degraded`, which records
the degraded step in the durable artifact. Do not swallow `command not found`
with `2>/dev/null || true`; either let it fail or guard it with `command -v`.
If a support skill owns the binary, declare the support skill instead of the
binary and let `capability.json` stay the readiness source of truth.

When setup prerequisites matter, express them as manifest readiness checks
instead of burying them in operator prose only.
