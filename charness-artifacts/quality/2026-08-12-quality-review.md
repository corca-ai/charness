# Quality Review
Date: 2026-08-12
Title: Release-Unblocking Lesson Index Regeneration

## Scope

Target boundary: the checked-in retro lesson-selection index used by preview and
validation surfaces during release readiness.

Ambient repo findings: hosted CI/public release readback, existing skill
ergonomics advisories, and product behavior are outside this generated-artifact
repair.

## Surface Contract Review

- semantic coverage: `not-in-scope` — no user-facing behavior or target-skill
  contract changed; this slice restores a generated projection to its source.
- surface: retro lesson text, its checked-in selection index, preview tests, and
  the quality validator.
- owner: `scripts/build_retro_lesson_selection_index.py` owns index rendering;
  `check_lesson_selection_index.py` owns drift detection.
- projections: `charness-artifacts/retro/lesson-selection-index.json` and the
  lesson-selection preview.
- state scope: current local repository snapshot.
- transitions: stale generated index → regenerated index → byte-level check and
  preview/quality proof.
- proof boundary: generator `--check`, six preview tests, fresh-eye review, and
  the full read-only quality gate.
- unexamined axes: hosted execution and the later publish/public readback.

## Current Gates

- `build_retro_lesson_selection_index.py --check` accepts the regenerated index.
- `pytest -q tests/test_lesson_selection_preview.py` closes at 6 passed.
- `./scripts/run-quality.sh --read-only` closes at 90 passed, 0 failed in
  91.1s; remaining output is advisory-only.
- Existing `validate-retro-lesson-index` is in the broad gate and directly
  detects future source/index drift.

## Runtime Signals

- runtime source: structured local metrics in
  `.charness/quality/runtime-signals.json`, rendered by
  `render_runtime_summary.py`.
- runtime hot spots: `run-quality-read-only` latest 91.2s / median 87.5s,
  budget 420.0s; `pytest` latest 72.5s / median 69.7s, budget 97.5s.
- coverage gate: no production or verdict logic changed; generated-artifact
  freshness is directly proven by the existing validator and preview tests.
- evaluator depth: deterministic local gates only; Cautilus was not requested
  and adds no proof for generated-text/index identity.

## Healthy

- The repair changes only four rendered index lines, including the derivative
  candidate key, to match the already-corrected retro source.
- A separate fresh-eye reviewer independently classified this as source/index
  drift, found regeneration to be the smallest correct repair, and found no
  release blocker.
- The same broad gate that caught the stale index proves recurrence detection;
  no new gate is needed to make a claim that the existing one already supports.

## Weak

- The index can drift when retro prose is edited without its generator being run;
  the current release attempt exposed that workflow gap, though the committed
  validator catches it before publication.

## Missing

- No hosted CI or public release readback exists yet for this repair; those are
  release-boundary proofs, not local quality claims.

## Deferred

- Test/production ratio, warn-band files, document near-duplicates, and
  plugin-version-skew observations remain advisory because they do not explain
  this failed release gate or invalidate its corrected rerun.

## Advisory

- structural review result: command: `build_retro_lesson_selection_index.py --check`;
  `not-in-scope` for a one-file generated projection whose direct
  generator/validator ownership is already explicit.
- prose review result: artifact: delegated-review record in this file; the reviewer
  checked the changed lesson wording against the retro source, and found no
  trigger, progressive-disclosure, or judgment-only skill change in this slice.
- ergonomics inventory command: `inventory_skill_ergonomics.py --summary`
  reports 16 heuristic-bearing skills, exclusively host-surface-reference hits;
  it requires a later dedicated prose review, not a release-blocking claim here.

## Delegated Review

- Executed — bounded read-only fresh-eye review confirmed the root cause,
  repair minimality, existing recurrence detection, and absence of a
  release-readiness blocker. Reviewer boundary fingerprint verification was
  clean.

## Commands Run

- `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write`
  — regenerated the checked-in projection.
- `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check`
  — passed.
- `pytest -q tests/test_lesson_selection_preview.py` — 6 passed.
- `./scripts/run-quality.sh --read-only > /tmp/charness-quality-after-index.log
  2>&1` — 90 passed, 0 failed, 91.1s.
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root .
  --detail` and `inventory_skill_ergonomics.py --summary` — runtime and
  advisory evidence captured for this record.

## Recommended Next Quality Moves

- active release preflight — capability_needed=publish only from a green local
  state; next_center=release helper; transformation=commit this regeneration and
  execute its release gate; proof_boundary=green release gate plus hosted/public
  readback; enforcement_posture=existing-gate-reuse.
- passive no new index floor — because the standing validator caught this defect;
  capability_needed=recurrence detection;
  next_center=retro index; transformation=keep the existing validator in the
  broad gate; proof_boundary=validator fails on drift; enforcement_posture=no-new-gate
  because a second overlapping floor would add ritual without a new escape path.

## History

- [Previous quality review](./history/2026-07-03-pytest-suite-test-value-audit.md)
