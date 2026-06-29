# Live-Capture Proof — hitl claim-fidelity BASELINE (floor proven, no planner needed)
Date: 2026-06-29

First live capture of the `hitl` claim-fidelity floor (item 3 of the
skill-planner-uniformity rollout: capture-prioritized, one skill at a time).
hitl is one of the two planner-absent public skills; retro (the other) was just
captured and given a planner because its run skipped its briefed doc. This
capture tests whether hitl shows the same passive-pointer shape. It does NOT.

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/hitl-claim-fidelity-2026-06-29/justification.md`
- note: operator (bae.hwidong@corca.ai) authorized this capture explicitly this
  session ("hitl 캡처 합시다", 2026-06-29). One real isolated `claude -p` run at
  ref HEAD; no shared install clone mutated (#258 hazard avoided via throwaway
  worktree + isolated CLAUDE_CONFIG_DIR).

## Commands Run

- planner consult (verbatim, read-only): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: "none"`, `must_ask_before_running: true`,
  `run_mode: "ask"`. Authorization is the operator's explicit request, supplied
  via `--justification-log` (the wrapper's override door).
- capture (one real isolated headless run at ref `HEAD`=17d05065):
  `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
  "<hitl spec prompt>" --out-dir /tmp/charness-hitl-capture` → exit 0, 101982ms
  wall, 927570 total tokens.
- build observed packet: `node scripts/agent-runtime/build-skill-execution-observation.mjs
  --session-tree <tree> --spec evals/cautilus/hitl-claim-fidelity/spec.json` →
  `outcome=passed | coverage=1/5 | tools: Bash=6 Edit=4 Read=2 Skill=1`.
- score: `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log justification.md -- --input observed.v1.json` →
  `cautilus evaluate observation` (0.17.1): `status: passed`, passed=1 failed=0,
  stable.

## Regression Proof (the floor survives live capture)

- Asserted floor `requiredCommandFragments: ["chunk-contract.md"]`: MET. The run
  opened `plugins/charness/skills/hitl/references/chunk-contract.md` via the Read
  tool during step 5 — a genuine doc-open, not a superficial filename mention.
- Tool sequence: `find-skills` → `resolve_adapter.py` → `charness worktree
  doctor` probe → Read target `docs/operator-acceptance.md` → `bootstrap_review.py`
  (materialized state.yaml/rules.yaml/queue.json) → **Read chunk-contract.md** →
  author queue.json (7 chunks) → update state.yaml + scratchpad.
- Coverage 1/5 is the EXPECTED profile, not a gap: the 4 unopened references are
  exactly the ones the spec's reference-engagement map classifies as not-RCF —
  `adapter-contract.md` and `state-model.md` are engage-always but SCRIPT-RESOLVED
  (the run ran resolve_adapter.py and bootstrap_review.py instead of reading the
  explainer docs); `report-mode.md` and `rule-propagation.md` are on-demand (no
  report packet, no reusable rule in this prompt). The only RCF floor was met.

## Quality Outcome (not just a doc-open)

- The run honored the chunk contract end to end at setup + first-present: it
  recorded `require_explicit_apply: true`, `apply_mode: explicit-after-all-chunks`,
  accepted rules R1 (excerpt + Agent Assessment + non-binding Recommended
  Disposition + decision, then pause), R2 (suggestion is not approval; no advance
  without explicit approval), and R3 (review-only; target file untouched
  mid-loop), planned 7 chunks + a full_target_review, then paused for human
  approval. In headless mode no approval ever arrives, so it correctly stopped —
  it did NOT auto-advance or edit the target.
- No guardrail violation despite `Edit=4`: all 4 Edits hit runtime state
  (`state.yaml` ×3, `hitl-scratchpad.md`), NEVER `docs/operator-acceptance.md`.
  The run treated chat as the review UI and the scratchpad/state files as durable
  review state — exactly the contract.

## Why hitl passed where retro failed (the distinguishing lesson)

- Both pre-fix retro and hitl use an explicit deferring pointer in SKILL.md
  (retro: "The lens patterns... live in references/expert-lens.md"; hitl: "Review
  in bounded chunks per references/chunk-contract.md"), so the structural shape is
  the SAME. The difference is FAKEABILITY, not inlining.
- retro's briefed output — a named-expert counterfactual lens — is fabricable from
  the model's general knowledge, so the first retro capture filled the
  `Expert Counterfactuals` section from generic scaffolding and never opened
  `expert-lens.md` → floor failed → planner needed.
- hitl's briefed output is NOT fakeable: `chunk-contract.md` carries repo-specific
  machinery the step-5 preview does not inline — the disposition verb vocabulary
  (accept/revise/defer), the markdown-in-markdown pseudo-tag rule, the
  good/bad-chunk rubric, the applied-rewrite-review surface, NON_AUTOMATABLE
  handoff preservation — so a faithful run must open the doc, and this run did.
- Predictive signal for "needs a planner": a passive prose pointer is FOLLOWED
  when the briefed output cannot be fabricated from SKILL.md + general knowledge,
  and SKIPPED when it can. The fix for a skipped pointer is a planner that makes
  the doc a `required_read`; the floor is fine where the pointer is already
  followed (hitl).

## Outcome

- recommendation: accept — hitl's claim-fidelity floor is now live-capture PROVEN
  (failed→never; proven at first capture), WITHOUT a planner. Per the item-3
  contract ("give a planner ONLY where a capture confirms a passive-pointer
  shape"), hitl correctly needs none; planner-izing it would be concept-adding
  boilerplate (Floor-Addition Restraint).
- `thresholds.max_duration_ms` set to 240000 (101982ms passing baseline ×~2,
  rounded to the next 60000-ms multiple — the retro model). It is a degrade
  signal, not pass/fail.

## Caveats / Follow-ups

- n=1 sample (sampleCount=1, the established methodology bar; retro's recapture
  was also n=1). A single pass is suggestive, not a stability proof.
- rollout (open): next planner-absent or unproven skill per the capture-driven
  sweep; the static floors of the remaining ~17 uncaptured skills are still
  HYPOTHESES until each gets one live capture.
