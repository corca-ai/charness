# Quality Review
Date: 2026-08-06
Title: Runtime evidence and installed-host nose boundary

## Scope

Target boundary: the retained runtime phase-isolation evidence and the
manifest-supported installed-host `nose` lifecycle for the active goal.

Ambient repo findings: provider freshness, remote CI, release publication,
issue state, and cross-host runtime behavior remain outside this proof packet.

## Surface Contract Review
- semantic coverage: `partial` — the local runtime and installed-host lifecycle are observed, while external and cross-host claims remain unexamined.
- surface: retained runtime phase-isolation evidence and installed-host `nose` lifecycle
- owner: the quality run receipt and `.agents/release-adapter.yaml` installation probes own this packet; product/runtime providers do not.
- projections: `.charness/quality/runtime-signals.json`, the dated proof packet, installer/doctor output, and the quality artifact
  <!-- reproduction-source -->
- state scope: per-run local host and installed version
- transitions: pre-install readiness, supported install, post-install doctor, and current-pointer reconciliation
- proof boundary: focused runner/aggregate suite plus installer/doctor readback and bounded reviewer
- unexamined axes: cross-host runtime cohort, provider roundtrip, live-agent observation, remote CI, release parity, and source/install commit parity

## Current Gates

- The focused runner/aggregate behavior suite passed 54 tests.
- The docs/artifact slice closeout passed its changed-surface checks, including
  links, command docs, spec-evidence durability, Markdown, secrets, and the
  browser-runtime hygiene check.
- The source/plugin staged-mirror check passed; no source or validator surface
  changed in this goal.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: the retained controlled A/B packet measured the declaration
  command at 6531 ms isolated median versus 10463 ms under same-affinity
  synthetic contention; the 3932 ms delta is advisory and does not retune the
  15.500s budget.
- coverage gate: no mutation producer was needed; the changed surface is
  Markdown/artifacts only, and the focused runner proof passed 54 tests.
- evaluator depth: deterministic-gates-only; Cautilus was not run because its
  execution remains ask-before-run and is outside this goal.

## Healthy

- [The evidence packet](../probe/2026-08-06-runtime-evidence-and-nose.md) binds
  source SHA, installed SHA/version, host, timestamps, command receipts, PATH,
  return codes, and explicit non-claims.
- The supported installer route ran successfully and post-install doctor found
  `nose 0.20.0` ready with the manifest minimum `>=0.17.0` matched.
- Support sync correctly classified `nose` as integration-only with no
  materialized support skill. The source clone inventory scanned every declared
  root with exit code 0 and kept its findings advisory.
- The bounded reviewer confirmed that the runtime units, A/B values, installer
  route, version requirement, and non-claims match their owning receipts.

## Weak

- Pre-install doctor already found `nose 0.20.0`, so this run does not prove a
  missing-to-installed transition; it proves that the supported installer was
  invoked successfully and the resulting binary is ready.
- Source `HEAD` `8047a614…` and installed checkout `7eed13ec…` differ; the host
  proof is not source/install commit parity.
- The clone inventory reports advisory families while its baseline is stamped
  under `nose 0.19.0`; no clean baseline comparison or re-baseline is claimed.

## Missing

- No controlled cross-host runtime cohort, exact repaired-runner A/B, provider
  roundtrip, live-agent observation, remote-CI observation, or release parity
  proof is present.

## Deferred

- Keep the runtime budget unchanged until a future controlled cohort supports a
  threshold decision. Re-baseline the clone inventory only in a separately
  scoped duplication/tool-version phase.

## Advisory

- structural review result: command `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`; no target skill was named; the current centers are
  the existing runtime packet and integration manifest, strengthened by the
  durable host-proof packet and current-pointer reconciliation. The proof
  boundary is packet plus bounded reviewer, with existing-gate reuse rather
  than a new floor.
- prose review result: `inventory_skill_ergonomics.py --summary` found only
  ambient host-surface advisories; the changed goal and packet passed the doc
  authoring preflight after link and inline-code repairs.
- `inventory_nose_clones.py --json` reported 9 advisory families and a
  0.19.0-to-0.20.0 baseline skew; these are refactoring candidates, not a
  standing quality failure or a reason to rewrite the baseline here.

## Delegated Review

- Delegated Review: executed — unnamed Codex bounded reviewer, requested
  `gpt-5.6-terra` with medium reasoning; findings received in the parent.
  Boundary fingerprint verdict was `clean` for window
  `runtime-evidence-nose-closeout`. The reviewer confirmed substantive packet
  claims and identified stale handoff/quality/retro pointers plus missing
  goal-bound closeout binding. Those findings are now reconciled in the goal,
  handoff, goal-bound retro, and evidence packet; this record is current.
- Final readiness review: executed — unnamed Codex bounded reviewer, requested
  `gpt-5.6-terra` with medium reasoning; verdict `PASS` and findings received in
  the parent. Boundary fingerprint verdict was `clean` for window
  `runtime-evidence-final-readiness`; the reviewer confirmed cross-surface
  consistency, goal binding, the contract follow-up, exact pointer-validator
  evidence, and the explicit non-claims.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not re-delegated because this docs/host-evidence slice
  changes no slow gate, runner, threshold, or proof logic.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --detail`
- `pytest -q tests/quality_gates/test_quality_runner.py tests/quality_gates/test_quality_runner_runtime_aggregate.py` — 54 passed.
- `python3 scripts/suggest_mutation_coverage_command.py --repo-root .` — noop; no eligible mutation-pool files changed.
- Host receipts: `charness tool doctor/install/sync-support nose`, `nose --version`, and `inventory_nose_clones.py --json`; full receipts are in the bound packet.
- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest` — completed.
- `python3 scripts/validate_current_pointer_freshness.py --repo-root .` — passed.
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` — passed.

## Recommended Next Quality Moves

- active — capability_needed=current cross-surface proof state; next_center=the
  goal, quality, retro, and handoff pointer set; transformation=keep one
  goal-bound packet and one current-pointer narrative aligned at closeout;
  proof_boundary=bounded claims review plus validators; enforcement_posture=existing-gate-reuse.
- passive — because no threshold or scheduler decision is proposed in this goal,
  capability_needed=cross-host runtime attribution; next_center=the
  controlled A/B packet; transformation=collect a supported-host cohort only
  when a threshold or scheduler decision is proposed; proof_boundary=versioned
  cohort and distinct review; enforcement_posture=no-gate because it is outside
  this goal.

## History

- [Prior runtime phase-isolation review](./history/2026-07-19-portable-proof-path-learning-review.md)
