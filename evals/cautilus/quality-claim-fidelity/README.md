# Quality skill claim-fidelity harness

Does a real `/charness:quality` run honor its own central claims — most of all,
that it routes to its references at the point of need? This harness runs the
**current installed skill** as a real user would, captures the **full session-log
tree** (parent + subagents), and lets **cautilus** score whether the run kept its
claims and respected a runtime budget.

It is the single-arm counterpart to the skill-clone-experiment A/B
(`evals/cautilus/skill-experiment/`): that one compares two skill versions on
source-coverage; this one asks whether one skill's real behavior matches what its
`SKILL.md` says it does.

## Pieces

- `scripts/agent-runtime/capture-skill-run.sh` — runs one isolated, real
  `claude -p "/charness:quality"` against a throwaway worktree at a chosen ref,
  with a per-run `CLAUDE_CONFIG_DIR` whose marketplace points at that worktree
  (so the slash command resolves to the ref under test, never the shared install
  clone — the #258 hazard) and `core.hooksPath` pinned to the worktree (a worktree
  otherwise inherits the main clone's absolute hooksPath and the maintainer-setup
  gate derails the run). Leaves the full session-log tree on disk.
- `scripts/agent-runtime/build-skill-execution-observation.mjs` — reads every
  `*.jsonl` under the session tree (parent + `subagents/*.jsonl`, so a reference
  read delegated to a subagent is still counted — the blind spot a parent-only
  grep misses), applies the spec's claim matchers, reports declared-reference
  coverage and a tool-call profile, and emits a
  `cautilus.skill_evaluation_inputs.v1` observed packet.
- `spec.json` — the quality skill's claims encoded: `requiredCommandFragments`
  (the lens-detail ref `SKILL.md` step 4 routes to), `declaredReferences` (the
  full reference set, for the coverage report), and `thresholds`
  (`max_duration_ms`, scored by cautilus for the `runtime_budget_respect` degrade).

## Run

```bash
# 1. capture (real run; on-demand, trusted checkout only — uses skip-permissions)
out=/tmp/quality-claim-fidelity
scripts/agent-runtime/capture-skill-run.sh \
  --ref HEAD --invocation "/charness:quality" --out-dir "$out"
# prints SESSION_TREE=<dir>

# 2. score the run into an observed packet (full tree -> claim matchers + coverage)
node scripts/agent-runtime/build-skill-execution-observation.mjs \
  --session-tree "<SESSION_TREE>" \
  --spec evals/cautilus/quality-claim-fidelity/spec.json \
  --output "$out/observed.json"

# 3. let cautilus score the packet (OPERATOR-GATED — see below)
python3 scripts/run_cautilus_eval.py --mode observation -- \
  --input "$out/observed.json" --output "$out/summary.json"
```

Step 3 runs `cautilus evaluate observation`, which is eval-only/ask-before-run:
`scripts/plan_cautilus_proof.py` returns `next_action: none` /
`must_ask_before_running: true` on a clean tree, so the wrapper refuses until an
operator authorizes the run. Steps 1–2 are host-owned and need no gate; step 2's
observed packet already carries the deterministic claim/coverage verdict, so the
cautilus step is the recommendation rollup + budget degrade, not the evidence.

## 2026-06-22 baseline

First real run (`/charness:quality` on `5a9d6fa8`, isolated, hooksPath fixed,
completed in ~12.6 min / 53 turns):

- **Reference coverage: 0/39.** The run never opened `quality-lenses.md` or any
  other declared reference.
- **Tool profile: Bash=77, Read=8, Edit=3, Write=2, Agent=1.** The skill's work
  was gate execution and interpretation, not reference-driven judgment.
- It still produced a capable posture summary (found a real `dup-ratchet` red gate
  and a CI enforcement gap) — so the gap is not competence; the gate-driven run
  **never enters the reference-consulting / judgment phase**, so the references go
  unread at runtime.
- Claim matcher: `failed` (required `quality-lenses.md` not read); duration
  exceeded the 600000ms bar — both feed a cautilus `reject`/degrade.

This is an **execution-shape** signal, not a reference-value verdict: ref value is
settled (2026-06-21 disposition — delete 0, "discoverability gap, not bloat"; blind
A/B 7/7 reach-via-pointer). Improvement direction: make the runtime reach the
judgment phase (triage the front-loaded gate suite) and/or wire references into the
gate-driven flow so the proven-good routing is reached at the point of need.
Pruning is out of scope. Re-running this harness after such a change is the
before/after proof.
