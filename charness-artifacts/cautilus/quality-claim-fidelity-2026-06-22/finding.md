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

## What it means

The quality skill's intelligence goes into running and interpreting ~77 gate
commands, not into reading its own 39-file reference corpus (0/39). The references
are **dead weight relative to actual behavior** — even the 2026-06-21 disposition
that *added inline routing pointers* to seven of them did not change reading
behavior (which also explains the earlier skill-experiment zero-delta: neither arm
read the routed refs). The skill keeps its OUTPUT claim (it produces a posture
review) but not its MECHANISM claim (route to references at the point of need).

## Improvement directions surfaced

1. **Wire references into the gate-driven flow** so they are reached at the point
   of need (e.g., a gate's finding cites the reference the agent must open to
   classify it), or
2. **Prune the orphaned references** the runtime never consults, or
3. **Trim/triage the front-loaded gate suite** so judgment-phase work (lenses,
   references) is reached well inside a sane time budget.

Re-running this harness after such a change is the before/after proof. This is
also the first end-to-end use of cautilus's `dev/skill` execution surface from
charness as a host (see the cautilus-usefulness issue this motivates).

## Reproduce

`evals/cautilus/quality-claim-fidelity/README.md`. Evidence in this bundle:
`session.parent.jsonl` + `session.subagent.jsonl` (raw tree), `observed.v1.json`
(scored packet), `summary.v1.json` (cautilus verdict), `justification.md`.
