# Public Executable Contracts

Public executable specs are for reader-facing current claims, not for pinning
internal implementation structure.

## Boundary

Treat `public executable contract` and `maintenance lint / implementation
guard` as different layers.

Public executable contract owns:

- current shipped behavior
- user- or operator-facing wording
- one or two cheap executable proofs per bounded claim

Maintenance lint or implementation guard owns:

- implementation file presence
- implementation-file pinning
- source inventory tables
- fixed-string source assertions
- low-level structural drift checks

Treat fixed-string source assertions as lower-layer maintenance guards, not as
public executable contract proof. If a current spec page needs one to stay
green, the page is probably carrying the wrong layer.

## Current-State Rule

Do not mix future roadmap, planned behavior, or next-session notes into the
same executable page that claims current acceptance.

If a claim is not current, move it into roadmap, handoff, or another design
artifact instead of leaving it beside executable proof.

## Reader-Facing Rule

Write the public claim first in language a non-developer reader can evaluate.

Implementation references are acceptable only when they help explain the
boundary. They should not become the main proof surface.

## Cheap-Proof Rule

Public executable pages should prove the contract with cheap bounded slices.

When a lower deterministic layer already proves the detail honestly, keep that
detail below the public contract instead of re-asserting it in the public spec.

## Viewer Rule

Public executable pages may also act as readers for the latest checked
on-demand validation artifacts when that helps operators understand current
product intent.

In that mode:

- the checked artifact remains the source of truth for the run
- the executable page is a viewer over the latest artifact, not the storage
  layer for evaluator output
- the page should verify artifact presence, shape, and current claim framing
  without rebuilding the whole evaluator inline
