# Retro — cautilus quality claim-fidelity session (2026-06-22)

Mode: session

## Context

Redesign of the cautilus skill-usage validation work after operator review, then
a pivot to a single-arm claim-fidelity eval of the `quality` skill. Shipped a
reusable harness (`evals/cautilus/quality-claim-fidelity/` +
`build-skill-execution-observation.mjs` + `capture-skill-run.sh`), one cautilus
`reject` verdict (0/39 refs read, gate-dominated), and issues corca-ai/cautilus#49
+ corca-ai/charness#397. Reviewed because two operator corrections exposed real
workflow misses.

## Waste

- **Reinvention framing of an existing capability.** I verified plugin-resolution
  isolation (Q1) and headless slash-command invocation (Q2) and drafted a
  skill-clone-experiment + `review variants` capture stack as if building new,
  when cautilus already ships the `dev/skill` execution eval surface
  (`evaluate observation` + `skill-test-claude-backend`/`-expectations`,
  token-telemetry that the operator had already optimized). The empirical
  verification was reused in the final harness, so the loss was bounded — but the
  initial direction (a bespoke review-variants/bare-A-B path in the committed
  spec) was wrong until the operator pointed me to reuse. Root: I read cautilus
  narrowly (scorer + comparison-prepare) and didn't survey the CLI surface, so I
  missed the dev/skill seam.
- **Re-litigating a settled decision (the headline miss).** My next-session
  proposal told the operator to "diagnose 39 refs → classify orphaned → prune."
  The 2026-06-21 disposition already concluded the opposite, operator-reframed:
  **delete 0, "nothing is meaningless," "un-routed ≠ worthless, test-pin ≠
  valuable — the defect is a discoverability gap, not bloat,"** and that the
  routing heuristic **over-flags "orphan."** I also let the same "prune orphaned
  refs" framing into the filed issue #397.

## Critical Decisions

- Scout-inline-first (smoke captures before building) caught the gate-domination
  and the original design flaw cheaply, before heavy investment. Right call.
- Reframe (operator-led) from bare baseline-vs-variant A/B to single-arm
  claim-fidelity on cautilus's `dev/skill` surface. Right, and it scored cleanly.
- Full-session-tree matcher (parent + `subagents/*.jsonl`) instead of parent
  stdout only — fixed the subagent-read blind spot that bit the earlier capture.
- Surfacing the design-flaw finding to the operator instead of forcing a green.

## Reconciliation (the correction the operator asked for)

The `0/39 refs read` finding does NOT reopen ref value or ref reachability — both
are settled: the merit fan-out judged every ref valuable (0 deletes), and the
blind A/B proved 7/7 reach-via-pointer WHEN the agent does a ref-seeking task.
The new finding is a DIFFERENT axis: in a real `/charness:quality` run the agent
is **gate-driven and never enters the reference-consulting / judgment phase at
all** — the gate suite satisfies "task complete" before any reference is needed.
So `0/39` is a symptom of **execution shape**, not a value or reachability
verdict. The references are valuable AND well-routed AND reachable-on-demand; the
gap is that the runtime never creates the demand. Remediation belongs on the
execution-shape layer (gate front-loading vs the judgment phase), not on the refs.

## Expert Counterfactuals

- Chesterton's-Fence / archivist lens: before proposing to prune or re-examine an
  artifact set, retrieve the prior decision record on it; a prior explicit "keep
  all — the issue is discoverability" is a fence. New evidence only removes the
  fence if it contradicts that decision. `0/39` does not contradict "refs
  valuable"; it lands on a different axis, so the fence stands and the proposal
  should have targeted execution shape from the start.

## Next Improvements

- **workflow:** When a new measurement (e.g. `0/N` coverage) implicates an
  artifact set a prior session ruled on, reconcile against that conclusion
  (handoff / recent-lessons / the disposition artifact) and attribute the symptom
  to the correct layer BEFORE proposing remediation. Cheap pre-check: grep
  `charness-artifacts/quality/` + handoff for the artifact set's prior verdict.
- **capability:** the claim-fidelity harness now exists and is reusable; the
  next-session work is execution-shape (gate triage so the judgment phase is
  reached), NOT a ref disposition redo.
- **memory:** `0/39 refs in a real quality run = execution-shape (gate-domination
  bypasses the judgment phase), not a ref-value/reachability verdict (settled
  2026-06-21: 0 deletes, discoverability-not-bloat).` Recorded here +
  `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-22/finding.md`.

## Sibling Search

Transferable pattern: mis-attributing a symptom to a layer that already has a
settled disposition, and re-opening that decision. Four-axis scan:

- **other artifacts this session:** issue corca-ai/charness#397 carries the same
  "prune the references the runtime never consults" leg → must be corrected to the
  execution-shape framing. (Action: edit #397.)
- **other skills/docs:** the harness README + finding.md already frame it as
  "references bypassed by gate-driven behavior" / "wire OR prune" — the "prune"
  hedge there should defer to the settled 0-deletes too (soften to "the unread set
  is a gate-engagement symptom; pruning is out of scope per 2026-06-21").
- **scripts/gates:** none — the analyzer reports coverage neutrally; it does not
  recommend pruning.
- **prior sessions:** no recurrence; this is the first time the execution-vs-merit
  axis confusion appeared.

## Persisted

(set by persist helper)
