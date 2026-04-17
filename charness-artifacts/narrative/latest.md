# Narrative Review
Date: 2026-04-17

## Source Map

- `README.md`
- `INSTALL.md`
- `UNINSTALL.md`
- `docs/control-plane.md`
- `docs/public-skill-validation.md`
- `docs/operator-acceptance.md`
- `docs/host-packaging.md`
- `docs/handoff.md`
- `charness-artifacts/quality/latest.md`

## Narrative Drift

- The core story is aligned: `charness` is a portable harness bundle, the
  managed install contract goes through `charness init`, and root-level host
  packaging artifacts remain generated surfaces instead of source-of-truth
  policy.
- README is intentionally short and now points evaluators more directly at the
  rollout-readiness and install-verification documents. That improves the
  first-touch path for internal developers without turning README into a second
  install manual.
- The honest remaining gap is not “basic docs are missing” but “the repo still
  carries explicit operator acceptance work.” `docs/operator-acceptance.md`
  still keeps managed CLI install experiments as an open item, and
  `docs/host-packaging.md` still frames public GitHub install as a testable
  hypothesis rather than a fully proven guarantee.

## Updated Truth

- No broad truth-surface rewrite was needed.
- Current honest position: the repo is internally dogfoodable and locally
  verifiable today, but rollout confidence is strongest when framed as
  “managed install plus post-install verification” rather than “fully proven
  zero-touch host rollout on every machine posture.”

## Brief

### One-Line Summary

`charness` looks ready for internal developer rollout when the expectation is a
documented managed install plus explicit verification, not a fully proven
hands-off host rollout on every posture.

### Current Contract

- README is the entrypoint.
- `INSTALL.md` owns the managed install contract.
- `docs/host-packaging.md` owns generated host-surface rules.
- `docs/operator-acceptance.md` owns remaining operator proof work.
- `./scripts/run-quality.sh` is the standing local quality bar.

### What Changed

- Added a short README routing block for rollout-readiness and install-verifier
  readers.
- Recorded this narrative assessment in the canonical narrative artifact path.

### Open Questions

- Should internal rollout mean “self-serve from README plus linked docs” or
  “maintainer-guided managed install with verification”?
- Should one remaining managed-install acceptance rerun be elevated into a
  release-blocking ritual, or stay as an on-demand operator proof?

## Claim Audit

- Claim: the current tree is locally healthy.
  Evidence: `./scripts/run-quality.sh` passed on 2026-04-17 with `38 passed,
  0 failed`.
- Claim: the repo has a current release/install story, not only local dev
  guidance.
  Evidence: `docs/handoff.md` records published `0.3.0`, and `INSTALL.md`
  treats `charness init` as the canonical operator bootstrap.
- Claim: the managed host story is not fully “done forever.”
  Evidence: `docs/operator-acceptance.md` still keeps managed CLI install
  experiments as an active remaining item, and `docs/host-packaging.md` keeps
  public GitHub install under hypothesis language.
- Claim: README is sufficient as an orienter, but not as the sole rollout
  decision document.
  Evidence: rollout confidence still depends on the linked install, packaging,
  acceptance, and quality surfaces.

## Compression

- README remains compressed enough to stay an orienter.
- The rollout/readiness decision still depends on a small linked packet rather
  than a single document: README, INSTALL, host packaging, operator
  acceptance, and latest quality review.

## Open Questions

- Do we want a dedicated “internal rollout checklist” surface, or is the
  current README routing plus operator-acceptance doc enough?
- Do we want one explicit fresh-machine Codex proof recorded before calling the
  internal rollout story “high confidence”?

## Next Step

1. Run one fresh-machine or clean-profile managed install proof for Codex with
   `charness init`, `charness doctor`, and `charness update`.
2. Record the exact host-visible result in `docs/operator-acceptance.md` or a
   linked artifact.
3. If that proof is clean, treat the repo as ready for broader internal
   developer distribution.
