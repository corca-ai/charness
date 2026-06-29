# Live-Capture Proof — retro claim-fidelity (first live capture of the sweep)
Date: 2026-06-29

This is the FIRST live capture of the per-skill claim-fidelity sweep shipped
statically in `v0.57.0`. It empirically tests retro's single asserted floor.

## Behavior Source

- source-kind: operator-log
- source-ref: `charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29/justification.md`
- note: operator (bae.hwidong@corca.ai) explicitly authorized one eval-only live
  capture, scope "retro only", this session. Authorization is the operator's
  one-run approval, not a planner green.

## Commands Run

- planner consult (read-only, verbatim): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: "none"`, `must_ask_before_running: true`,
  `run_mode: "ask"`, `goal: "preserve"`.
- capture (one real isolated headless run at ref `HEAD`=482352dc):
  `bash scripts/agent-runtime/capture-skill-run.sh --ref HEAD --invocation
  "<retro spec prompt>" --out-dir /tmp/charness-retro-capture` → exit 0, real
  `/charness:retro` run, 285074ms wall, 2.70M total tokens.
- build observed packet (host-side matcher):
  `node scripts/agent-runtime/build-skill-execution-observation.mjs --session-tree
  <tree> --spec evals/cautilus/retro-claim-fidelity/spec.json --output observed.v1.json`
  → `outcome=failed | coverage=0/9 | duration_ms=285074`.
- score via wrapper: `python3 scripts/run_cautilus_eval.py --mode observation
  --justification-log justification.md -- --input observed.v1.json --output
  cautilus-report.json` → `cautilus evaluate observation` (0.17.1): `status: failed`,
  `passRate: 0`, `derivedStatus: failed`. No new `.cautilus/runs/` dir created
  (observation scores an already-observed packet without launching a runner).

## Regression Proof (the floor did NOT survive live capture)

- Asserted floor: `requiredCommandFragments: ["expert-lens.md"]` — retro's single
  engage-always RCF floor per the spec rationale ("to fill the mandatory
  counterfactual section the run is FORCED to open expert-lens.md").
- Observed: the real run NEVER referenced `expert-lens.md` by any tool. The
  fragment matcher scans every tool-call input value across the full session tree
  (including Bash command strings), so a `sed`/`cat` read would have matched — it
  did not. The floor claim is empirically false for this run.
- What the run actually did: read references via `Bash sed/git show` (handoff,
  methodology spec, rca-ledger-append, waste-sibling-scan), ran
  `scaffold_retro_artifact.py`, wrote a complete, validator-passing retro
  (`validate_retro_artifact.py` green; RCA event recorded; recent-lessons
  refreshed). It produced a strong Expert Counterfactuals section (Michael
  Feathers characterization-first lens + a direct "spike-one-end-to-end" lens)
  entirely from the SKILL.md-inlined Expert Counterfactual Rule + named-expert
  general knowledge — see `captured-retro-artifact.md`.
- Self-corroboration: the captured run's OWN counterfactual independently flagged
  this over-declaration pattern ("first-pass claim-fidelity fixtures systematically
  over-declare RCF; default to the minimal floor" and "spike one item end-to-end
  before a fan-out").

## Honest reading / matcher integrity

- The FLOOR check (expert-lens.md fragment) is robust: it sees Bash inputs, so
  the miss is real, not a tooling blind spot. Per the handoff contract, a miss is
  a calibration signal — re-pin or re-classify the skill, NEVER soften the matcher.
- Secondary-metric caveat (do NOT use to rescue the floor): the `coverage=0/9`
  number understates reality because `collectOpenedBasenames` counts only
  `file_path`/`notebook_path` keys (Read/Edit/Write), not Bash `sed`/`cat` reads.
  The run did read ~4 references via Bash. This is a coverage-report accuracy gap,
  separate from the floor verdict; logged as a follow-up observation, not acted on
  here.

## Verdict (operator disposition, decided 2026-06-29)

The operator rejected both "re-classify the fixture down" and "re-pin the prompt"
and reframed the miss as a **skill-shape defect**: a good skill briefs the judge
via a deterministic surface, not a prose pointer. Root cause (evidence in git):
the 2026-06-23/24 planner-first sweep gave debug/handoff/quality/issue/gather/release
a planner that emits `required_reads`; retro and hitl were left **planner-absent**,
and the claim-fidelity sweep then calibrated retro as *fidelity-to-current-shape*
(`7fb51ac8 ... by lens 7 script-briefs-judge`), freezing the planner gap into the
fixture instead of closing it. With no planner to brief the lens, the prose pointer
is a ritual the agent skips — so the run missed the Engelbart `system-improving-itself`
lens that was the on-the-nose fit for this work.

Decided direction:

1. **Extract a real `plan_retro_run.py` planner** by conceptually separating the
   classify/brief responsibility from `scaffold_retro_artifact.py`. Match the common
   planner shape so every skill has a uniform structure (plugin-user benefit). The
   planner emits the fitting counterfactual lens brief + `required_reads`, so the
   run reaches `expert-lens.md` at the point of need because a deterministic surface
   routed it there.
2. **Re-capture** to prove the planner-first retro flips the floor failed→proven.
3. **Change the claim-fidelity methodology** after the retro test: anchor RCF to
   planner `required_reads` / outcome assertions (not fidelity-to-current-shape),
   add an "also-ask-better-shape" lens.
4. **Roll the planner out** to hitl and the other planner-absent skills.

- thresholds.max_duration_ms intentionally NOT set: a failed-floor capture is not a
  clean baseline. The duration baseline is set from the PASSING re-capture.

## Cross-cutting implication

- All 20 fixtures were statically calibrated with ZERO live captures, against each
  skill's *current* shape. This first capture exposed that the methodology measures
  fidelity-to-current-shape and never asks whether the skill should have a better
  shape — so it silently blessed retro's missing planner. The remaining 19 fixtures
  (esp. planner-absent hitl) are unvalidated against this failure mode; the
  methodology change in step 3 addresses the class, not just retro.
