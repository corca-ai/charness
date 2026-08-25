# Quality Review
Date: 2026-08-25
Title: Critique/debug evidence skill review

## Scope

Target boundary: public `critique` and `debug` skills, their evidence-led producers/validators, source/plugin parity, and release readiness. Ambient findings are recorded separately and are not treated as skill blockers unless they invalidate this boundary.

## Surface Contract Review

- semantic coverage: `observed` — the artifact producer, validator, planner, and final-consumer receipt path were exercised.
- surface: `skills/public/{critique,debug}`, `scripts/adversarial_evidence.py`, validators, planners, and exported plugin mirrors.
- owner: skill contracts own schema and trigger routing; validators own verdicts; release owns publication claims.
- projections: Markdown artifacts, YAML scaffold payloads, validator commands, and plugin copies.
- state scope: evidence-led mode only plus compatibility of default mode; no live host installation state.
- transitions: scaffold → receipt-bound artifact → validator → closeout/release evidence.
- proof boundary: local deterministic tests and readback; no live Codex/Claude host roundtrip claim.
- unexamined axes: live host adapter behavior, authenticated public release readback, and Cautilus evaluator depth.

## Current Gates

`validate_skills.py`, `check_skill_contracts.py`, source/plugin parity, focused evidence/planner/scaffold tests, and fresh-checkout probes passed. `check_dup_ratchet.py` is green after reviewing six intentional symmetry families; it still reports ambient lineage advisories.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: `run-quality-full-release` 199.5s latest / 180.1s median (365.5s budget); `pytest-release` 176.3s / 157.9s (300s); `run-quality-read-only` 168.9s / 166.3s (420s).
- coverage gate: focused repaired-surface suite 84 passed; the broad read-only run had 96 passed and three ambient failures (shellcheck advisory, cumulative mutation-line coverage, and duplicate-ratchet before the reviewed overlay).
- evaluator depth: deterministic gates only; no live Cautilus run was requested or needed to establish this local contract.

## Healthy

- Reproduced/disconfirmed records now require an existing repo-relative receipt, matching SHA-256, executable fixture/roundtrip metadata, and final-consumer observation; fabricated prose no longer passes.
- `--evidence-led` propagates from critique/debug scaffold and debug planner into the emitted validator command and evidence sections. Default invocations remain compatible.
- Debug routing retains compatibility/prompt-surface/public-skill/validator critique triggers and the `host-disproves-local` handoff trigger.

## Weak

- Heuristic ergonomics reports 15 findings, mostly intentional host-surface references and argparse-help observations; this needs prose judgment rather than automatic cleanup.
- Runtime samples for several older labels are stale, so cost conclusions are local and advisory.

## Missing

- Live Codex/Claude host roundtrip and authenticated GitHub/public release readback are unproven in this local review.

## Deferred

- Re-run the full broad quality gate after the final release commit to separate the cumulative mutation-coverage baseline from this slice.

## Advisory

- structural review result: `structural_review_packet=executed`; planner selected skill-ergonomics and deterministic quality gates. Evidence: `command: python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`.
- prose review result: trigger boundaries, progressive disclosure, helper ownership, dogfood pressure, and target-vs-ambient split were reviewed; evidence sections are opt-in, receipt validation is fail-closed, and shared mechanics remain in `scaffold_artifact_lib`.
- `inventory_skill_ergonomics.py --summary` found 15 heuristic findings and explicitly requires this prose disposition; no unreviewed target-skill ergonomics blocker remains.

## Delegated Review

- Delegated Review: executed — bounded runtime reviewer approved current behavior; artifact reviewer and counterweight reviewer supplied the receipt/scaffold/routing blockers that this repair addressed. The required second proof-surface round is pending final post-repair readback.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): re-delegated through the bounded counterweight review; no slow-gate change was proposed.

## Commands Run

- `python3 tests/test_adversarial_evidence.py` equivalent focused suite: 84 passed.
- `python3 scripts/validate_skills.py --repo-root .`; `python3 scripts/check_skill_contracts.py --repo-root .`: passed.
- `python3 skills/public/release/scripts/check_fresh_checkout_probes.py --repo-root . --run-probes --detail`: five probes passed.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root .`: exit 0; only ambient lineage/reduction advisories remain.

## Recommended Next Quality Moves

- active — capability_needed=live host adapter; next_center=runtime proof; transformation=run Codex/Claude host roundtrip for evidence-led critique/debug; proof_boundary=distinct host readback; enforcement_posture=advisory.
- passive — capability_needed=runtime samples; next_center=stale-label refresh; transformation=record current duplicate/portability timings; proof_boundary=structured runtime signals; enforcement_posture=no-gate because the labels are outside this slice and no current failure is established.

## History

- [2026-08-18 quality review](history/2026-08-18-quality-review.md)
