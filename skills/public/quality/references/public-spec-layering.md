# Public Spec Layering

Once a repo adopts public executable specs, `quality` should audit proof layering,
not only proof presence.

## Public-Spec Boundary

Public executable specs should own current reader-facing claims plus cheap local proof.

They should not become the main home for:

- source inventory tables
- implementation-file pinning
- future roadmap or next-session notes
- low-level structural guardrails that a non-developer reader cannot evaluate

## Layering Matrix

- public executable spec: cheap reader-facing contract proof
- app or unit test: single-command behavior, payload shape, normalization, edge cases
- smoke test: cross-command or repo-mutation integration seams
- on-demand E2E: expensive external-consumer or environment-heavy flows

The rule is simple: prove each claim at the narrowest layer that can own it
honestly, and delete the repeated happy path once a narrower layer already owns
it.

## What To Flag

Heuristic review is enough to be useful. Look for:

- public spec pages dominated by source guards or implementation paths
- public spec pages mixing current claims with future-state language
- spec blocks that mostly delegate to broad test runners
- the same happy-path command example repeated across public specs
- standing smoke or E2E paths that likely repeat a public-spec happy path

## Review Question

Do not ask only "what is missing?"

Ask both:

- what is still unproven?
- what is now duplicated at the wrong layer?
