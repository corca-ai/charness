# Quality Review
Date: 2026-07-19
Title: Speed-only proof-path review

## Scope

Target boundary: focused mutation-coverage production and repeated closeout
duplicate scans; preserve the exact proof while reducing wall time.

Ambient repo findings: none promoted. The broad suite's nested-CLI population is
real structural debt, but redesigning it is outside this measured slice.

## Current Gates

The standing pytest runner owns bounded xdist, external basetemp isolation, and
serial-fallback diagnostics. The changed-line consumer still owns the final
freshness verdict. Surface aggregation deduplicates exact command strings.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: broad pytest 73.6s latest / 54.1s median against a 140s budget; read-only quality 93.9s latest / 59.5s median against a 90s budget.
- coverage gate: the prior focused producer took 213s; the same 228-test set now passed under coverage in 34.8s, with roughly 20s more for JSON export.
- install/update self-validation: the same 34 cases took 91.56s through raw serial pytest and 29.29s through the canonical xdist runner.
- release resilience: the same 41-test serial command fell from 51.41s to 30.38s after removing one Python proxy startup per Git call.
- evaluator depth: deterministic gates only; no prompt or behavior-evaluator surface changed.

## Healthy

- Existing xdist, temp isolation, coverage combine, freshness fingerprint, and
  changed-line consumer owners remain separate and reusable.
- Root and generated plugin scripts are synchronized; final delegated review
  found no proof-loss or operability blocker.
- The install/update wrapper now owns only its three-target selection; runner
  parallelism, release-marker inclusion, temp isolation, and fallback stay centralized.
- Release tests still cross real Git and temporary remotes; the faster proxy removes
  only the extra Python interpreter and retains fault injection plus decoded argv logs.
- Shell test fixtures now route through repo-python ownership and are actually
  discovered by the existing shell lint before standing pytest.

## Weak

- Before this slice the focused suggester emitted raw serial pytest, bypassing
  the repo's canonical parallel runner. This made a smaller test set materially
  slower than the broad standing suite.
- The install/update self-validation wrapper had the same bypass and paid
  91.56s for 34 cases that the canonical runner completed in 29.29s.
- The quality-baseline surface rendered the same duplicate-ratchet verdict as
  JSON while Python and skill surfaces rendered summary, defeating literal
  command deduplication.
- The release fixture previously started Python before real Git for every proxied
  command, concentrating avoidable startup cost in the slowest test family.

## Missing

None within the speed-only boundary after adding a real nested-runner coverage
export regression.

## Deferred

- The standing-runner recognizer accepts some non-`python3` command shapes that
  instrumentation does not normalize. Generated commands use `python3`, so this
  is a compatibility edge rather than a speed-slice blocker.
- Broad nested-CLI consolidation remains structural test-economics work and was
  not inferred from file counts alone.
- Pretty-printed logs from the retired Python proxy are not accepted as preseed
  state; active test logs are ephemeral and shell-owned, so compatibility stays deferred.

## Advisory

- structural review result: evidence: capability needed was same changed-line evidence at
  lower latency; current centers were the standing runner and mutation producer;
  target replacement strengthened the runner without adding a new gate; evidence:
  `command: python3 scripts/run_standing_pytest.py --print-command`.
- prose review result: artifact: no skill trigger or progressive-disclosure change was
  needed; one implementation-discipline example was synchronized to the runnable
  command; evidence: `artifact: docs/conventions/implementation-discipline.md`.
- structural review result: evidence: command: focused fake-Git contract pytest;
  capability needed was faster real-Git release proof; current center was the
  fault-injecting proxy; moving its execution mechanics to Bash removed startup
  without adding a gate or weakening the real boundary.
- `command: inventory_standing_test_economics.py --detail` found
  `test_file_count=406` and `nested_cli_standing_file_count=158`; the inference does not establish which
  boundary smokes are waste, so no broad deletion follows.

## Delegated Review

- Delegated Review: executed — final code critique found no remaining ship blocker;
  both final angle and counterweight boundary fingerprints verified clean.
- Slow-gate lenses: `parallel-critical-path` and `duplicated-proof` executed;
  `fixture-economics` was inventoried locally but not used to expand this slice.

## Commands Run

- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --detail`
- focused coverage experiment over the prior 13-file packet with 16 xdist workers: 228 passed in 34.8s; coverage JSON contained 940 files.
- `/usr/bin/time ./scripts/self-validate-install-update.sh`: 34 passed in 91.56s before runner reuse and 29.29s with identical targets after reuse.
- `/usr/bin/time -f 'elapsed=%e' python3 -m pytest -q tests/quality_gates/test_release_publish_resilience.py`: identical 41 tests measured 51.41s before and 30.38s after on this host.
- canonical seven-file release packet: 102 passed in 6.16s with xdist.
- command: python3 -m pytest -q tests/quality_gates/test_standing_pytest_runner.py tests/quality_gates/test_suggest_mutation_coverage_command.py tests/quality_gates/test_mutation_coverage_producer.py tests/quality_gates/test_surface_obligations.py
- `python3 scripts/check_changed_surfaces.py --repo-root . --paths ... --json` confirmed one duplicate-ratchet command for the combined surfaces. <!-- reproduction-source -->

## Recommended Next Quality Moves

- active completed — capability_needed=same focused changed-line proof faster; current_centers=standing runner and mutation producer; next_center=standing runner target selection; transformation=gate reuse through target replacement plus exact duplicate-command normalization; proof_boundary=real child-process coverage export and final changed-line consumer; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=faster install/update self-validation; current_centers=three-target wrapper and standing runner; next_center=standing runner execution; transformation=replace raw serial pytest with canonical target replacement; proof_boundary=identical 34-case collection plus real parallel execution; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=faster real-Git release proof; current_centers=release fixture and real temporary remotes; next_center=fault-injecting proxy; transformation=replace Python proxy startup with exact Bash delegation; proof_boundary=102 related release tests plus full standing suite; enforcement_posture=existing-gate-reuse.
- passive interpreter compatibility until a non-`python3` caller is supported — capability_needed=broader caller compatibility; current_centers=standing-runner recognizer; next_center=instrumentation normalization; transformation=defer outside speed-only scope; proof_boundary=real alternate-interpreter command; enforcement_posture=no-gate because generated commands are fixed to `python3`.

## History

- [Prior review](history/2026-07-19-quality-review.md)
