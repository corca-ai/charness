# Quality Review
Date: 2026-07-19
Title: Portable proof-path learning review

## Scope

Target boundary: `quality`, `impl`, `prove`, `retro`, and `create-skill` consumer
paths; determine whether this session's proof-efficiency lessons transfer to
other repos, then dogfood them against Charness release recovery.

Ambient repo findings: release resume checked only remote tag presence, not the
exact peeled release commit; the fix is included as dogfood, while broader
nested-CLI consolidation remains outside this review.

## Current Gates

The quality planner owns progressive disclosure, the standing-test inventory
owns runtime triage, public dogfood owns consumer acceptance rows, and the
release resume helper owns exact Git publication identity.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: broad pytest 73.6s latest / 54.1s median against a 140s budget; read-only quality 93.9s latest / 59.5s median against a 90s budget.
- coverage gate: the prior focused producer took 213s; the same 228-test set now passed under coverage in 34.8s, with roughly 20s more for JSON export.
- install/update self-validation: the same 34 cases took 91.56s through raw serial pytest and 29.29s through the canonical xdist runner.
- release resilience: the same 41-test serial command fell from 51.41s to 30.38s after removing one Python proxy startup per Git call.
- planner token surface: 4,854 default bytes versus 23,021 `--detail` bytes,
  a 79% smaller first read for the same repo/target.
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
- The public quality inventory now emits observed finding types plus a compact
  pointer to the five-question proof-efficiency reference.
- `impl` owns boundary replacement, `prove` actual-consumer execution, and
  `retro → create-skill` the portable-candidate handoff; the inventory only
  points to the owning detail rather than repeating it.
- Release resume now peels annotated remote tags and refuses a tag whose commit
  identity differs from the local release commit.

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
- Before this review, the lessons were durable in retros but absent from the
  public skills' executable planner/inventory/dogfood path. `quality` also
  requested full `--detail` output by default despite summary-first policy.

## Missing

- Precommit release rollback still restores/quarantines correctly but its typed
  recovery result is not persisted after the helper exits; restart evidence is missing.
- Post-publication probes use a distinct channel, but the durable artifact does
  not yet bind a different postpublication observer identity.

## Deferred

- The standing-runner recognizer accepts some non-`python3` command shapes that
  instrumentation does not normalize. Generated commands use `python3`, so this
  is a compatibility edge rather than a speed-slice blocker.
- Broad nested-CLI consolidation remains structural test-economics work and was
  not inferred from file counts alone.
- `issue_verify_closeout` still uses terminal-sounding `verified` for state/form
  observables even when behavior is explicitly non-verified. Renaming is a
  compatibility decision for a future major or an additive migration field.

## Advisory

- structural review result: evidence: capability needed was same changed-line evidence at
  lower latency; current centers were the standing runner and mutation producer;
  target replacement strengthened the runner without adding a new gate; evidence:
  `command: python3 scripts/run_standing_pytest.py --print-command`.
- prose review result: evidence: the five skill cores each gained only their owning
  selection/sequence rule; the detailed method is one quality reference and the
  planner defaults to compact output; evidence: `artifact: skills/public/quality/references/proof-path-efficiency.md`.
- structural review result: evidence: command: focused fake-Git contract pytest;
  capability needed was faster real-Git release proof; current center was the
  fault-injecting proxy; moving its execution mechanics to Bash removed startup
  without adding a gate or weakening the real boundary.
- `command: inventory_standing_test_economics.py --detail` found
  `test_file_count=406` and `nested_cli_standing_file_count=158`; the inference does not establish which
  boundary smokes are waste, so no broad deletion follows.
- scenario review result: `command: python3 scripts/plan_cautilus_proof.py --repo-root . --paths ... --detail`;
  `create-skill` retains `representative-skill-contracts`
  and `impl` retains `impl-adapter-bootstrap`; this additive closeout guidance
  changes neither trigger nor adapter bootstrap, so no scenario mutation or live
  Cautilus run is claimed; the planner did not recommend evaluator execution.

## Delegated Review

- Delegated Review: executed — three bounded audits found the portable-routing
  gaps, exact remote-tag bug, and three explicitly deferred irreversible-boundary risks;
  the shared-tree fingerprint verified with `drift: []`.
- Slow-gate lenses: `fixture-economics`, `parallel-critical-path`, `duplicated-proof`,
  compatibility envelope, and validator consumption all executed.

## Commands Run

- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --detail`
- default/detail planner byte counts: 4,854 / 23,021.
- reviewed dogfood rows for `quality`, `prove`, `retro`, and `create-skill`
  bind the new acceptance claims; registry validation and plugin parity prove shape, not live prompt routing.
- focused portable-skill/release packet: 61 passed in 2.07s; annotated-tag
  identity proof: 6 passed in 1.59s.
- command: python3 -m pytest -q tests/quality_gates/test_standing_pytest_runner.py tests/quality_gates/test_suggest_mutation_coverage_command.py tests/quality_gates/test_mutation_coverage_producer.py tests/quality_gates/test_surface_obligations.py
- `python3 scripts/check_changed_surfaces.py --repo-root . --paths ... --json` confirmed one duplicate-ratchet command for the combined surfaces. <!-- reproduction-source -->

## Recommended Next Quality Moves

- active completed — capability_needed=same focused changed-line proof faster; current_centers=standing runner and mutation producer; next_center=standing runner target selection; transformation=gate reuse through target replacement plus exact duplicate-command normalization; proof_boundary=real child-process coverage export and final changed-line consumer; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=faster install/update self-validation; current_centers=three-target wrapper and standing runner; next_center=standing runner execution; transformation=replace raw serial pytest with canonical target replacement; proof_boundary=identical 34-case collection plus real parallel execution; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=faster real-Git release proof; current_centers=release fixture and real temporary remotes; next_center=fault-injecting proxy; transformation=replace Python proxy startup with exact Bash delegation; proof_boundary=102 related release tests plus full standing suite; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=portable proof-efficiency learning; current_centers=quality planner/inventory plus impl/prove/retro/create-skill; next_center=consumer execution path; transformation=one concept-owned reference, compact planner default, observed-finding pointer, owned core rules, and reviewed dogfood acceptance; proof_boundary=real Charness inventory output plus focused tests and explicit live-routing non-claim; enforcement_posture=existing-gate-reuse.
- active completed — capability_needed=unambiguous release recovery; current_centers=release resume and real Git remotes; next_center=remote tag identity; transformation=peel and compare exact remote/local tag commits; proof_boundary=annotated bare-remote regression plus mismatch refusal; enforcement_posture=existing-gate-reuse.
- passive interpreter compatibility until a non-`python3` caller is supported — capability_needed=broader caller compatibility; current_centers=standing-runner recognizer; next_center=instrumentation normalization; transformation=defer outside speed-only scope; proof_boundary=real alternate-interpreter command; enforcement_posture=no-gate because generated commands are fixed to `python3`.
- passive irreversible-boundary follow-up until recovery-state and observer schemas are designed together — capability_needed=durable rollback restart evidence and distinct postpublication observer binding; current_centers=release rollback/probe artifacts; next_center=release recovery/observer schema; transformation=spec then implement without another terminal green; proof_boundary=forced rollback restart plus observer-bound public readback; enforcement_posture=no-gate because the schema choice is not locally obvious.

## History

- [Prior review](history/2026-07-19-quality-review.md)
