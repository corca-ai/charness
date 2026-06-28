# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: resume the per-skill claim-fidelity fixture review at
  `8/20 gather`.** Go skill-by-skill applying the calibration lenses
  (methodology spec `## Per-Skill RCF Calibration Lenses`, now 7) AND the
  `## Per-Skill Review Protocol` (also-fix-the-skill, north-star-over-prose-teeth,
  less-but-better) in order; carry edits through `impl`; run `critique` before each
  commit.

## Current State

- **Schema evolved + skills 1-7 calibrated, committed.** The validator now
  accepts objective-carrying prompts
  (`startswith /charness:<skill>`) and multiple scenario fixtures per skill
  (`(skill_id, scenario_id)` uniqueness; default = `spec.json`, named branch =
  `<scenario>.spec.json`). Commits `427f473f` (schema + achieve + setup split),
  `33c591dd` (announcement/create-cli/create-skill/critique/debug), `4e99ff03`
  (find-skills). 22 scenario specs validate.
- **find-skills (7) set the script-briefs-judge pattern.** Its bare default is a
  script-resolved inventory dump, so the prompt is pinned to a cross-layer routing
  objective and RCF is the single `discovery-order.md`. The skill fix:
  `list_capabilities.py` now emits an active `next_step` that routes the judge to
  answer the ranking-interpretation question (north star over prose). Critique also
  closed a sibling leak — `recommendation_interpretation` no longer rides the
  canonical inventory artifact.
- **Calibration method lives in the methodology spec section**
  `## Per-Skill RCF Calibration Lenses` (+ `## Per-Skill Review Protocol`), not
  inline. Key find: debug's RCF was inverted vs its own deterministic planner
  (`plan_debug_run.py`) — fixed.
- **CEAL portability deleak done** (`007b6b0f`): `ceal` -> generic `acme` across
  the live portable surface; only 6 protected files retain `ceal` (domain-blind
  guard, `slack.ceal-dev` examples, frozen logs). Broader ceal-dev consumer-name
  deleak stays the WS-3a/3b workstream.

## Next Session

1. **Resume at `8/20 gather`**, then registry order, **skipping setup (already
   split), quality (the pilot), and find-skills (done)**. For each skill: check for
   a deterministic planner / required-reads script FIRST (lens 1), then bare-vs-pin
   (2), script-resolved demotions (3), multi-fixture splits (4), and
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
