# Cautilus Dogfood
Date: 2026-06-29

## Trigger

- slice: capture-prioritized rollout (skill-planner-uniformity item 3, START
  HERE) — first live capture of the `hitl` claim-fidelity floor. hitl is the
  second of the two planner-absent public skills (retro, the first, was captured
  and given a planner because its run skipped its briefed doc).
- source: hitl's static floor `requiredCommandFragments: ["chunk-contract.md"]`
  had never been exercised by a live run — a HYPOTHESIS until this capture.

## Validation Goal

- goal: preserve
- reason: prove (or refute) that a real `/charness:hitl` run honors its central
  claim — open `references/chunk-contract.md` and author bounded chunks against
  it at the point of need — and decide from the result whether hitl needs a
  planner (the retro passive-pointer shape) or correctly needs none.

## Change Intent

- intent: `truth_surface_change`. No prompt-affecting SKILL surface changed; the
  edits are truth-surface / contract records — `docs/handoff.md` (pickup pointer),
  the hitl claim-fidelity spec `_comment` + `thresholds.max_duration_ms`, and this
  proof bundle. This is a read-only baseline capture of the shipped hitl skill at
  ref HEAD to flip its floor from hypothesis to proven (or to surface a planner
  need); the floor is unchanged.

## Prompt Surfaces

- subject under evaluation (read-only) at `HEAD`=17d05065:
  `skills/public/hitl/SKILL.md`, `skills/public/hitl/references/chunk-contract.md`
  (+ the other declared references), via the isolated installed-plugin worktree
  capture.

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/justification.md`
- note: operator (bae.hwidong@corca.ai) authorized this capture explicitly
  ("hitl 캡처 합시다", 2026-06-29). One real `claude -p` capture in an isolated
  read-only worktree; no shared install clone mutated.

## Commands Run

- planner consult (verbatim, read-only): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: none`, `must_ask_before_running: true`,
  `run_mode: ask` (authorization is the operator's explicit request via
  `--justification-log`, not a green).
- capture: `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD
  --invocation "<hitl spec prompt>" --out-dir /tmp/charness-hitl-capture` → exit
  0, 101982ms, 927570 tokens.
- score: `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/justification.md
  -- --input .../observed.v1.json --output .../cautilus-report.json`

## Regression Proof

- `cautilus evaluate observation` (0.17.1): `status: passed` (passed=1, failed=0,
  stable). All declared claims met.
- behavior: the run opened `references/chunk-contract.md` via Read during step 5,
  recorded `require_explicit_apply: true` + accepted rules R1/R2/R3 (incl. "target
  file not edited mid-loop"), planned 7 chunks, then paused for human approval
  (correctly stopping in headless mode). Tool profile: Bash=6 Edit=4 Read=2
  Skill=1; the 4 Edits hit ONLY runtime state (state.yaml/scratchpad), never the
  target file — no guardrail violation. Coverage 1/5 = the only RCF floor met;
  the 4 unopened references are exactly the script-resolved/on-demand ones the
  engagement map predicts.
- no new `.cautilus/runs/` dir: observation scores an already-captured packet.

## Scenario Review

- spec `evals/cautilus/hitl-claim-fidelity/spec.json` reviewed against the live
  run: the single RCF floor (`chunk-contract.md`, engage-always presentation-
  invariant) was met; the 4 non-RCF references (adapter-contract.md + state-model.md
  script-resolved; report-mode.md + rule-propagation.md on-demand) were correctly
  not opened — the reference-engagement classification matches observed behavior,
  so no scenario re-classification is needed. The only spec change is the
  `_comment` (baseline-proven note + fakeability framing) and a
  `thresholds.max_duration_ms` derived from this passing baseline; the prompt,
  floor, declaredReferences, and engagement map are unchanged.

## Outcome

- recommendation: accept — hitl's claim-fidelity floor is live-capture PROVEN
  WITHOUT a planner. Both retro and hitl use an explicit deferring pointer in
  SKILL.md; the difference is fakeability — retro's named-expert counterfactual is
  fabricable from general knowledge (so its run skipped the doc → planner needed),
  whereas hitl's repo-specific chunk machinery is not, so the run had to open
  `chunk-contract.md`. Per the item-3 contract, hitl correctly needs no planner;
  planner-izing it would be concept-adding boilerplate.
  `thresholds.max_duration_ms` set to 240000 (101982ms baseline ×~2, retro model)
  as a degrade signal.

## Follow-ups

- n=1 caveat: single passing sample (the established methodology bar).
- rollout (open): the remaining ~17 uncaptured public skills still carry
  HYPOTHESIS floors; each needs one live capture to flip it. Next skill chosen
  per the capture-driven sweep, ask-before-run, one at a time.
