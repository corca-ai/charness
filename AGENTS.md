# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://github.com/corca-ai).

## Start here

- Read [docs/design-north-star.md](./docs/design-north-star.md) when a decision
  changes a boundary: brief a capable judge and keep teeth only where a wrong
  answer can escape.
- Then read [docs/index.md](./docs/index.md) and only the owner page for the
  requested surface. Do not reconstruct state from a session hook, handoff file,
  or a full issue graph.
- For an active Goal Run, read the parent issue and the cursor-selected child.
  `Achieve` owns navigation, progress, and continuation.
- If support or integration availability is genuinely unclear, use the
  read-only `charness catalog list --repo-root <repo> --summary` inventory and
  report a nonzero result as a command failure.

## Make changes

- Preserve the parent worktree. Never reset, restore, stash, clean, or mass-delete
  it to make a task easier.
- Create implementation/proof worktrees from explicit base and target commits,
  on a temporary named branch, with an explicit path scope. Refuse detached or
  dirty checkouts before running work.
- Keep Python bytecode, pytest/ruff caches, coverage, temporary output, and
  generated runtime state outside the worktree. `.gitignore` is not isolation.
- Prefer deleting obsolete code, wrappers, gates, mirrors, and tests over adding
  another ceremony. Derive facts from their source of truth.
- Keep host-specific behavior in adapters, presets, and manifests.

## Verify and finish

- Run focused tests first. [`run-quality.sh`](./scripts/run-quality.sh) is the default small core
  lane; use `./scripts/run-quality.sh --full --read-only` only for broad,
  release, or review work.
- Changed-line proof, full-suite proof, fresh-eye review, and closeout ledgers
  are conditional. Require the narrow evidence that matches a verdict/proof
  surface, irreversible boundary, release, security, compatibility, or
  uncertain deletion. Do not turn a reversible implementation into a ceremony.
- After source changes that have a generated plugin export, batch edits and run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` once. The source
  under `skills/public/` is canonical; never hand-edit its mirror.
- Commit meaningful code, test, workflow, and durable-artifact changes after
  verification. Keep the commit scoped and report the evidence.
- Never claim an unavailable proof ran. If an independent observer is needed but
  unavailable, record that as a non-claim; a same-agent reread is not independent.

## External boundaries

- Issue writes go through the provider and read the exact target back. Closing
  an issue may record completed, not planned, or superseded; an external-repo
  confirmation that is outside the goal is not a reason to leave it open.
- Push, pull request creation, reopening, tagging, version changes, release
  publication, installation, and evaluator execution require an explicit
  phase-scoped request.

## Documentation map

- [docs/index.md](./docs/index.md): documentation entry point
- [docs/implementation-discipline.md](./docs/implementation-discipline.md):
  change, cache, and verification loop
- [docs/operating-contract.md](./docs/operating-contract.md): ownership and
  boundary rules
- [docs/host-packaging.md](./docs/host-packaging.md): install/export layout
- `charness-artifacts/`: dated evidence, retros, proposals, and active Goal Run
  records; these do not override current docs
