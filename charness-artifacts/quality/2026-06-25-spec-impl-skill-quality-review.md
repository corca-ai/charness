# Quality Review
Date: 2026-06-25

## Scope

Target boundary: `spec` and `impl` public skill quality, especially
progressive disclosure, helper ownership, target-vs-ambient classification, and
consumer dogfood pressure.

Ambient repo findings: broad quality passed. The doc-duplicate advisory between
`hitl` and `narrative`, and Python length warn-band files from the broad gate,
are not `spec` or `impl` target findings.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed 79/79.
- Target-only ergonomics inventory scanned `spec` with `core_nonempty_lines=139`,
  `reference_file_count=16`, `script_file_count=0`, and zero heuristic findings.
- Target-only ergonomics inventory scanned `impl` with
  `core_nonempty_lines=145`, `reference_file_count=8`, `script_file_count=7`,
  and one host-surface advisory class: five `.codex` / Codex-skill lookup hits.
- Public-skill dogfood suggestions exist for both targets, but both are
  `evaluator-required`; this pass did not run live evaluator proof.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 41.4s latest / 65.7s median, budget
  90.0s; `pytest` 25.1s latest / 25.1s median, budget 140.0s; `check-coverage`
  19.1s latest / 19.5s median, budget 55.0s; `check-duplicates` 10.0s latest /
  11.9s median, unbudgeted.
- coverage gate: broad read-only quality passed.
- evaluator depth: deterministic gates plus bounded fresh-eye review only;
  Cautilus was not run because `plan_cautilus_proof.py` returned
  `next_action: "none"` and no explicit log-backed behavior source was in scope.

## Healthy

- `spec` has an honest trigger boundary: turn a concept into a living
  implementation contract before code churn spreads.
- `spec` core owns selection and sequencing; references deepen contract modes,
  ambiguity handling, acceptance, evidence durability, and the `impl` loop
  without becoming a second workflow.
- `impl` has an honest downstream boundary: implement the smallest meaningful
  slice, verify against the contract, and synchronize the contract when reality
  changes.
- `impl` already owns the helper-shaped pieces that should be code, not prose:
  adapter resolution, adapter initialization, and verification survey.

## Weak

- Consumer dogfood is shaped correctly but not proven here. The `spec` and
  `impl` prompts pressure real consumer behavior, but their declared tier is
  `evaluator-required`, and this pass had no allowed evaluator run.
- `spec` has zero heuristic findings, but that is scanner quiet, not proof of
  health. The main risk is behavioral judgment quality, which needs prose review
  and eventual evaluator-backed dogfood.

## Missing

- No missing target-skill helper, split, merge, or deterministic gate is
  justified by this pass.

## Deferred

- Do not run Cautilus for this generic quality review without a concrete
  behavior log, failing prompt, transcript, issue log, or regression log.
- Do not add a `spec` planner now; the target's shaping work is judgment-heavy,
  and a planner would likely overfit before a repeated ordering failure exists.

## Advisory

- structural review result: target findings are advisory only. Command:
  `plan_quality_run.py --target-skill spec` and
  `plan_quality_run.py --target-skill impl`. `spec` asks the model to shape a
  contract from repo truth, which is not currently a helper-owned packet. `impl`
  already has adapter and verification survey helpers. No reference in either
  target became a competing workflow.
- prose review result: both target cores own selection and sequencing. Command:
  target SKILL/reference read plus bounded reviewer
  `019efd32-57bc-7123-bcb1-eff03a2a2f3a`. The target references deepen chosen
  phases. `impl` host-surface hits are intentional compatibility and
  installed-skill lookup seams, not immediate portability debt, but they should
  remain visible in future reviews.
- command: `inventory_skill_ergonomics.py --skill-path skills/public/spec --json`;
  interpretation: zero heuristic findings satisfy no structural pressure signal
  only, so prose review above is the health claim.
- command: `inventory_skill_ergonomics.py --skill-path skills/public/impl --json`;
  interpretation: `host_surface_reference=5` is a target advisory watch item,
  not a current repair, because `.agents` is canonical and `.codex` / `.claude`
  are compatibility fallbacks.
- command: `./scripts/run-quality.sh --read-only`; broad-gate interpretation:
  the `hitl` / `narrative` doc duplicate advisory is ambient and should not be
  charged to the `spec` or `impl` targets.
- artifact: `docs/handoff.md`; scenario review result: a pickup that follows
  "START HERE" still chooses dogfood mode first, while a pickup that continues
  #401 no longer repeats `spec` / `impl` quality and instead sees
  evaluator-backed dogfood as the remaining behavior-proof lane.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019efd32-57bc-7123-bcb1-eff03a2a2f3a` found no blocking target-skill issue,
  classified the `impl` host references as intentional advisory hits, and
  confirmed the doc-duplicate advisory as ambient.
- Slow-gate lenses: fixture-economics, parallel-critical-path, and
  duplicated-proof were not re-delegated because this pass did not redesign slow
  gates; runtime data is reported as existing evidence only.

## Commands Run

- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/resolve_quality_artifact.py --repo-root . --intent current`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill spec --json`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill impl --json`
- `./scripts/run-quality.sh --read-only`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --skill-path skills/public/spec --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --skill-path skills/public/impl --json`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id spec`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id impl`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- scenario review readback of `docs/handoff.md` truth-surface edit

## Recommended Next Gates

- active none for `spec` / `impl` target skills — no delete, merge, split,
  helper, or interface-narrowing gate is justified by this pass.
- passive keep the `impl` host-surface hits visible until a portability failure
  or repeated consumer confusion shows they need a structural repair.
- passive keep evaluator-backed dogfood for both target skills visible because
  the current suggestions pressure real behavior but this pass did not include
  an allowed behavior-source log.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
