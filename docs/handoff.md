# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Pinned next task: review/calibrate the per-skill claim-fidelity fixtures.**
  Start by reading the methodology spec + registry below, then go skill-by-skill.
  Carry edits through `impl`; run `critique` at closeout. Before mutating eval
  specs, read [implementation discipline](./conventions/implementation-discipline.md).

## Current State

- **20 per-skill claim-fidelity fixtures shipped (commit `247084fe`).**
  `evals/cautilus/<skill>-claim-fidelity/spec.json` for all 19 public skills +
  the pre-existing quality pilot, plus a registry (see References), the
  `validate-claim-fidelity-specs` standing gate, and a test. Authored statically;
  **no live captures run** (eval-only / ask-before-run is unchanged).
- **The mental model to start from (do not over-complicate):** a fixture is just
  (1) a `prompt` to run + (2) what the run's log must show. The ONLY active
  pass/fail matcher today is `requiredCommandFragments` (refs the tool-call log
  must show were opened). `requiredSummaryFragments` is `[]` and `thresholds` is
  unset everywhere. The `referenceEngagement` engage-always/on-demand/gate-sufficient
  classification is annotation/coverage, **not** pass/fail.

## Next Session

1. **Review each skill's `requiredCommandFragments`** (the real teeth). Wrong =
   a ref that will NOT always be opened (state/condition-dependent). Confirmed
   bug to fix: **setup** lists `greenfield-flow` in RCF, but `greenfield-flow`
   and `normalization-flow` are mutually exclusive (setup `SKILL.md` lines
   68-69, also 162-163) -> a partial-repo run fails it. Demote both flows to
   on-demand, drop `greenfield-flow` from RCF, fix its `fan_out_fit` (registry
   entry). Scan other conditional-flow skills for the same shape.
2. **Review each skill's `prompt`.** Most skills do NOT activate on a bare
   `/charness:<skill>`; they need a representative task prompt to exercise the
   real workflow. Expect most of the 20 to need realistic task context; only
   self-activators (e.g. `find-skills`) stay bare.
3. Secondary: spec `document-seams`/`impl-loop` are coverage-only over-generous
   (not RCF, low stakes); `thresholds` need per-skill baseline captures
   (ask-before-run, one at a time); support-skill tier not started; quality
   pilot #397 runtime-consultation proof still open.

## Discuss

- Keep the `referenceEngagement` annotation, or simplify fixtures to
  `prompt + requiredCommandFragments` (+ thresholds later)? Operator leaned
  toward minimal; methodology spec currently mandates the classification.
- `nose v0.16.0` upgrade is advisory-available; bumping regroups families and
  triggers a one-time lockstep re-baseline (by design, not a defect).

## References

- [claim-fidelity methodology spec](../charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md)
- [claim-fidelity registry](../evals/cautilus/claim-fidelity-registry.json)
- [evals README — claim-fidelity section](../evals/README.md)
- [validator](../scripts/validate_claim_fidelity_specs.py) + [builder/matcher](../scripts/agent-runtime/build-skill-execution-observation.mjs)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
