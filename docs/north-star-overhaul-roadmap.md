# North-Star Overhaul Roadmap

Plan of record for realigning the charness harness to
[`docs/design-north-star.md`](./design-north-star.md). Authored 2026-06-18 after
the #386 pilot (v0.52.4). **Execution is post-compaction**; this is the durable
pickup so the next session continues without re-deriving it.

The governing idea: *equip a capable judge; keep teeth only where a wrong answer
escapes.* The overhaul is not "delete gates" — it is **consolidate terminal-green
gates into non-terminal per-unit-disposition + distinct-observer confirmation,
and separate concepts so prose stops displacing into reference/gate sprawl.**

## Hard rule for every phase (from the #386 premortem, F8)

Per-surface migration discipline, never bulk deletion:

1. Name the failure-mode the gate/prose currently catches.
2. Land its replacement first; prove it catches a *seeded* instance.
3. Only then delete the old surface; record a one-line rollback ref.
4. Stage surface-by-surface. **Tripwire:** the first lifecycle transition that
   closes on aggregate/proxy proof *after* a phase ships triggers a mandatory
   north-star retro before further rollout.

Counting "fewer lines / fewer gates" as success is a north-star failure
signature. The metric is: did a wrong answer's escape path close, and did a
concept get clearer.

## Phase 0 — Validate the diagnosis (gates everything else)

The diagnosis ("terminal trust at irreversible boundaries; bloat is the cost of
bespoke gates") is provisional. Before consolidating or deleting, back-test it:

- For each recurrence-cluster issue (#359, #363, #376, #381, #382, #385, #386):
  was it caught by a deterministic gate, by fresh-eye review, or did it escape?
  If review (not a gate) is the recurring catcher, that argues *for* the
  distinct-observer model and *against* adding gates.
- Bloat driver test (Weinberg): in the 5 SKILL.md bodies pinned at the 200 cap,
  measure how much is the skill's own concept vs. stacked closeout-floor
  boilerplate. If boilerplate dominates, fix the floors, not the cap.

Output: a short validated-diagnosis note. If the back-test contradicts the
diagnosis, revise this roadmap before Phase 1.

## Phase 1 — #387 as the first concrete pilot (cheap, evidenced)

[#387](https://github.com/corca-ai/charness/issues/387) "Report goal closeout
shape errors in one actionable pass." The achieve closeout gate stack surfaces
failures serially — directly observed this session: a single commit bounced
through validate-skills, then headroom, then artifact-shape, then the critique
gate, one round each. The `describe_goal_closeout_shape.py` preflight should
aggregate *all* closeout-shape errors in one pass.

Why first: small, scoped, first-hand evidence, and it *demonstrates* less-but-
better (fewer round-trips, the gate stack made legible) without touching the
trust model. Good proof the approach pays off before the big structural phase.

## Phase 2 — Consolidate the per-unit-disposition cluster (root-cause win)

operator-queue (#381), blocked-matrix (#385), and the #386 disposition-review
mandate are three faces of one abstraction: *a per-unit disposition record at a
lifecycle transition, with a rung-1 floor that forces the question and a rung-2
distinct observer that confirms or dispositions each unit.* Design one shared
concept; retire the bespoke duplication. This net-reduces both the gate stack
(~7 closeout floors) and the prose that documents each separately, and bakes in
non-terminality (no floor declares completion). This is the causal-review's
deferred generalization and the largest structural payoff.

## Phase 3 — Bloat audit + concept-separation (P2/P3)

21 SKILL.md bodies at/near the 200 cap; 17.6K reference lines; 34.7K gate-script
lines. Per surface, decide: over-stuffed by concept-mixing (separate a concept)
or genuine (keep, with headroom). Convert defensive "do not X" enumerations to
principle + one sharp example (P3). The achieve SKILL.md (hit its headroom wall
this session) is a named first candidate. Measure concept clarity, not line
count.

## Phase 4 — Non-terminality at the remaining irreversible boundaries

Issue #386 piloted non-terminality at issue-bundle closeout. Extend the
distinct-observer + distinct-channel pattern to the other irreversible boundaries
named in
the north star: release publish, prod apply, and the deferred **Direction-3**
(make `issue_tool.py verify-closeout` refuse on undispositioned HOTL entries —
the second consumer #386 deferred). Each follows the Phase-0→migration discipline.

## Separate tracks (not this overhaul)

- [#388](https://github.com/corca-ai/charness/issues/388) mutation-test
  regression — recurring CI hygiene (siblings: #355/#360/#361/#369/#370/#374/
  #379/#380/#384). Handle on its own; do not couple to the overhaul.
- [#371](https://github.com/corca-ai/charness/issues/371) agent-browser orphan
  chromium trees + profile dirs — runtime/host-state cleanup; orthogonal.

## Open questions for the operator (resolve before Phase 2)

- Appetite: shape this as one `achieve` goal (auditable lifecycle) or run phases
  as independent issues?
- How aggressive on Phase 3 deletion vs. the migration discipline's caution?
