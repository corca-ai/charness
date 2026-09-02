# Progressive operator path

> Status: current
> Source of truth: this page and the linked executable surfaces
> Last verified: 2026-09-02

This page describes the smallest useful operating path as familiarity grows.
It is guidance, not a certification ladder.

## Day 1

- Read [AGENTS.md](../AGENTS.md), then [docs/index.md](./index.md) and the
  owner page for the task.
- Run [`./scripts/run-quality.sh`](../scripts/run-quality.sh) when the core
  contract is relevant.
- Ask for implementation, debugging, setup, or quality work in ordinary
  language; use a direct skill name only when intent is already unambiguous.
- Use [worktree prepare](./worktree-prepare.md) when the change needs an
  isolated checkout.

## After several slices

- Keep current procedures in their owner docs and move dated evidence to
  `charness-artifacts/`.
- Run the canonical exporter once when `skills/public/` changes.
- Use `charness worktree doctor` or `audit` when isolated lanes accumulate or
  readiness becomes unclear.
- Use the optional [retro](../skills/public/retro/SKILL.md) lesson ledger when
  a recurring failure is worth carrying forward.

## For repo-level changes

- Let [quality](../skills/public/quality/SKILL.md) choose the broader gate when
  a contract, proof surface, release, security, or uncertain deletion warrants
  it.
- Let [release](../skills/public/release/SKILL.md) own export, version, and
  publication checks.
- Let [achieve](../skills/public/achieve/SKILL.md) own provider-backed goal
  progress; do not recreate a session hook or handoff file for pickup state.

The path is complete when the next action is visible from the current owner
page and no extra root policy is needed to explain it.
