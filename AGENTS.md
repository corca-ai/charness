# Charness

`charness` is Corca's Claude Code/Codex plugin for efficient, auditable
software work. Keep this file short: it routes to the document that owns the
question; it is not a second operating manual.

## Start here

- Read the lesson ledger before planning, not after failing:
  `python3 scripts/render_lesson_selection_preview.py --repo-root . --seed <id>`.
- Read [docs/index.md](./docs/index.md), then only the owner page the request
  needs. [docs/development.md](./docs/development.md) owns local work,
  [docs/operating-contract.md](./docs/operating-contract.md) irreversible
  boundaries, [charness-artifacts/](./charness-artifacts/) dated evidence.
- Independent investigation, implementation, and review are the default shape;
  the parent owns intent, integration, and final verification.
  [docs/parallel-execution.md](./docs/parallel-execution.md) owns channel
  choice and the live tool inventory rule.
- Read the active host adapter before choosing a carrier:
  [Codex](./.agents/codex-host.md), [Claude Code](./.agents/claude-host.md).

`CLAUDE.md` is a compatibility symlink to this file; changing either needs the
operator's explicit approval, and neither is a second source of truth.
