# Quality Review
Date: 2026-07-19
Title: Complete focused proof and resumable release failure

## Scope

Target boundary: changed-line focused-test selection, its compact structured
output, and pre-publication release failure recovery evidence.

Ambient repo findings: standing-test ratio and duplicate inventories remain
advisory; no prompt/evaluator behavior changed.

## Current Gates

The standing runner owns execution, the mutation selector owns affected-test
discovery, the changed-line consumer owns coverage truth, and the release
runtime owns local failure evidence. Existing gates are reused; no new hard
gate or prose ritual was added.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: broad quality completed in 67.4s; pytest was 46.5s.
- coverage gate: the broad pre-commit run passed but honestly warned that five uncommitted pool files were outside base..HEAD; locked post-commit proof remains required.
- selector dogfood: dependency-aware discovery took 6.03s versus 3.33s for direct-only discovery, but selected the release integration tests that the faster pass omitted.
- evaluator depth: deterministic gates only; no prompt, routing, or evaluator-backed behavior surface changed.

## Healthy

- Eligible untracked pool files now participate in pre-commit selection and
  content fingerprinting, keeping producer and post-commit consumer identities aligned.
- Test selection follows local test-helper imports and all loader ancestors,
  preserving direct unit tests plus entrypoint integration tests.
- Default suggestion output remains one copyable command; `--detail` emits YAML,
  and no live suggester call site retains `--json`.
- Release failures persist structured rollback/restart state under the Git
  common directory without dirtying the worktree.
- Failure records omit raw exception text, use directory/file modes 0700/0600,
  retain at most 20 YAML records, and atomically replace a temporary file.
- If persistence fails, the terminal regains bounded detailed diagnostics while
  still reporting typed persistence failure.
- Source and generated plugin mirrors are synchronized.

## Weak

- Static affected-test inference cannot model pytest's implicit `conftest.py`
  and `pytest_plugins` edges; the result is a safe broad fallback, not false green.
- Conservative loader-ancestor selection increased selector cost by about 2.7s
  and expands release-focused targets; the avoided late coverage rerun is the
  intended tradeoff but needs continued runtime observation.

## Missing

- Post-publication probes use a distinct channel, but the durable release
  artifact still does not bind a different observer identity.

## Deferred

- Pytest implicit fixture/plugin edges remain deferred until dogfood shows they
  materially reduce focused selection; current missing/partial states retain broad fallback.
- Durable failure records intentionally omit raw exception text. The original
  raised exception remains the detailed live channel; the YAML record is restart state.

## Advisory

- structural review result: evidence: command: selector dogfood and final
  changed-line consumer; capability needed was complete focused proof before
  commit; current centers were selector, standing runner, and final coverage
  consumer; selection moved to the selector owner and enforcement reuses the
  existing coverage consumer rather than adding a gate.
- prose review result: evidence: artifact: `scripts/suggest_mutation_coverage_command.py`;
  trigger and helper ownership remain executable in the
  selector; default output is summary-first and detailed YAML is opt-in; no
  public skill prose expansion was needed.
- command: `inventory_standing_test_economics.py --detail` reported 407 test
  files and advisory-only nested CLI inventory; this slice did not infer safe
  test deletion from counts.
- command: `validate_skill_ergonomics.py` reported 16 heuristic findings across
  22 skills, reviewed as ambient host-adapter/integration references rather than
  target skill defects.

## Delegated Review

- Delegated Review: executed — two high-leverage bounded angle reviewers plus a
  separate counterweight found the raw-error persistence hazard; the fix removed
  raw exception content, restricted permissions/retention, and restored a
  persistence-failure fallback. Both boundary verifies reported `drift: []`.
- Slow-gate lenses: fixture-economics, parallel-critical-path, and duplicated-proof
  were considered; conservative integration selection was retained because it
  prevents a measured late proof rerun.

## Commands Run

- `bash scripts/run-quality.sh` pre-refresh runs — first caught the CLI length
  boundary; a later run caught duplicated YAML-helper ownership. Both were
  fixed by moving default rendering to the release runtime's shared repo module.
- focused selector/release packet — 73 passed in 34.27s after critique fixes.
- `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --detail` — recommended, all five pool files mapped.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` — source/plugin mirrors synchronized.
- reviewer boundary snapshot/verify — both review phases returned `ok: true`, `drift: []`.

## Recommended Next Quality Moves

- active completed — capability_needed=complete pre/post-commit changed-line identity; current_centers=mutation changed-file selector and coverage consumer; next_center=selector; transformation=union eligible untracked files; proof_boundary=post-commit freshness fingerprint; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=complete focused tests through helper/loader seams; current_centers=direct reference scan and standing runner; next_center=dependency-aware selector; transformation=follow imported helpers and retain all loader ancestry; proof_boundary=exact changed-line coverage consumer; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=compact resumable release failure; current_centers=terminal payload and rollback state; next_center=release runtime; transformation=restricted bounded YAML recovery record plus compact/fallback terminal channels; proof_boundary=forced rollback and renderer-failure fixtures; enforcement_posture=existing-gate-reuse.
- passive pytest implicit-edge inference until dogfood shows broad fallback waste — capability_needed=fixture/plugin-aware focused selection; current_centers=pytest collection and selector; next_center=selector dependency model; transformation=add scoped conftest/plugin edges; proof_boundary=fixture-only changed-line regression; enforcement_posture=no-gate because present behavior fails safe.
- passive distinct observer binding until the release observer schema is designed — capability_needed=observer-identified irreversible-boundary proof; current_centers=release observer and durable artifact; next_center=release schema; transformation=bind different observer identity without terminal-green semantics; proof_boundary=public readback by distinct observer; enforcement_posture=no-gate because schema remains undecided.

## History

- [Portable proof-path learning review](history/2026-07-19-portable-proof-path-learning-review.md)
