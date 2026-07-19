# Portable Proof Learning Retro
Date: 2026-07-19

## Mode

session

## Context

Recent speed, quality, release, and proof slices were audited to determine
which lessons were merely local history and which were usable by another repo.
The slice moved the latter into concept-owned public skills, dogfooded their
first-prompt contracts, and tightened release recovery around exact tag
identity.

## Evidence Summary

- The default quality planner output is 4,854 bytes versus 23,021 bytes with
  detail, about 79% smaller while preserving the executable next action.
- Public-skill dogfood passes all 20 required cases and now exercises the new
  quality, implementation, proof, retro, and skill-authoring contracts.
- Release recovery tests use real lightweight and annotated tags and reject a
  local/remote object mismatch before any mutation.
- Three bounded fresh-eye reviews found four concrete gaps; two focused
  re-reviews accepted the repairs, and both reviewer boundary fingerprints
  remained unchanged.
- The final broad suite exposed one raw-prose contract coupling after 4,955
  passes; a 15-case focused packet now proves whitespace-insensitive contract
  matching and dual-stream failure summaries.

## Waste

The audit initially copied a five-field proof-path method into an inventory
result even though the quality reference already owned that method. That would
have created a second mini-rulebook. The first remote-tag parser also accepted
malformed or unrelated `ls-remote` records, and the first dogfood edit updated
skill prose without updating the executable consumer registry. Finally, file
headroom was checked after the helper grew, forcing a late mechanical module
extraction. These were avoidable ownership and consumption mistakes, not
missing test volume.
The final lock also showed that a gate described as a representative contract
guard still compared raw Markdown substrings, while its summary renderer hid
stderr behind non-empty stdout. The failure was useful; the diagnostic path
made the correction slower than necessary.

## Critical Decisions

- Put each reusable rule at its concept owner: quality owns proof economics,
  implementation owns the current-consumer envelope, prove owns actual input
  consumption, retro owns portable-candidate capture, and create-skill owns
  promotion into a reusable capability.
- Keep inventory output compact: report observed finding types and point to the
  canonical method instead of duplicating it.
- Treat a remote tag as recovered only when its exact peeled object identity
  matches local state; tag presence alone is provisional evidence.
- Remove compatibility claims for the retired Python proxy's pretty JSON and
  traceback text. Retain only decoded argv semantics consumed by current tests.

## Expert Counterfactuals

- A database-normalization lens would have rejected the duplicated inventory
  method immediately: facts belong in the observation record and method belongs
  behind one stable reference.
- A protocol-design lens would have specified remote tag recovery as an exact
  identity relation before implementation, making malformed, duplicate, and
  unrelated records obvious negative cases.
- An information-theory lens would have made compact planner output the default
  and charged detail only when a human explicitly asks for it.

## Sibling Search

- same layer: public-skill dogfood acceptance | decision: same gap, fix now |
  proof: all changed skill contracts have executable registry cases
- abstraction up: retro-to-skill promotion | decision: same gap, fix now |
  proof: `Portable Candidate` now routes evidence into `create-skill`
- specialization down: release resume tag parsing | decision: same gap, fix now
  | proof: strict parser and real annotated/lightweight remote tests
- mental-model sibling: issue closeout's terminal `verified` status | decision:
  defer | reason: migration may be breaking and needs an additive schema choice

## Next Improvements

- workflow: capture the selected focused mutation command as part of the first
  mutation plan, before the broad lock run.
- capability: persist pre-commit rollback results in a durable typed record.
- capability: bind post-publication confirmation to an explicitly different
  observer identity as well as a different evidence channel.
- memory: a route or selector proves mechanism only; closure requires a
  representative changed input to reach the final consumer.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-portable-proof-learning-retro.md
