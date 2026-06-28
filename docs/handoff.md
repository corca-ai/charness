# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: resume the per-skill claim-fidelity fixture review at
  `15/20 narrative`.** Go skill-by-skill applying the calibration lenses
  (methodology spec `## Per-Skill RCF Calibration Lenses`, now 8) AND the
  `## Per-Skill Review Protocol` (also-fix-the-skill, north-star-over-prose-teeth,
  less-but-better) in order; carry edits through `impl`; run `critique` before each
  commit.

## Current State

- **Schema evolved + skills 1-14 calibrated, committed.** Validator accepts
  objective-carrying prompts (`startswith /charness:<skill>`) and multi-scenario
  fixtures (`(skill_id, scenario_id)`; default `spec.json`, branch `<scenario>.spec.json`).
  Commits `427f473f`, `33c591dd`, `4e99ff03`, `4aba39c1`, `8fb030ca`, `43d066a9`,
  `974dae10`, `168d856c`, `29260c26`, `bb715a88` (lens 8 + executable-subject re-pin),
  `88785945` (issue new/resolve split). 25 scenario specs validate.
- **Method lives in the methodology spec + each commit, not inline.** The 8 calibration
  lenses and the Review Protocol are in the spec; per-skill rationale is in the commit
  messages — do not replay them here. Skill fixes shipped: find-skills `next_step`, gather
  provider-host redirect, handoff chunker bug, ideation point-of-need route; hitl/hotl/impl
  were fixture-only. lens 8 (executable-subject) + the loop-step-6 critique check landed
  after the operator caught impl/hotl/ideation prompts carrying a run SHAPE with no concrete
  subject; debug stays a deliberate lens-5 capture-context non-claim.
- **CEAL portability deleak done** (`007b6b0f`): `ceal` -> generic `acme` across
  the live portable surface; only 6 protected files retain `ceal` (domain-blind
  guard, `slack.ceal-dev` examples, frozen logs). Broader ceal-dev consumer-name
  deleak stays the WS-3a/3b workstream.

## Next Session

1. **Resume at `15/20 narrative`**, then registry order, **skipping setup (already
   split), quality (the pilot), find-skills + gather + handoff + hitl + hotl + ideation + impl + issue (done)**. For each skill: check
   for a deterministic planner / required-reads script FIRST (lens 1), then
   bare-vs-pin (2), script-resolved demotions (3), multi-fixture splits (4), and
   script-briefs-judge (7) — and run the Review Protocol (fix the skill, not just
   the fixture).
2. Secondary: support-skill tier not started; quality pilot #397 runtime-
   consultation proof open; `thresholds` need per-skill baseline captures
   (ask-before-run, one at a time).

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
