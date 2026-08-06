# Quality Review
Date: 2026-08-06
Title: Focused mutation coverage export runtime review

## Scope

Target boundary: issue #505's local focused changed-line coverage producer,
coverage JSON export, consumer limits, source/plugin mirror, and closeout proof.

Ambient repo findings: skill-ergonomics heuristics and remote/installed/provider
behavior are outside this runtime slice.

## Current Gates

- The focused producer/consumer run over the four mapped changed pool files returned
  `clean`, `0` blocking files, and `4/4` analyzed files.
- Focused regression tests passed `57`; the implementation commit's pre-commit gate
  passed, including staged mirror drift and boundary checks.
- No broad final quality, remote CI, installed-host, provider, release, or Cautilus
  proof is claimed by this artifact.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `skills/public/quality/scripts/render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: the matched export phase, `coverage json` over the same combined data, took `9.54s`
  and produced `6,746,080` bytes without a filter, versus `0.31s` and `34,158`
  bytes when restricted to the four changed pool paths.
- end-to-end focused lane: the clean current run took `30.00s`; its consumer verdict
  remained clean. The earlier `43.77s` run was a pre-change, one-file observation and
  is context only, not a matched whole-lane speed claim.
- coverage gate: focused changed-line consumer passed `4/4`; no coverage floor or
  mutation scope was weakened.
- evaluator depth: deterministic-gates-only; Cautilus was not run because this slice
  has no explicit evaluation authorization or live behavior claim.

## Healthy

- The focused pytest selection is unchanged; only report serialization is narrowed.
- The selector still owns what runs, while the coverage producer owns collection and
  the consumer owns the changed-line verdict.
- One comma-separated `--include` preserves every mapped path; broad closeout callers
  remain unfiltered; freshness is stamped only after export succeeds.
- Unmapped files remain explicit partial/unproven results rather than clean verdicts.

## Weak

- The end-to-end lane still pays proof-bearing coverage collection and emits an
  existing `CoverageWarning` about the sitecustomize file being already imported;
  the warning did not alter the clean consumer verdict.
- The timing comparison is local-host evidence and does not establish cross-host or
  remote CI runtime.

## Missing

- There is no automatic per-phase producer/export timing receipt dedicated to this
  focused lane; the matched phase evidence is recorded from the commands run here.
- Installed plugin behavior, remote CI, provider behavior, and Cautilus evidence are
  not established.

## Deferred

- Further test selection, parallelism, and runtime-budget changes remain deferred
  until a new matched proof-bearing workload identifies a safe owner-backed candidate.
- The broad final quality gate remains the publish-boundary backstop; focused speed
  does not replace it.

## Advisory

- structural review result (command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill quality --detail`): the planner's runtime-test-economics packet was answered by preserving the exact test selection and narrowing only the consumer's JSON export. The target skill `quality` was not edited; 16 heuristic skill findings (93 host-surface hits) are ambient portability prompts, not this issue's target.
- prose review result (command: `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`): trigger boundaries, progressive disclosure, and helper ownership are unchanged because this is a host-local coverage export seam, not a public skill authoring change.
- Maintainer-Local Enforcement (command: `python3 scripts/validate_maintainer_setup.py --repo-root .`): enforced — checked-in `.githooks/pre-push` runs the
  read-only quality gate, and `validate_maintainer_setup.py` verified this clone's
  hook path. CI parity was inventoried, but both workflows are explicitly exempt and
  zero jobs were evaluated; that is not remote parity proof
  (`command: python3 scripts/validate_maintainer_setup.py --repo-root .`).

## Delegated Review

- Delegated Review: executed — the first parent-delegated coverage-scope reviewer
  found the repeated-`--include` multi-file blocker; the repair changed it to one
  comma-separated argument and added a two-path argv regression test. The repaired
  surface reviewer returned clean, confirmed broad callers remain unfiltered, and
  both boundary fingerprints were clean for their respective windows.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  applied through the planner and proof-path-efficiency review; no test selection or
  proof-floor reduction was recommended.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --target-skill quality --detail`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `pytest -q tests/quality_gates/test_mutation_coverage_producer.py tests/quality_gates/test_prepush_focused_changed_line_coverage.py` — `57 passed`
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha origin/main --json` — clean, `4/4`
- `/usr/bin/time -p python3 -m coverage json ...` — same-data full versus four-path filtered export, `9.54s` versus `0.31s`
- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_ci_local_gate_parity.py --repo-root . --require-empty-parity-issues`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`

## Recommended Next Quality Moves

- active — capability_needed=actionable focused proof cost; next_center=the
  changed-file coverage export boundary; transformation=retain path-scoped JSON
  export while preserving the unchanged focused test workload; proof_boundary=the
  changed-line consumer plus broad final gate; enforcement_posture=existing-gate-reuse.
- passive — because the remaining collection cost is proof-bearing and no matched
  owner-backed candidate is evidenced, capability_needed=lower mutation-lane cost;
  next_center=the next measured producer workload; transformation=compare a new
  equal-workload candidate before changing selection or parallelism; proof_boundary=
  changed-line consumer and full quality command; enforcement_posture=no-gate.

## History

- [prior mutation lane quality review](history/2026-07-19-portable-proof-path-learning-review.md)
