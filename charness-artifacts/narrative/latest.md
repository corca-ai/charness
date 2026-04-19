# Narrative Review
Date: 2026-04-17

## Source Map

- `README.md`
- `https://github.com/corca-ai/cautilus/blob/main/README.md`
- `docs/support-skill-policy.md`
- `docs/public-skill-validation.md`
- `docs/operator-acceptance.md`
- `docs/host-packaging.md`
- `docs/deferred-decisions.md`
- `docs/handoff.md`
- `charness-artifacts/quality/latest.md`

## Narrative Drift

- The core contract was already honest, but the first-touch README led with
  structure instead of choice. A maintainer could learn what `charness` owns
  without quickly learning who it is for, what problem shape it fits, or how
  it differs from neighboring harnesses such as `cautilus`.
- Compared with the public `cautilus` README, the missing front-door pieces
  were:
  reader targeting, day-1 trigger, short contrast-based philosophy, and a
  visible “what to use when” map.
- The real narrative gap was not install truth. It was product-shape truth.
  `charness` already had the philosophy in supporting docs: public workflow
  concepts vs support tool knowledge, deterministic gates in-repo, evaluator
  work out of core, and host policy in adapters rather than in public skills.
  README simply did not surface that framing early enough.

## Updated Truth

- README now makes the intended reader, product boundary, and skill-routing
  model visible before install and packaging details.
- Current honest position: `charness` is the portable workflow-and-operator
  harness. It is not the behavior-eval product. If the repo needs workflow
  concepts and portable operating seams, use `charness`. If the repo needs
  evaluator-driven behavior protection, use `cautilus` or an explicit HITL /
  evaluation loop.

## Brief

### One-Line Summary

`charness` now reads more like a product entrypoint and less like a packaging
inventory: who it is for, why it exists, how it differs, and what skill to
reach for are all visible near the top.

### Current Contract

- README is the entrypoint and decision orienter.
- `INSTALL.md` and `docs/host-packaging.md` still own install and packaging
  truth.
- `docs/support-skill-policy.md` and
  `docs/public-skill-validation.md` remain the deeper boundary docs behind the
  new README framing.
- `./scripts/run-quality.sh` remains the standing local proof bar.

### What Changed

- Added `Who It Is For`, `Why charness`, and `What To Use When` near the top of
  README.
- Added a small surface-classification block so readers can tell public skills,
  support skills, and integration manifests apart.
- Added one concrete multi-skill workflow so the harness reads as an execution
  path, not only as a catalog.
- Added one bootstrap workflow so partially initialized repos also have a clear
  first move.
- Kept install and packaging material intact, but moved reader guidance ahead
  of operational detail.

### Open Questions

- Should the public skill map stay intent-grouped, or should one future doc own
  a full scenario catalog similar to `cautilus` archetypes?
- Are two examples enough, or is there still one missing high-frequency path
  that users cannot infer from the current README?

## Claim Audit

- Claim: the repo is locally healthy after the rewrite.
  Evidence: `./scripts/run-quality.sh` passed on 2026-04-17 with `38 passed,
  0 failed`.
- Claim: the new README framing is grounded in existing source-of-truth docs,
  not fresh invention.
  Evidence: `docs/support-skill-policy.md` defines public workflow concepts vs
  support tool knowledge; `docs/deferred-decisions.md` keeps evaluator-heavy
  work out of `charness`; `docs/public-skill-validation.md` fixes current skill
  validation posture.
- Claim: README now shows an actual charness-shaped path, not only sectioned
  philosophy.
  Evidence: the new concrete workflow maps one common maintainer journey across
  `ideation`, `spec`, `impl`, `quality`, and `handoff`, with `init-repo` and
  `cautilus` called out as neighboring boundaries.
- Claim: README now covers both “shape new work” and “make the repo operable”
  entry paths.
  Evidence: the bootstrap workflow maps `init-repo`, `narrative`, `quality`,
  and `handoff` into a second bounded path for thin or uneven repos.
- Claim: `charness` is ready to be described as internally roll-outable.
  Evidence: the user confirmed the managed install proof and update-propagation
  proof are already complete, and the repo still carries passing local quality
  proof.
- Claim: install truth still should not collapse back into README.
  Evidence: `docs/operator-acceptance.md`, `INSTALL.md`, and
  `docs/host-packaging.md` remain the correct homes for rollout and packaging
  detail.

## Compression

- README gained new high-leverage product-shape sections instead of only more
  install detail.
- The change is a real narrative restructure because the top of the document
  now answers reader-selection questions before ownership and packaging
  inventory.

## Open Questions

- Do we want a separate “workflow examples” doc that gives one concrete path
  per major public skill cluster?
- If we keep README compact, should it stop at these two examples and push any
  further scenario expansion into a separate doc?

## Next Step

1. Re-read README from the perspective of a new internal maintainer who does
   not already know the `charness` / `cautilus` split.
2. Treat these two workflows as the README ceiling unless a repeated confusion
   shows a third path is load-bearing.
3. Keep install, packaging, and acceptance details in their owner docs instead
   of re-growing README into a second operator manual.
