# Quality skill claim-fidelity — 2026-06-22

cautilus verdict on one real `/charness:quality` run: **reject** (execution
quality failed on BOTH declared dimensions).

## What ran

`/charness:quality` on `5a9d6fa8`, captured as a real user would
(`scripts/agent-runtime/capture-skill-run.sh`): isolated `CLAUDE_CONFIG_DIR`
resolving the slash command to a throwaway worktree, `core.hooksPath` pinned,
full tools, session persistence. The run **completed** (53 turns, ~12.6 min) and
produced a capable posture summary — it found a genuine red `dup-ratchet` gate (8
new fixable families), ruled out the #395 family-id churn false positive, and
flagged that `dup-ratchet` is not enforced in CI. Competence was not the problem.

`build-skill-execution-observation.mjs` read the full session tree (parent +
subagents) into a `cautilus.skill_evaluation_inputs.v1` packet; `cautilus evaluate
observation` (operator-authorized, transcript justification-log) scored it into
`cautilus.skill_evaluation_summary.v1`.

## Verdict (summary.v1.json)

- `recommendation: reject`; execution 1, **failed 1**, passed 0.
- surface `execution_quality`; intent dimensions `skill_task_fidelity` +
  `runtime_budget_respect`.
- **skill_task_fidelity FAILED:** required reference `quality-lenses.md` never
  read; **reference coverage 0/39** — the run opened none of the skill's declared
  references.
- **runtime_budget_respect FAILED:** `thresholdFindings` duration_ms actual
  755169 > limit 600000.
- tool profile: **Bash=77**, Read=8, Edit=3, Write=2, Skill=1, Agent=1.
- tokens: 8,948,439 total (78,396 output; 8,510,977 cache-read).

## What it means (execution shape, NOT reference value)

The quality skill's intelligence goes into running and interpreting ~77 gate
commands; the run never enters the reference-consulting / judgment phase, so it
reads 0/39 of its references. This is a symptom of **where the runtime spends
itself**, not a value verdict on the references.

Reference value is settled and not reopened here: the 2026-06-21 disposition
concluded **delete 0, "nothing is meaningless, un-routed ≠ worthless — the defect
is a discoverability gap, not bloat,"** and the blind A/B proved **7/7
reach-via-pointer** when the agent does a ref-seeking task. The references are
valuable AND well-routed AND reachable-on-demand; the gate-driven runtime simply
never creates the demand. (This also explains the earlier skill-experiment
zero-delta: neither arm reached the reference-consulting phase.) The skill keeps
its OUTPUT claim but not its MECHANISM claim (route to references at the point of
need).

## Improvement directions surfaced (execution-shape only)

1. **Make the runtime reach the judgment phase.** Triage the front-loaded gate
   suite so the 4-lens / reference-consulting work is reached well inside a sane
   time budget (the run spent ~12.6 min + 77 Bash calls before any judgment-layer
   read).
2. **Wire references into the gate-driven flow** so the proven-good routing layer
   is reached at the point of need (e.g., a gate finding cites the reference
   needed to classify it).

Pruning / re-judging refs is explicitly out of scope (settled 2026-06-21).
Re-running this harness after such a change is the before/after proof. This is
also the first end-to-end use of cautilus's `dev/skill` execution surface from
charness as a host (see the cautilus-usefulness issue this motivates).

## Reproduce

`evals/cautilus/quality-claim-fidelity/README.md`. Evidence in this bundle:
`session.parent.jsonl` + `session.subagent.jsonl` (raw tree), `observed.v1.json`
(scored packet), `summary.v1.json` (cautilus verdict), `justification.md`.
