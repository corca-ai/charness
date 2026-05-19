# Issue #178 Create-Skill Adapter Contract

## Problem

Charness #178 was filed from Ceal #114, where a request for one skill to be
available from two Slack channels was initially treated as two channel-local
skill implementations. The source failure is Ceal-specific, but the Charness
question is narrower: should `create-skill` have a repo-local adapter surface
for skill topology vocabulary and proof hints instead of baking a channel model
into the portable skill body?

## Current Slice

Add a minimal `create-skill` adapter contract and move `create-skill` from
adapter-free to adapter-required. The adapter must help a repo name its own
skill implementation topology without making Charness know Ceal, Slack,
channels, or any repo-local layout.

## Fixed Decisions

- `create-skill` remains a portable public skill. It must not mention Ceal,
  Slack, channel ids, or Ceal path layouts in the public core.
- The adapter is for repo-local authoring vocabulary and verification hints,
  not for secrets, runtime credentials, or external provider behavior.
- This satisfies the existing adapter-pattern threshold: skill topology
  vocabulary differs across repos, and re-deriving canonical implementation,
  host-facing registrations, aliases, and intentional forks on every skill
  creation would hide repo topology assumptions in the agent's one-off
  judgment.
- The default portable decision point is implementation identity:
  one canonical implementation versus an intentional fork.
- Missing adapter is no longer silent for `create-skill`; the public-skill
  validation matrix should classify it as adapter-required with `visible`
  fallback behavior.
- The first implementation slice ships the adapter contract, resolver,
  initializer, validation policy update, and deterministic tests.

## Probe Questions

- How much structure should the adapter validate now? Keep the first slice to
  string/list fields and avoid inventing nested topology schemas until a second
  non-Ceal consumer needs them.
- Should the default Charness adapter contain example topology terms? It may
  use generic terms such as `canonical implementation`, `registration`,
  `alias`, and `intentional fork`; it must not include channel-specific terms.

## Deferred Decisions

- A deterministic duplicate-directory verifier is deferred. Charness does not
  know each repo's skill placement graph, so verifier logic belongs in consumer
  adapters or repo-owned support tools once concrete consumers exist.
- Cautilus scenario-registry changes are deferred unless implementation finds a
  maintained scenario surface that already models `create-skill` adapter
  behavior.

## Non-Goals

- Do not solve Ceal #114 inside Charness.
- Do not add Slack/channel wording to Charness skill prose.
- Do not create a generic multi-registration ontology.
- Do not make `create-skill` adapter fields mandatory beyond the common adapter
  core and narrow optional lists.

## Deliberately Not Doing

- Not adding a `registration_target` enum. That name would look portable while
  still being a thin abstraction over Ceal's channel problem.
- Not requiring a workspace-scope canonical implementation path. Some repos may
  make a local placement the canonical implementation and point other
  placements at it.
- Not using adapter-free `create-skill` plus one more prose rule. The user
  explicitly wants a repo-local adapter boundary, and the current validation
  policy already has a first-class adapter-required classification.

## Constraints

- Adapter path follows the Charness public-skill convention:
  `.agents/create-skill-adapter.yaml` first, then `.codex/`, `.claude/`,
  `docs/`, and root compatibility fallback.
- `SKILL.md` owns selection and sequence. Bulky field explanations belong in
  `references/adapter-contract.md` or `references/portable-authoring.md`.
- Generated plugin exports must be synced before validators.
- Public-skill validation policy, JSON policy, docs, and tests must remain
  aligned.

## Success Criteria

- `create-skill` has `adapter.example.yaml`, `scripts/resolve_adapter.py`,
  `scripts/init_adapter.py`, and an adapter contract reference.
- `docs/public-skill-validation.json` and markdown classify `create-skill` as
  adapter-required, not adapter-free.
- `validate_public_skill_validation.py` passes with the new classification.
- Resolver output distinguishes missing adapter, valid adapter, invalid field
  types, and compatibility fallback paths.
- The checked-in public guidance states the adapter boundary without naming
  Ceal, Slack, or channels.
- Gathered source records for Charness #178 and Ceal #114 remain tied to the
  implementation discussion.

## Acceptance Checks

- `python3 skills/public/create-skill/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/create-skill/scripts/init_adapter.py --repo-root <tmp>`
- `python3 scripts/validate_public_skill_validation.py --repo-root .`
- targeted pytest for public-skill validation and create-skill adapter behavior
- changed-surface survey followed by required sync and validators

## Critique

Pre-implementation critique completed with three bounded reviewers:

- overfitting angle: no blocker; the adapter-required move has Charness-native
  footing in existing adapter-pattern and public-skill validation policy.
- portability angle: avoid Ceal, Slack, channel ids, and channel-shaped field
  names in public guidance; if `registration` is used, define it generically.
- counterweight angle: align dogfood metadata and fallback policy, not only
  public-skill validation markdown/JSON.

Actioned before implementation:

- fallback policy set to `visible`, not `allow`
- dogfood metadata included in the implementation scope
- adapter fields kept to generic string/list vocabulary and verification hints

Scenario review:

- `scripts/plan_cautilus_proof.py --repo-root . --json` returned
  `next_action: none`; live Cautilus execution is not required for this slice.
- `evals/cautilus/scenarios.json` already maps `create-skill` to
  `representative-skill-contracts`.
- No scenario-registry edit is bundled. This slice adds deterministic adapter
  bootstrap tests and dogfood metadata for the new adapter-required contract;
  it does not claim log-backed behavior improvement.

Post-implementation critique completed with three bounded reviewers:

- adapter-boundary finding actioned: provider-specific negative examples were
  removed from `references/adapter-contract.md` and replaced with a generic
  topology glossary.
- policy/dogfood finding actioned: markdown and JSON policy now agree that
  `critique` is adapter-required, and `create-skill` is adapter-required with
  visible fallback.
- artifact-drift finding actioned: `find-skills` inventory was regenerated with
  installed support skill visibility preserved, then its checked-in repo id was
  restored to `charness` instead of the worktree basename.

Additional post-commit critique completed on 2026-05-19 with three bounded
reviewers plus a counterweight pass. Packet:
`charness-artifacts/critique/2026-05-19-115234-packet.md`.

Actioned before merge:

- malformed present adapters now fail closed instead of collapsing to generic
  fallback
- unsupported adapter schema versions are rejected; version `1` is the only
  supported version in this slice
- Charness now has a canonical `.agents/create-skill-adapter.yaml`, so the
  final resolver proof exercises `found: true`, `valid: true`
- `SKILL.md` now tells agents to stop on `valid:false`, name visible fallback
  on `found:false`, and use `init_adapter.py` to scaffold the canonical adapter

Final proof:

- `python3 skills/public/create-skill/scripts/resolve_adapter.py --repo-root .`
- `python3 scripts/validate_public_skill_validation.py --repo-root .`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- `./scripts/run-quality.sh`: 62 passed / 0 failed

## Canonical Artifact

This file is the current implementation contract for issue #178 until the slice
is committed.

## First Implementation Slice

Implement the minimal adapter package and policy change, then run a full
post-implementation critique before commit.
