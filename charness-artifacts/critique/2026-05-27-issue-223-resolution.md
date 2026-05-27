# Critique — corca-ai/charness#223 resolution

- **Execution**: executed (bounded fresh-eye subagents)
- **Fresh-Eye Satisfaction**: parent-delegated
- **Packet Consumed**: `charness-artifacts/critique/2026-05-27-041953-packet.md`
- **Target**: `references/code-critique.md` (prompt-surface + script contract change)

## Change

Resolve #223: make duplicate-test pressure observable at slice boundaries in
long autonomous `achieve` runs, and make `quality` distinguish structural test
cleanup from hiding test bodies and report the smallest next cleanup on broad
gate failure. Implemented as prose-contract edits (achieve SKILL.md, lifecycle.md,
goal-artifact.md; quality SKILL.md anchor + testability-and-selection.md section),
a new free-text `--test-pressure` slice-log field, and a regression test. No
Charness-owned duplicate runner; no Ceal-specific rule.

## Angles

1. Dead-prose / over-instruction risk.
2. Issue #223 acceptance fit (no silently dropped acceptance point).
3. Cross-surface consistency, duplication, and regression risk.

## Findings (deduped)

- A. Before-phase "expected test-duplication pressure" prediction is a planning
  prior with no baseline; risks a vacuous line.
- B. `--test-pressure` is unenforced free text; "stays visible" relies on agent
  discipline.
- C. Issue point 5 ("HITL artifacts carry quality state forward") was carried in
  the goal artifact but not explicitly into the `blocked`/HITL handoff record.
- D. No positive regression test asserted the new slice field renders.
- E. Recommended-Outcomes paragraph lightly restates the new section.

## Counterweight Triage

- **Act Before Ship**: none.
- **Bundle Anyway**: D — added `test_render_slice_block_includes_test_duplication_pressure`
  guarding the field render and its order between Targeted verification and Critique.
- **Bundle Anyway (maintainer call)**: C — tightened the `blocked`-status step in
  lifecycle.md to cite the latest `Test duplication pressure` sample, closing the
  only "partial" acceptance point at one-line cost.
- **Over-Worry**: A (planning prior is intentional and cheap), B (prose-level fix
  is what the issue accepts; conditional free-text validation would be the
  over-instruction trap the acceptance shape warns against), E (reinforcement at
  the recommendation-ordering site, not redundancy).
- **Valid but Defer**: none remaining after bundling C/D.

## Deliberately Not Doing

- No `check_goal_artifact.py` validation that the `Test duplication pressure`
  field is populated when a slice touches tests. Conditional free-text
  enforcement would push toward the Charness-owned-runner trap the issue
  acceptance shape forbids; the field stays an agent-discipline prose contract.
- No Charness-owned duplicate/length runner. The gate stays repo-local; Charness
  owns only detection and recommendation.

## Next Move

Bundled C and D applied. Re-sync plugin export, re-run slice closeout with
`--ack-cautilus-skill-review`, then commit/push/auto-close and release.
