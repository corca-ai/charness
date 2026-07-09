# T3 step-7 slim frozen-text critique
Date: 2026-07-09
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

Freeze `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-workflow-replacement.md`
as the T3 rewrite payload for `plugins/charness/skills/handoff/SKILL.md#handoff/workflow@51a25aa66f`.
The replacement keeps `## Workflow` steps 1-6 byte-equivalent to f84eb223 and
changes only step 7's duplicate literal closeout-token wording into a pointer
to `## Closeout Vocabulary`.

## Failure Angles

- Public-skill prose risk: a pointer is more abstract than inline token spelling, so the model might miss the emitted `Refresh kept:` / `Refresh non-claims:` literals unless the experiment observes them directly.
- Experiment integrity: the payload must be the literal frozen replacement, not a deletion-arm carryover from the pilot, and both plugin/public mirrors must match the same bytes.
- Blinding risk: the capture refs must remain parentless raw snapshot SHAs with no `refs/prompt-mutants/*` handles.

## Counterweight Pass

- The prose risk is real but testable; T3 now includes dedicated emitted-token sentinels for `Refresh kept:` and `Refresh non-claims:` in addition to the planner and `spill-targets.md` sentinels.
- The deletion-arm concerns from one reviewer were stale against the old pilot report, not the current generated rewrite manifest. Current proof shows a single rewrite unit, `operator_kind=rewrite`, and no legacy `mutant_ref`.
- Byte identity was checked after manifest generation: plugin and public Workflow sections in the mutant snapshot both equal the frozen replacement hash `860483a0a100132980da0c077a9e9b80abfd5d2598d358c63cee5796e4170e01`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-mutants.json` | action: fix | note: Add direct emitted-token sentinels so T3 does not over-claim from planner/spill sentinels alone; fixed before captures.
- F2 | bin: bundle-anyway | evidence: strong | ref: `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-workflow-replacement.md` | action: document | note: The frozen text is shippable if the experiment passes, but it is intentionally more abstract than inline spelling.
- F3 | bin: over-worry | evidence: moderate | ref: `charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md` | action: defer | note: Deletion-arm and parent-diff concerns describe the completed pilot, not the current T3 rewrite manifest; current arms are parentless snapshots.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium; service_tier inherited.
- Host exposure state: requested_fields_sent
- Application state: host returned reviewer agent ids and completion payloads. One reviewer reported no nested Agent tool inside its own runtime, but parent delegation did run.

## Fresh-Eye Satisfaction

parent-delegated — three bounded read-only reviewers completed through
`multi_agent_v1.spawn_agent`.

## Boundary Ownership

- Producer: the frozen replacement artifact and prompt mutant generator produce the rewrite payload and manifest.
- Consumer: the live capture/scorer/judge packet consumes those bytes as the T3 experimental treatment.
- Owning surface: prompt-mutation experiment artifact and generator manifest.
- Verdict: owned-correctly
