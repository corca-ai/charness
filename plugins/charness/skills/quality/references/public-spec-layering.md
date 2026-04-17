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

## Keep, Move Down, Delete

Use this decision split when public specs, smoke tests, and E2E paths all
exist:

- keep in the public spec: one cheap reader-facing command or scenario that
  proves the current contract directly
- move down into app or unit tests: payload shape checks, normalization
  branches, edge cases, and low-level structure assertions that readers do not
  need in the public contract
- keep in smoke tests only when the value is cross-command flow, repo mutation,
  or a seam that a narrower layer cannot own honestly
- keep in on-demand E2E only when the value is external-consumer, environment,
  or expensive install/onboarding behavior not suitable for standing gates
- delete from smoke or E2E when the test only repeats the same happy-path claim
  already owned by a cheap public spec or lower-layer test

## Review Outputs

The review should not stop at "layering looks suspicious." It should say which
move is implied:

- `move_down`: broad delegated runner proof or low-level assertions leaked into
  the public spec surface
- `delete_or_merge`: the same happy-path public proof is repeated across
  multiple public specs
- `keep_if_integration_value`: smoke or E2E paths should stay only when they
  add cross-command, repo-mutation, or external-consumer value beyond the
  public spec
- `delete_if_happy_path_only`: smoke or E2E paths that do not add that extra
  value should be removed once a narrower layer owns the claim

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
