# Quality Review
Date: 2026-07-11
Title: 0.66.2 full-carrier release readiness

## Scope

Target boundary: the complete `v0.66.1..HEAD` delta for patch release 0.66.2:
eleven post-tag commits already on origin plus twenty-five unpushed commits,
including five new north-star slices.

Ambient repo findings: no ambient gate failure was folded into the release.
Issue #433 remains an open external boundary and is not a release-close target.

## Current Gates

Per-slice focused tests, repo surface closeout, pre-commit hooks, packaging
parity, public-skill validators, and fresh-eye critique passed. The final locked
full-carrier closeout and release-owned `--release` gate remain publish
preconditions, not claims already made by this readiness record.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: pytest 35.8s latest / 35.7s median against 140s budget; coverage 7.5s / 7.4s against 55s; markdown 5.6s / 5.4s against 11s; secrets 5.2s / 5.2s against 6s.
- coverage gate: focused and pre-lock surface proof passed; final changed-line producer runs after release critique and mutation lock.
- evaluator depth: deterministic gates and distinct fresh-eye reviews only; Cautilus stayed ask-before-run because no explicit log-backed behavior request existed.

## Healthy

- Quality scaffold direct, CLI, and exported-plugin paths execute the real validator.
- Explicit closeout campaign bases now resolve once and feed range, broad, and focused coverage consumers.
- Release-linked issue closeout now assembles a final-consumer-valid carrier;
  the corrected conditional inputs repair a path whose prior output was rejected.
- Parser extraction restored `run_slice_closeout.py` headroom from 4 to 80 code lines with CLI metadata parity.
- Nose 0.18.0 is ready on the real host; doctor reported `ready`, installer
  dry-run resolved the upstream v0.18.0 release asset, sync-support reported no
  support-skill source, and the advisory clone inventory displayed 3 families /
  111 duplicated lines without promoting them to failures.

## Weak

- The stored aggregate `run-quality-read-only` timing sample is 25 days old; current per-phase runtime samples are available, but this artifact does not claim a new aggregate trend.

## Missing

- None found by the structural-waste, CLI-ergonomics, brittle-source-guard, packaging, or focused behavior inventories.

## Deferred

- Seven low-confidence dead-code review candidates remain after dataclass-field noise was removed; reviewed intentional vocabulary and dynamic helper entries are not deletion targets without stronger consumer evidence.
- Fresh-install proof is not planned for this patch; existing-install refresh and fresh-checkout probes are distinct claims.

## Advisory

- artifact: structural review result: the active goal and five slice critiques selected producer fixes, one proven deletion, one internal ownership split, and one advisory classifier improvement; they rejected new floors and inventory-score chasing.
- command: prose review result: `inventory_skill_ergonomics.py --summary` reports 85 host-reference lexical hits in adapter/integration/detector contexts already reviewed in the prior carrier; zero are unresolved portable-prose debt.
- command: `inventory_nose_clones.py` found three displayed clone families / 111 duplicated lines; its own contract classifies them as advisory refactoring candidates, not standing failures, and no family was admitted without a separate ownership case.

## Delegated Review

- Delegated Review: executed — five implementation slices received distinct fresh-eye reviews; all act-before-ship findings were cleared and rail-1 worktree/index verification reported zero drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): reviewed through runtime summary and structural-waste inventory; no proof was moved off the local path and final broad proof remains required.

## Commands Run

`plan_quality_run.py`; focused pytest suites (24, 78, 17, 38, and 12 tests);
`run_slice_closeout.py --skip-broad-pytest` per slice; skill/packaging/markdown/
secret/ruff gates; skill, structural-waste, CLI, brittle-guard, runtime, dead-code,
and nose-clone inventories; real-host nose doctor/install-dry-run/sync-support.

## Recommended Next Quality Moves

- active release-proof-lock — capability_needed=publish the full carrier without a range or install-proof false claim; next_center=locked full-carrier closeout and release helper; transformation=run the changed-line producer, release critique, dry-run, execute, and distinct public readback; proof_boundary=public v0.66.2 content plus installed-version readback; enforcement_posture=existing-gate-reuse.
- passive dead-code-vocabulary-classification — capability_needed=smaller recurring review queue; next_center=dynamic/intentional constant evidence; transformation=defer until a general structural owner signal exists because exact-name exemptions would hide future drift; proof_boundary=repeated finding with machine-readable ownership; enforcement_posture=no-gate because current evidence is judgment-only.

## History

- [Archived quality review](history/2026-06-16-quality-review.md)
