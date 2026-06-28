# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: resume the per-skill claim-fidelity fixture review at
  `12/20 ideation`.** Go skill-by-skill applying the calibration lenses
  (methodology spec `## Per-Skill RCF Calibration Lenses`, now 7) AND the
  `## Per-Skill Review Protocol` (also-fix-the-skill, north-star-over-prose-teeth,
  less-but-better) in order; carry edits through `impl`; run `critique` before each
  commit.

## Current State

- **Schema evolved + skills 1-11 calibrated, committed.** Validator accepts
  objective-carrying prompts (`startswith /charness:<skill>`) and multi-scenario
  fixtures per skill (`(skill_id, scenario_id)`; default `spec.json`, branch
  `<scenario>.spec.json`). Commits `427f473f` (schema+achieve+setup), `33c591dd`
  (announcement/create-cli/create-skill/critique/debug), `4e99ff03` (find-skills),
  `4aba39c1` (gather), `8fb030ca` (handoff), `43d066a9` (hitl), `974dae10` (hotl).
  24 scenario specs validate.
- **Method + lessons live in the methodology spec, not inline.** See the spec's
  `## Per-Skill RCF Calibration Lenses` (now 7: lens 1 planner-ground-truth caught
  debug, gather, AND handoff RCF inverted/over-broad vs their planners; lens 7
  script-briefs-judge) and `## Per-Skill Review Protocol`. Skill fixes shipped with
  the fixtures: find-skills `next_step`, gather provider-host redirect, and handoff's
  chunker bug (plugin-namespaced `/charness:handoff` was bypassing chunked routing) —
  each critique-checked. handoff also split into 3 intent scenarios (lens 4). hitl and
  hotl were fixture-only (no planner; RCF via script-resolution): hitl → single
  chunk-contract.md; hotl demoted adapter-contract.md (resolve_adapter.py-resolved, same
  as hitl) → RCF [proof-rules.md, ledger-and-dispositions.md] + bare→pinned closeout (lens 2).
- **CEAL portability deleak done** (`007b6b0f`): `ceal` -> generic `acme` across
  the live portable surface; only 6 protected files retain `ceal` (domain-blind
  guard, `slack.ceal-dev` examples, frozen logs). Broader ceal-dev consumer-name
  deleak stays the WS-3a/3b workstream.

## Next Session

1. **Resume at `12/20 ideation`**, then registry order, **skipping setup (already
   split), quality (the pilot), find-skills + gather + handoff + hitl + hotl (done)**. For each skill: check
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
