# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Per-skill claim-fidelity sweep COMPLETE — all 20 public skills calibrated
  (static).** Pinned next task: **empirically validate via live `/charness:<skill>`
  captures** (ask-before-run, one at a time, per the Cautilus eval-only contract —
  consult `plan_cautilus_proof.py` first, use `run_cautilus_eval.py`) to confirm each
  calibrated prompt actually opens its RCF docs and to set `thresholds` baselines.
  Start with the cleanest single-floor skills (retro→expert-lens, ideation→concept-
  architecture, narrative→brief-shape, impl→verification-ladder). Method + lenses (now 8)
  live in the methodology spec `## Per-Skill RCF Calibration Lenses`.

## Current State

- **Schema evolved + all 20 skills calibrated, committed (static).** Validator accepts
  objective-carrying prompts (`startswith /charness:<skill>`) and multi-scenario
  fixtures (`(skill_id, scenario_id)`; default `spec.json`, branch `<scenario>.spec.json`).
  Per-skill commits `427f473f`, `33c591dd`, `4e99ff03`, `4aba39c1`, `8fb030ca`, `43d066a9`,
  `974dae10`, `168d856c`, `29260c26`, `bb715a88` (lens 8 + executable-subject re-pin),
  `88785945` (issue split), `429bf50e` (narrative), `7a550270` (release), `7fb51ac8` (retro),
  `c389d916` (spec). 25 scenario specs validate. No live captures run yet.
- **Shipped in `v0.57.0`** (2026-06-28, minor): the sweep + de-leak + fixes published to
  corca-ai/charness, distinct-channel verified (gh release isDraft:false, https-fetch 200);
  `charness update` refreshed the installed plugin 0.56.9 -> 0.57.0. See the
  [release critique](../charness-artifacts/critique/2026-06-28-release-claim-fidelity-sweep-critique.md).
  One release-gate fix folded en route: the find-skills/narrative adapter-echo dup-ratchet
  family was re-fingerprinted by the next_step add -> classified intentional in the
  [dup-review overlay](../charness-artifacts/quality/dup-review.json).
- **Method lives in the methodology spec + each commit, not inline.** The 8 calibration
  lenses and the Review Protocol are in the spec; per-skill rationale is in the commit
  messages — do not replay them here. Skill fixes shipped: find-skills `next_step`, gather
  provider-host redirect, handoff chunker bug, ideation + narrative point-of-need route;
  hitl/hotl/impl fixture-only; issue split new/resolve + release RCF 5->3 by planner reads (lens 1);
  impl/release/retro over-broad RCF cut to forced floors (lens 7). lens 8 (executable-subject) + the loop-step-6 critique check landed
  after the operator caught impl/hotl/ideation prompts carrying a run SHAPE with no concrete
  subject; debug stays a deliberate lens-5 capture-context non-claim.
- **CEAL portability deleak done** (`007b6b0f`): `ceal` -> generic `acme` across
  the live portable surface; only 6 protected files retain `ceal` (domain-blind
  guard, `slack.ceal-dev` examples, frozen logs). Broader ceal-dev consumer-name
  deleak stays the WS-3a/3b workstream.

## Next Session

1. **Live-capture validation phase** (the static sweep is done). Per skill, ask before
   running: `plan_cautilus_proof.py` gate → `run_cautilus_eval.py` → confirm the observed
   packet opens the RCF docs (coverage ≥ RCF) → set `thresholds.max_duration_ms` from the
   real run. A miss is a real signal: re-pin or re-classify the skill, not the matcher.
2. Secondary: support-skill claim-fidelity tier not started; quality pilot #397
   runtime-consultation proof still open (its own live capture).

## Discuss

- Keep the `referenceEngagement` annotation, or simplify fixtures to
  `prompt + requiredCommandFragments` only? Operator leaned minimal; spec mandates it.
- `nose v0.16.0` upgrade is advisory-available; bumping triggers a one-time
  lockstep dup-ratchet re-baseline (by design).

## References

- [claim-fidelity methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md) (lenses + schema)
- [claim-fidelity registry](../evals/cautilus/claim-fidelity-registry.json)
- [validator/lib](../scripts/claim_fidelity_lib.py) + [builder/matcher](../scripts/agent-runtime/build-skill-execution-observation.mjs)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
