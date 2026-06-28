# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: live-capture validation of the claim-fidelity sweep.** All 20
  public-skill fixtures are statically calibrated and shipped (`v0.57.0`); no live
  captures have run. Per skill, ask before running: `plan_cautilus_proof.py` gate ->
  `run_cautilus_eval.py` -> confirm the observed packet opens the RCF docs (coverage
  >= `requiredCommandFragments`) -> set `thresholds.max_duration_ms` from the real run.
  A miss is a real signal: re-pin or re-classify the skill, never the matcher. Start
  with the cleanest single-floor skills (retro->expert-lens, ideation->concept-architecture,
  narrative->brief-shape, impl->verification-ladder).

## Current State

- **Per-skill claim-fidelity sweep COMPLETE and shipped in `v0.57.0`.** All 20 public
  skills calibrated, static only (reasoning + per-skill fresh-eye critique; no live
  captures); 25 scenario specs validate. The 8 calibration lenses, the Review Protocol,
  and the per-skill rationale live in the methodology spec + each commit message, not here.
- **Open follow-on:** broader ceal-dev consumer-name de-leak (WS-3a/3b). The portable
  surface is already clean (`007b6b0f`); 6 protected files retain `ceal` by design.

## Next Session

1. **Live-capture validation phase** (see Workflow Trigger). The first capture
   empirically closes the "tested the prompt?" gap and sets the first `thresholds`
   baseline; treat any RCF miss as a calibration signal, not a matcher to soften.
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
