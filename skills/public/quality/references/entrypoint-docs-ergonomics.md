# Entrypoint Docs Ergonomics

`quality` should review first-touch docs with the same general philosophy it
already applies to skill bodies:

- less is more
- progressive disclosure
- trust a smart model or operator when inference is safe
- keep one maintained owner instead of repeating setup/update/help prose across
  multiple entry docs
- when one canonical bootstrap exists, prefer a thin README-first contract over
  a second install manual

This is not a rule that every repo must have the same document set or the same
layout. It is a lens for asking whether the docs that start work are carrying
only the next move, or whether they are accreting into competing manuals.

## Review Questions

- Does the entrypoint doc orient the next move clearly, then hand detailed
  procedure to a deeper maintained document?
- Is there one obvious owner for recurring setup/update/proof detail, or are
  nearby entry docs repeating the same instructions?
- When a CLI owns a deterministic first bootstrap, would a pasteable README
  contract plus a repo-owned next-action command be clearer than a separate
  install document?
- Are explicit modes, flags, or branch explanations doing real safety work, or
  compensating for weak defaults and weak inference?
- Is the doc trying to narrate every predictable branch instead of trusting the
  agent or operator to follow a linked deeper owner?
- Does any agent-facing prose still tell the reader to fetch a remote install
  doc and follow it instead of pasting the contract directly?
- Would trimming this doc make the next move harder, or only remove duplicate
  prose?

## Advisory Inventory

Use `<repo-root>/scripts/inventory_entrypoint_docs_ergonomics.py` when operator, developer,
or agent-facing entry docs are in scope.

The helper stays advisory on purpose. It does not claim to prove good writing.
It only inventories signals that deserve a human quality pass:

- long first-touch docs
- weak progressive disclosure when a long doc has no deeper markdown owner
- many command fences with no deeper doc link
- repeated `mode` / `option` / `flag` language that may signal unnecessary
  branching
- high inline-code density with no deeper doc link, which can suggest a doc is
  trying to carry too much procedural detail itself
- host instruction runbook pressure, where `<repo-root>/AGENTS.md` embeds a multi-step
  recovery or setup procedure that likely belongs in a deeper maintained doc
  or repo-owned command surface
- stale assumptions that every installable repo needs `INSTALL.md` or
  `UNINSTALL.md`, even when README Quick Start already owns first bootstrap

Treat these as prompts, not automatic failures.

## Command Docs Drift Gate

When a repo owns an installable CLI, bootstrap script, or operator command
surface, `quality` should ask whether the first-touch docs are close enough to
the real command surface for a later agent to act without rediscovery.

Promote the concern into a deterministic gate when the command surface is
stable enough to name. A portable gate should usually:

- run no-side-effect help commands such as `<cli> --help` and
  `<cli> <subcommand> --help`
- declare the first-touch docs that own each command's operator contract
- check required help anchors for stable options or subcommands
- check required doc phrases for behavioral invariants such as read-only
  doctor behavior, explicit delete flags, managed install ownership, or
  machine-readable output
- check forbidden doc phrases when deprecated remote-doc handoff language or
  package-manager guidance must not reappear
- check forbidden doc phrases when a deprecated path must not reappear

Do not try to prove broad prose quality with substring checks. The gate should
only protect command existence, option visibility, and crisp semantic
invariants. Keep taste, structure, and progressive-disclosure review in the
advisory inventory above.

Keep repo-specific command names and doc ownership in a repo-local contract
such as `<repo-root>/.agents/command-docs.yaml`, then call the checker from the standing
quality gate. The public skill should carry the pattern; the adapter or
repo-local contract should carry the actual CLI surface.
