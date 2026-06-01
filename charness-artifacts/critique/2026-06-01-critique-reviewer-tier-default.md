# Fresh-Eye Critique: Critique Reviewer Tier Default

Target: critique adapter defaults for high-leverage fresh-eye reviewers.

## Change

The repo-owned `critique` adapter and newly scaffolded adapters now declare a
Codex high-leverage reviewer tier:

- `model: gpt-5.5`
- `reasoning_effort: medium`
- `service_tier: priority`

The public skill prompt now tells agents to apply
`reviewer_tiers.high-leverage` spawn fields when the host exposes them.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated.

Reviewer:

- Singer (`019e82d0-7eea-7001-8a37-0e15557cb74a`) — adapter portability and
  default propagation

## Act Before Ship

Fixed before closeout:

- Removed the initial missing-adapter inference of Codex-specific reviewer
  tiers. Adapter-less repos still use inferred generic defaults and consume no
  prepare packet.
- Kept the Codex default in the live repo adapter and in `init_adapter.py`, so
  repos that adopt the adapter inherit the intended Charness default.
- Added regression coverage for the live adapter, scaffolded adapter, and
  adapter-less behavior.

## Counterweight Triage

No remaining ship blocker after the portability fix.

Bundle anyway:

- Keep the live adapter, scaffold, public contract, skill instruction, tests,
  and plugin mirror together because they define one adapter behavior.
- Keep `service_tier: priority` in both implementation and tests because the
  intended default is the full high-leverage spawn profile, not only model and
  reasoning effort.

Over-worry:

- Do not block on a runtime-level spawn-field validator in this change; current
  host exposure is still prompt/adapter mediated.

Valid but defer:

- A future host adapter can add a machine-checked bridge from resolved
  `reviewer_tiers` to actual subagent spawn arguments.

## Verification Cited

- targeted reviewer-tier tests
- adapter validation and live adapter resolution
- public skill and packaging validators
