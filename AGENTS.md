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

## Documentation

Documentation is treated like code. Search and read the owning page before
you touch anything; update it after you touch anything.

- Reduce duplication, reveal intent, keep pages clear and simple. One page owns
  one question; link related pages like a wiki instead of restating them.
- [docs/index.md](./docs/index.md) is the entry point of all documentation.
  Keep this file minimal and route to `docs/`; put detail in the owning page.
- [README.md](./README.md) is the public user guide for people installing and
  using charness. `docs/index.md` links it; it duplicates no `docs/` page.
- Superseded decisions and dated evidence go to `charness-artifacts/`, not
  `docs/`. [docs/documentation-principles.md](./docs/documentation-principles.md)
  owns the authoring detail.

`CLAUDE.md` is a compatibility symlink to this file; changing either needs the
operator's explicit approval, and neither is a second source of truth.
