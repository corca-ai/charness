# Quality Catalog Redesign Closeout Critique

## Decision

Ship this slice after deterministic validation and commit.

The redesign keeps the public `quality` skill's essence in the core while
moving reference routing and gate packet metadata into
`references/catalog.yaml`. The planner now gives the generative sequence:
read required primers, run applicable evidence packets with cost/trust/parallel
metadata, then open on-demand references from concrete findings.

## Fresh-Eye Findings

Three bounded reviewers checked execution mechanics, progressive disclosure,
and validation drift. The real ship blockers were:

- `gate_packets` could read as mandatory and Charness-specific for every repo.
- `security-npm.md`, `security-pnpm.md`, and `security-uv.md` were in the
  reference index but not the executable catalog.
- Public-skill dogfood still described only `required_primer_refs`, missing the
  new `required_reads` / `gate_packets` contract.
- Planner phase-barrier wording mixed the old compatibility key with the new
  schema.
- Exact closeout and fresh-eye reviewer contracts still needed point-of-use
  visibility in the compressed core.

All five were addressed before closeout.

## Counterweight

A fourth bounded reviewer found no remaining ship blocker. Two cheap bundle
items were also addressed before commit:

- harmonized the older dogfood evidence sentence to the new planner contract
- asserted all three package-manager security references in the planner test

Remaining concerns are valid follow-up, not blockers:

- exact-ish planner tests such as trigger counts still create brittleness
  pressure
- `required_primer_refs` remains as a compatibility key until a later schema
  cleanup
- broader exact-prose test smell deserves a separate audit instead of widening
  this slice

## Proof Plan

This slice is prompt-affecting but does not require a live Cautilus run. The
planner returned `next_action: none`; deterministic skill, dogfood, packaging,
markdown, prompt-proof, Python, and closeout gates own the proof.
