# Quality Review
Date: 2026-06-16

## Scope

Operator-requested test-speed-first repair, second slice. Scope: reduce the
locked mutation coverage producer path that previously made
`run_slice_closeout.py --verification-lock --produce-mutation-coverage` spend
hundreds of seconds under broad pytest coverage.

## Current Gates

- Focused producer proof: `pytest -q
  tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py`: **29
  passed in 13.12s**.
- Focused producer file proof: `pytest -q
  tests/quality_gates/test_mutation_coverage_producer.py`: **19 passed in
  2.95s**.
- Lint proof: `ruff check scripts/mutation_coverage_producer.py
  scripts/run_slice_closeout.py
  tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py`: **passed**.
- Boundary proof: `python3 scripts/check_boundary_bypass_ratchet.py --repo-root
  .`: **passed**, 89 candidates / 52 clean-convertible / 36 internally-spawning /
  23 likely keep-boundary.
- Spec proof after marker fix: `python3 scripts/check_spec_evidence_durability.py
  --repo-root .`: **passed across 152 docs**; targeted pytest for that gate:
  **11 passed in 4.72s**.
- Locked closeout with focused producer:
  `python3 scripts/run_slice_closeout.py --repo-root . --json
  --verification-lock --refresh-broad-pytest-proof
  --produce-mutation-coverage --mutation-coverage-command "python3 -m pytest -q
  tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py"`:
  **completed**. Broad pytest ran normally in **247.0s**; the focused coverage
  producer then ran in **22.3s** and wrote `reports/mutation/test-coverage.json` <!-- reproduction-source -->
  plus fingerprint
  `9b369e2238f1cff26babdab761c499d60fb9f130ce6cf93e9b5f036fe4c0dfa6`.
- Post-commit branch-wide producer:
  `python3 -m pytest -q tests/quality_gates/test_check_coverage_inventory.py
  tests/quality_gates/test_repo_copy_invariants.py
  tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py
  tests/quality_gates/test_staged_commit_gate_plan.py` under the focused
  producer: **87 passed in 29.66s**, producer elapsed **30.2s**.
- Post-commit changed-line consumer:
  `check_changed_line_mutation_coverage.py --reuse-coverage
  --require-fresh-coverage` over `origin/main..HEAD`: **ok true**, no blocking
  changed lines.
- Previous locked producer baseline from the prior quality record:
  broad pytest under coverage took **462.9s**. The producer-specific cost is now
  the focused 22.3s coverage command; the broad proof is no longer covered by the
  producer path.

## Runtime Signals

- runtime source: closeout JSON payload from `run_slice_closeout.py` on
  2026-06-16 local time, plus structured gate timings emitted by the same run.
- runtime hot spots: ordinary broad pytest remains over budget at **247.0s**;
  focused mutation coverage producer is **22.3s**; earlier broad-coverage
  producer baseline was **462.9s**.
- coverage gate: focused producer successfully emitted
  `reports/mutation/test-coverage.json` <!-- reproduction-source --> and a fresh
  content fingerprint marker. Post-commit consumer proof over `origin/main..HEAD`
  passed with no blocking changed lines.
- evaluator depth: deterministic gates only; Cautilus planner reported
  `next_action: none` and no log-backed behavior evaluation request was present.
- direct outcome: the expensive mutation coverage producer is no longer coupled
  to the broad pytest proof. The remaining slow path is ordinary broad pytest,
  which is separate gate-baseline debt.

## Standing Test Economics

- The focused coverage command deliberately covers only the tests proving this
  producer/runner change. It does not claim full-suite coverage for every changed
  Python line.
- The broad pytest proof still ran normally at verification lock and recorded a
  passing broad proof cache entry for the full changed path set.
- `run_slice_closeout.py` remains near the Python file-length advisory band
  (465/480 lines) and `main()` remains exactly 100/100 function lines; this slice
  kept new behavior in helpers instead of growing `main()`.

## Healthy

- Default behavior is preserved: `--produce-mutation-coverage` without a focused
  command still instruments the broad pytest producer.
- Focused mode validates command shape before plan-only output, requires the
  verification lock, rejects `--skip-broad-pytest`, and participates in unsafe
  command scanning.
- Root scripts and checked-in plugin exports were resynced with
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- Fresh-eye critique found real Act Before Ship issues; all were fixed before
  the successful closeout.

## Weak

- The ordinary broad pytest gate is now the dominant local runtime cost at about
  247s on this machine. This is not producer overhead, but it is still
  gate-baseline runtime debt.
- The focused producer relies on the operator choosing an honest focused pytest
  command for the changed mutation pool. The broad proof still protects general
  regression confidence, but the coverage marker only reflects the focused
  command.
- `run_slice_closeout.py` has only 15 advisory code-line headroom left.

## Missing

- No missing deterministic enforcement remains for this slice.

## Deferred

- Extract closeout producer planning/validation from `run_slice_closeout.py` on
  the next runner touch.
- Investigate ordinary broad pytest runtime separately; this slice removed the
  mutation producer coupling, not the full suite cost.

## Advisory

- The successful closeout emitted a gate-runtime advisory because broad pytest
  took 247.0s against the 120s budget.
- A failed closeout before the successful run exposed a spec evidence durability
  marker miss for `reports/mutation/test-coverage.json` <!-- reproduction-source -->;
  the marker is now on the cited line.
- The closeout advisory also noted subprocess boundary guidance in
  `tests/quality_gates/test_run_slice_closeout_surface_obligations.py`; the
  boundary-bypass ratchet stayed green.

## Delegated Review

- Delegated Review: executed. Bounded fresh-eye code critique used three angle
  reviewers plus one counterweight reviewer through the repo-authorized
  subagent path. Reviewer tier requested: `high-leverage`; requested spawn
  fields sent: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`;
  host exposure state: `requested_fields_sent`; application state:
  `unverified-by-host`.
- Findings fixed: plan-only validation bypass, unsafe focused-command bypass,
  stale plugin mirror, missing invalid-command regression coverage, and stale
  quality evidence.
- Valid but deferred: split closeout producer planning/validation out of
  `run_slice_closeout.py` before adding more runner behavior.

## Commands Run

- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.50.1/skills/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "mutation coverage producer speed" --summary`.
- `pytest -q tests/quality_gates/test_mutation_coverage_producer.py` and
  `pytest -q tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py`.
- `ruff check scripts/mutation_coverage_producer.py
  scripts/run_slice_closeout.py
  tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py`.
- `python3 scripts/check_python_lengths.py --headroom --paths
  scripts/run_slice_closeout.py scripts/mutation_coverage_producer.py
  tests/quality_gates/test_mutation_coverage_producer.py
  tests/quality_gates/test_run_slice_closeout_surface_obligations.py`.
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`.
- `python3 scripts/check_doc_authoring_preflight.py --path
  docs/conventions/implementation-discipline.md`.
- `python3 scripts/check_spec_evidence_durability.py --repo-root .` and
  `pytest -q tests/quality_gates/test_check_spec_evidence_durability.py`.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- Successful locked closeout with focused producer as listed in Current Gates.

## Recommended Next Gates

- active none - post-commit changed-line mutation coverage consumer passed.
- passive treat ordinary broad pytest runtime as the next speed target; it is now
  the largest remaining local gate.
- passive extract closeout producer planning from `run_slice_closeout.py` before
  adding more behavior there.

## History

- [2026-06-12 quality review](history/2026-06-12-quality-review.md)
