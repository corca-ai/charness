# Entrypoint Docs Ergonomics

`quality` should review first-touch docs with the same general philosophy it
already applies to skill bodies:

- less is more
- progressive disclosure
- trust a smart model or operator when inference is safe
- keep one maintained owner instead of repeating setup/update/help prose across
  multiple entry docs

This is not a rule that every repo must have the same document set or the same
layout. It is a lens for asking whether the docs that start work are carrying
only the next move, or whether they are accreting into competing manuals.

## Review Questions

- Does the entrypoint doc orient the next move clearly, then hand detailed
  procedure to a deeper maintained document?
- Is there one obvious owner for recurring setup/update/proof detail, or are
  nearby entry docs repeating the same instructions?
- Are explicit modes, flags, or branch explanations doing real safety work, or
  compensating for weak defaults and weak inference?
- Is the doc trying to narrate every predictable branch instead of trusting the
  agent or operator to follow a linked deeper owner?
- Would trimming this doc make the next move harder, or only remove duplicate
  prose?

## Advisory Inventory

Use `scripts/inventory_entrypoint_docs_ergonomics.py` when operator, developer,
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

Treat these as prompts, not automatic failures.
