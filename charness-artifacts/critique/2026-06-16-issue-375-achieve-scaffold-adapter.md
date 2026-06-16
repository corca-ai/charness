# Critique: Issue 375 Achieve Scaffold Adapter

Execution: parent spawned three bounded angle reviewers and one separate
counterweight reviewer through `multi_agent_v1.spawn_agent`. Reviewers were
read-only in the shared worktree.

Fresh-Eye Satisfaction: parent-delegated

Packet Consumed: charness-artifacts/critique/2026-06-16-004228-packet.md

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host-metadata; spawn returned agent ids and completed reviewer messages

## Target

Code critique for the #375 implementation slice.

## Diff Scope

The slice adds adapter-controlled `achieve` draft Active Operating Frame scaffold
lines, applies them only when creating new goal artifacts, preserves existing
artifact idempotence, updates adapter examples/init output, syncs plugin mirrors,
and adds focused tests.

## Findings

- Michael Jackson/problem framing: no blocker. The change solves the named
  downstream scaffold/gate mismatch rather than a convenient adjacent problem.
- Gerald Weinberg/diagnostic: found one blocker. New artifact creation used
  validated adapter data without checking adapter validity, so malformed scaffold
  config could silently fall back to default wording. Fixed before commit by
  refusing new artifact creation when a found adapter is invalid while preserving
  existing artifact status-only updates.
- Atul Gawande/operational: found one bundle requirement. The new helper,
  plugin mirror, scaffold test, and critique artifacts must be included in the
  commit.
- Counterweight: no remaining Act Before Ship findings after the invalid-adapter
  refusal and helper cleanup.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_lib.py | action: fix | note: Refuse new goal artifact creation when a found achieve adapter is invalid, so scaffold config mistakes do not silently recreate the generic-frame failure.
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_scaffold.py | action: fix | note: Include the new source helper, plugin mirror, scaffold tests, and critique packet artifacts in the commit.
- F3 | bin: over-worry | evidence: moderate | ref: skills/public/achieve/references/adapter-contract.md | action: document | note: A full rendered line list is broader than a single disposition token, but it is appropriate because downstream repos may need complete frame wording.
- F4 | bin: valid-but-defer | evidence: weak | ref: skills/public/achieve/scripts/achieve_adapter_policy.py | action: defer | note: Future observability could expose scaffold line count/source in closeout policy reports, but created-artifact proof is sufficient for #375.

## Defect Class Cross-Link

No direct repeat-trap cross-link. The closest related operating lesson is the
general adapter-surface rule in `docs/conventions/implementation-discipline.md`:
portable policy belongs in the public skill surface, not repo-local memory.

## Capability Gap

None. Existing `achieve` adapter policy and helper surfaces were the right layer.

## Public Skill Dogfood Review

`python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id
achieve --json` was inspected. It reports the existing `achieve` dogfood case as
`hitl-recommended`, with acceptance evidence around routing to `achieve`,
scaffolding a draft goal artifact, surfacing `/goal @...`, and keeping drafting
artifact-only. Decision: keep the reviewed dogfood case explicit; no maintained
evaluator scenario is required by default for this adapter-scaffold slice.

## Deliberately Not Doing

- Not changing Ceal's local gate.
- Not making Charness's default draft frame use Ceal vocabulary.
- Not closing #375 in this slice; GitHub closeout still needs the final carrier
  and closed-state readback.

## Pre-Merge Action

- Completed: added invalid-adapter refusal for new artifact creation.
- Completed: removed the unused weaker `scaffold_policy()` helper.
- Completed: added focused tests for custom scaffold lines, idempotence, and
  invalid adapter behavior.
- Remaining: stage/include all new helper, plugin, test, critique, and HOTL proof
  files in the commit.
