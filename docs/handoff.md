# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff entries + live open issues. `## Next Session` is
  sequencing judgment, not the full queue — **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`, and skim `git log --oneline -10`
  (de-stale the queue against what recently shipped). Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Pin sweep shipped** (`1f58af89`+`18467e56`, 126/128 keep; disciplined
  pin-deletion test in the gate header). Gotcha: editing `check_skill_contracts.py`
  re-rotates the clone family → count-neutral dup-ratchet re-baseline.
- **Skill-structure audit DONE.** Raskin + north-star fan-out, 20 public skills:
  split=0, merge=0, structure healthy. [audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md).
- **Quality reference disposition critiqued + EXECUTED + validated.** 41-ref merit
  map → critique (10-skeptic, corrected 4 anchors + 2 merge targets) → **7 route-it +
  2 merge-retire, 0 deletes**; full pin sweep green + mirror synced; blind A/B
  confirmed routing **7/7 reach-via-pointer** (Cautilus gated, planner
  `next_action: none`; blind-runner capture was the in-policy substitute). Detail:
  [disposition proposal](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).
- **Headless-runner de-risk (B-smoke) DONE.** A real `claude -p` `quality` run
  resolves headless, reads refs via routing, and **spawns the Step-8 fresh-eye
  reviewer as a real subagent** (a subagent-runner can't see this). Gotcha:
  `/quality` loads from the INSTALLED clone `~/.agents/src/charness` (old `f7bf5d2c`).
- **Skill claim-fidelity harness DONE + first verdict: `reject`.** A reusable
  single-arm cautilus `dev/skill` eval (`evals/cautilus/quality-claim-fidelity/`
  + `scripts/agent-runtime/build-skill-execution-observation.mjs` +
  `capture-skill-run.sh`). A real isolated `/charness:quality` run (full tree:
  parent + `subagents/*.jsonl`) opened **0/39 references**; `cautilus evaluate
  observation` → `reject` (failed `skill_task_fidelity` + `runtime_budget_respect`,
  755s>600s, Bash=77). KEY: this is **execution shape** (gate-driven run never
  enters the judgment/ref-consulting phase), NOT a ref-value/reachability verdict
  — ref value is settled (2026-06-21: delete 0; blind A/B 7/7 reach-via-pointer).
  Bundle: `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-22/`. Issues
  filed: corca-ai/cautilus#49 (dev/skill useful + subagent-capture/token-budget
  gaps), corca-ai/charness#397 (execution-shape fix). Retro:
  `charness-artifacts/retro/2026-06-22-quality-claim-fidelity-retro.md`.

## Next Session

- **Quality-ref disposition done+validated+pushed** (critique → execute → blind A/B
  7/7). Broader 19-skill rollout stays a verify-first "where to look" map.
- **A: cautilus skill-experiment harness DONE** ([goal](../charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness.md),
  complete). Built the stream-json capture + the keystone
  transcript→`skill_clone_experiment_input.v1` extractor + wrapper wiring +
  obligations spec; **one real baseline(b01cee6b) vs variant(5ded9f3a) cautilus
  verdict: `discard`** — honest zero source-coverage delta (both arms read the same
  6 refs). KEY FINDING: source-coverage measures *which files*, not
  pointer-directness; this disposition's value (reach-via-pointer, prior A/B 7/7) is
  orthogonal to the lens. Reproduce via [the harness README](../evals/cautilus/skill-experiment/README.md).
  Deferred (operator queue): the full multi-scenario sweep; `reviewer_tiers`. Carried
  nits: DRY findResultEvent/findClaudeResultEvent; a no-name-hint eval task so
  source-coverage can discriminate this disposition class.
- **START HERE — Skill claim-fidelity + doc-philosophy across ALL skills
  (public + support).** Generalize the quality finding: the same lens applies to
  every skill. Two linked questions, per skill and per reference doc:
  1. **Per skill (execution shape):** does a real run engage its reference /
     judgment layer, or is the gate/flow path self-sufficient so the refs are
     never reached? Measure with the claim-fidelity harness
     (`evals/cautilus/quality-claim-fidelity/` is the template; one spec.json per
     skill — `declaredReferences` + `requiredCommandFragments` for the docs the
     SKILL claims to read + `thresholds`).
  2. **Per doc (quality philosophy):** when is THIS doc worth reading, and is the
     relevant gate/flow sufficient on its own? If a doc is genuinely
     gate-sufficient (its content is fully enforced/covered elsewhere), it may be
     **deletable** — but only via this principled merit + gate-sufficiency
     judgment. Do NOT reuse the rejected "un-routed/orphan ⇒ worthless"
     reachability heuristic; the 2026-06-21 quality-ref disposition (delete 0,
     "discoverability gap not bloat", blind A/B 7/7) stays settled and deletion
     reopens only on the gate-sufficiency axis.
  - **First move is a framing decision (`ideation`/`spec`), not a mechanical fix:**
    for a given skill, should a run engage its ref/judgment layer every time, or
    is gate/flow-sufficient + on-demand acceptable? If gate-sufficient ⇒ either
    delete the redundant doc OR honest-up the skill's claim (and fix its harness
    spec). If should-engage ⇒ execution-shape fix (triage front-loaded gates so
    the judgment phase is reached; or wire refs into gate findings). This decision
    gates the rest. The quality skill (#397) is the pilot; then fan out.
  - **Tooling to extend:** add a discriminating scenario to the harness (gates
    GREEN but lens-level issues lurk) so it actually tests whether a skill engages
    its refs WHEN it should; cautilus `cases[]`/`repeatCount` supports multi-scenario.
  - **Shape:** one eval per skill (~20 public + the support set) is a fan-out, but
    each run is a real `claude -p` capture (expensive) + an operator-gated
    `cautilus evaluate observation`. Budget per skill; pilot quality first.
  - **Non-blocking dep:** cautilus#49 (runner reads parent stdout only, misses
    subagent reads) is already worked around host-side by the full-tree matcher.
- **C — #387 one-pass goal-closeout shape report.** Fits
  `describe_goal_closeout_shape.py` (describe-first preflight), not a new floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
- **Parked:** #394 (mutation cron-only, auto-closes). #371 (upstream-blocked
  vercel-labs/agent-browser#1334). #391 extraction candidates.

## Discuss

- **Skill claim-fidelity framing (decide at START HERE pickup):** per skill, is
  the ref/judgment layer meant to run every time, or is gate/flow-sufficient +
  on-demand acceptable? `0/39` on quality is only a defect under the former; under
  the latter the move is delete-the-redundant-doc or honest-up-the-claim. The
  measured signal is execution shape, not ref value (settled). Operator intent
  needed before fanning out across public + support skills.
- **#392 scope (decide at pickup of D):** attempt a real exact-X route
  (browser/auth — likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale (done again this session).

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md),
  [skill-structure audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md),
  [quality ref disposition proposal](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md);
  pin-sweep convention lives in the
  [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
