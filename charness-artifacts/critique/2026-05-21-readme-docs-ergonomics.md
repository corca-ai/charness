# README Docs Ergonomics Critique
Date: 2026-05-21

## Decision

Trim README as a first-touch orientation surface without turning
[docs/cli-reference.md](../../docs/cli-reference.md) into the prose owner.

## Fresh-Eye Review

Bounded reviewer found the same overload as the local quality inventory:

- `How You Use It` mixed first-run safety, new-project procedure,
  existing-repo procedure, direct invocation syntax, retros, and Cautilus.
- `Core Concepts` repeated long philosophy blocks and connected-area links.
- `Skill Map`, support/integration detail, and `Learn More` carried more
  inventory and packaging detail than first-touch readers need.

## Applied

- Replaced README procedure blocks with compact `Workflow Routes` orientation.
- Moved detailed new-project and existing-repo route examples to
  [docs/workflow-routes.md](../../docs/workflow-routes.md).
- Compressed `Core Concepts` into the eight durable principles while keeping
  [Skill Map](../../README.md#skill-map) discoverable.
- Replaced support/integration inventory with links to
  [support skill policy](../../docs/support-skill-policy.md) and
  [control plane](../../docs/control-plane.md).
- Updated [readme-proof](../../docs/readme-proof.md),
  [handoff](../../docs/handoff.md), and the current quality artifact so the
  truth surfaces match the new README shape.

## Counterweight

Do not trim Quick Start, the basic CLI trio, direct invocation syntax, or the
public skill map: those are the first-touch discovery points. Do not make a new
gate yet; the useful proof is the existing docs ergonomics inventory showing
README no longer trips the entrypoint heuristics.

## Verification

- `inventory_entrypoint_docs_ergonomics.py` reports README
  `core_nonempty_lines=134` and no heuristics.
- `python3 scripts/check_doc_links.py --repo-root .` passes after the link
  changes.
