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
4. Run focused tests for the changed behavior, then the default core lane when
   the changed surface has cross-module consumers. Use
   `./scripts/run-quality.sh --release` for the release-final changed-line
   coverage and mutation proof; it is not part of ordinary implementation.
   A slow or conditional gate is not silently part of ordinary implementation.
5. If a source surface exports a generated mirror, run its canonical exporter
   once after batching source edits, then validate the result. The source is
   authoritative; mirror drift is a release/package concern, not a reason to
   duplicate authoring work.
6. Commit after verification. Do not push, release, tag, install, or mutate an
   external issue unless that phase was explicitly requested.

When a documentation change is unusually broad, [authoring-preflight](./authoring-preflight.md)
and [check_doc_authoring_preflight.py](../scripts/gates/check_doc_authoring_preflight.py)
are authoring affordances that forecast the relevant checks. When deleting a
wrapper or symbol in `docs/` or `skills/`, [check_symbol_residue.py](../scripts/gates/check_symbol_residue.py)
remains advisory by design
(#259): use it to find consumers, then let the owning focused test decide.

## Worktree and runtime hygiene

The parent worktree is user state. Never reset, restore, stash, clean, or
mass-delete it to make a proof run convenient. A temporary worktree is the
owner's disposable execution state and must be created from explicit base and
target commits with its path scope recorded in the receipt.

Use the repository runtime wrapper or equivalent external locations for
`PYTHONPYCACHEPREFIX`, pytest's cache directory, coverage data, ruff cache, and
temporary artifacts. `.gitignore` only hides an ignored file; it does not
prevent a command from writing into the worktree. A cleanliness check and cache
isolation are separate facts:

- `git diff --quiet` and `git status --short --untracked-files=all` describe
  tracked and untracked changes;
- `git status --ignored --short` describes ignored output;
- the command environment determines whether the next run creates any of it.

Creation-time cleanliness is a precondition. A run-time or end-of-run check is
the diagnostic that tells us what the command actually created. Do not claim
that a clean starting tree guarantees a clean finish.

## Proof proportionality

Normal local implementation needs focused tests and, when the surface is broad,
the default core lane. It does not run changed-line coverage/mutation proof or
pay its cost. That proof belongs only to the release-final lane. Other evidence
remains conditional:

- a verdict/proof-surface change gets the narrow proof of the surface it
  changes;
- an irreversible external write gets its owning readback and boundary check;
- a release, compatibility, security, or uncertain deletion change gets the
  review appropriate to that risk.

The `prove` skill is an evidence formatter for those cases, not a universal
stop ceremony. `Achieve` owns active goal navigation and progress; there is no
session-start hook or standalone handoff artifact to keep synchronized.

## Shared commands

```bash
# fast core lane
./scripts/run-quality.sh

# explicit broad lane
./scripts/run-quality.sh --full --read-only

# source export, only when the source surface changed
python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .

# documentation receipt when docs changed
./scripts/check-docs.sh
```

If a command fails because a capability is unavailable, report that concrete
failure. Do not replace an unavailable proof with a prose assertion that it
ran.
