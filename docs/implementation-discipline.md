# Implementation Discipline

> Status: current
> Source of truth: this page and the executable commands it names
> Last verified: 2026-09-02

This page answers one question: how do we make a change, learn whether it
worked, and leave the next change easy to start? It is intentionally short.

## Default loop

1. Read [AGENTS.md](../AGENTS.md), [docs/index.md](./index.md), and the owner page for the surface being
   changed. For an active Goal Run, read the parent issue and the one child
   selected by its cursor; read the full graph only for explicit sync or parent
   close.
2. Inspect the exact target and current diff. Keep the parent worktree intact.
   Implementation and proof worktrees must be clean at creation and use a
   separate named branch. Runtime caches and temporary output live outside the
   worktree.
3. Make the smallest change that improves the user's path. Removing obsolete
   code, wrappers, gates, mirrors, docs, or tests is a valid implementation
   when their consumers have been checked. Do not add a rule to compensate for
   a problem that deletion or derivation removes.
4. Run focused tests for the changed behavior, commit the slice, run the
   changed-line proof over `base..HEAD`, and only then the default core lane
   when the changed surface has cross-module consumers; the order and its cost
   are owned by [parallel execution](./parallel-execution.md#disjoint-writers).
   `./scripts/run-quality.sh --release` is the release-final changed-line
   coverage and mutation proof; it is not part of ordinary implementation.
   A slow or conditional gate is not silently part of ordinary implementation.
5. If a source surface exports a generated mirror, run its canonical exporter
   once after batching source edits, then validate the result. The source is
   authoritative; mirror drift is a release/package concern, not a reason to
   duplicate authoring work.
6. Commit after verification; the external phases that need an explicit request
   are listed in [operating contract](./operating-contract.md#external-changes).

When a documentation change is unusually broad, [authoring-preflight](./authoring-preflight.md)
and [check_doc_authoring_preflight.py](../scripts/gates/check_doc_authoring_preflight.py)
are authoring affordances that forecast the relevant checks. When deleting a
wrapper or symbol in `docs/` or `skills/`, [check_symbol_residue.py](../scripts/gates/check_symbol_residue.py)
remains advisory by design (#259): use it to find consumers, then let the owning
focused test decide.

## Worktree and runtime hygiene

Worktree rules are owned by
[operating contract](./operating-contract.md#git-and-worktrees) and the commands
by [worktree prepare](./worktree-prepare.md).

## Proof proportionality

Proof proportionality is owned by
[operating contract](./operating-contract.md#verification); the `prove` skill is
an evidence formatter for the cases it lists, not a universal stop ceremony.

## Shared commands

The quality lanes, the standing runner, and the
[check-docs.sh](../scripts/check-docs.sh) receipt are in
[development](./development.md#verification-and-export); the
direct-`pytest` export line is in
[operating contract](./operating-contract.md#generated-surfaces).
