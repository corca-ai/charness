# Quality Review
Date: 2026-08-06
Title: Runtime phase isolation and final quality closeout

## Scope

Target boundary: repo-wide quality review of the quality-runner scheduling seam,
its checked-in plugin export, focused behavioral proof, and closeout artifacts.

Ambient repo findings: existing skill-ergonomics heuristics, historical local-only
issue states, and remote/installed/provider claims are not target findings here.

## Current Gates

The pre-repair standing read-only suite ran 84 gates with one failure: the
inventory declaration runtime budget. The repaired full read-only run passed
85/85 gates in 59.5s.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json`, rendered by the <!-- reproduction-source -->
  quality runtime summary command; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: the declaration gate now reports 7.345s latest / 7.497s
  recent median / 18.572s historical max against a 15.500s budget; ten
  sequential isolated runs were 7.1–7.7s. The earlier 16.075s/18.572s samples
  were contended observations, not a reason to raise the floor.
- coverage gate: focused runner/aggregate proof passed 54 tests; the final
  standing read-only quality gate passed 85/85.
- evaluator depth: deterministic-gates-only; Cautilus was not run because its
  execution requires explicit authorization.

## Healthy

- Runner ownership is preserved: phase scheduling and receipt aggregation stay
  in `scripts/run-quality.sh`, while validator semantics are unchanged.
- The source runner and `plugins/charness/scripts/run-quality.sh` are synced,
  and the behavioral probe covers first drain, isolated declaration completion,
  next-phase start, runtime-record order, and failure receipt propagation.
- Two bounded fresh-eye rounds reviewed the proposal and repaired diff before
  parent edits; each returned a clean boundary fingerprint.
- The final full read-only quality run passed 85 gates with 0 failures, including
  critique, retro, artifact, source/plugin, mutation, and runtime-budget checks.
- Verification-locked closeout passed its deterministic checks, broad pytest,
  and changed-line mutation consumer; the closeout's unexamined prior Python
  path was checked with `python3 scripts/parity_harness.py --against origin/main`
  and reported zero repairs/uncomparable files.

## Weak

- The causal explanation is now supported by same-host isolated samples but is
  not yet a controlled isolated-versus-contended A/B cohort across hosts.
- The focused test uses a fixture probe and does not establish installed-plugin,
  provider, or remote CI behavior.

## Missing

- Independent remote CI observation for this unpublished head.
- A controlled cross-run runtime cohort sufficient to justify changing the
  15.500s budget.
- Automatic discovery of every mutation producer relevant to a changed proof
  surface; the existing suggestion helper remains a manual workflow aid.

## Deferred

- Cross-host runtime-budget retuning and any scheduler generalization are
  deferred until the measured A/B evidence identifies a recurring need.
- Cautilus, live provider behavior, installed-machine behavior, release tags,
  and public version publication are outside this phase.

## Advisory

- structural review result (artifact: this quality record): target is the runner quality seam; the applied move
  is a bounded gate-reuse/phase-isolation repair, not a new scheduler framework.
  Ambient skill ergonomics remain advisory (command: `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`).
- prose review result (artifact: this quality record): target-vs-ambient split is explicit; progressive
  disclosure and helper ownership are unchanged because the defect is execution
  sequencing, not public skill authoring (artifact: this quality record;
  command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`).
- dup-ratchet remains an existing advisory/ratchet signal (command: `python3
  skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary`);
  interpret its result after the final full run.

## Delegated Review

- Delegated Review: executed — two distinct unnamed bounded reviewer rounds
  reviewed the proposal and repaired diff. The repaired round identified and
  drove the generated mirror sync and immediate-flush test hardening; boundary
  fingerprints were clean for every returned reviewer. Evidence is in
  `charness-artifacts/critique/2026-08-06-critique-review.md`.
- Slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof
  were executed through the quality planner and runtime evidence; no
  threshold change is justified before controlled A/B measurement.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `pytest -q tests/quality_gates/test_quality_runner.py tests/quality_gates/test_quality_runner_runtime_aggregate.py` — 54 passed.
- `python3 scripts/validate_critique_artifacts.py --repo-root . --paths charness-artifacts/critique/2026-08-06-critique-review.md` — passed.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `bash -n scripts/run-quality.sh` and `git diff --check` — passed.
- `CHARNESS_QUALITY_LABELS=validate-inventory-consumption-declaration ./scripts/run-quality.sh --read-only` — 10 sequential isolated runs, each passed in 7.1–7.7s.
- `./scripts/run-quality.sh --read-only` — 85 passed, 0 failed, 59.5s.
- `python3 scripts/run_slice_closeout.py --repo-root . --base --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage` — completed; broad pytest 41.0s and changed-line consumer passed.
- `python3 scripts/parity_harness.py --repo-root . --against origin/main --paths tests/test_web_fetch_route_and_classify.py --json` — `repair_count: 0`, `uncomparable: {}`.
- `python3 scripts/validate_quality_artifact.py --repo-root . --artifact-path charness-artifacts/quality/2026-08-06-runtime-phase-isolation.md` — passed.
- Locked closeout, pre-push, remote CI, and issue readback remain publish-boundary evidence.

## Recommended Next Quality Moves

- active — capability_needed=isolated runtime evidence; next_center=the
  runtime profile and budget consumer; transformation=compare contended and
  isolated declaration samples on the same host before any retune;
  proof_boundary=controlled A/B runtime packet; enforcement_posture=advisory.
- active — capability_needed=complete mutation producer selection; next_center=the
  existing mutation suggestion helper; transformation=invoke and validate its
  producer set before assembling focused proof;
  proof_boundary=changed-line consumer receipt; enforcement_posture=existing-gate-reuse.
- passive — because no release target/version was supplied, capability_needed=public
  release publication; next_center=the explicit release selector;
  transformation=keep current 3.2.0 surfaces unchanged until a version/tag
  decision is supplied; proof_boundary=release planner plus remote readback;
  enforcement_posture=no-gate.

## History

- [issue #508 local quality record](history/2026-07-19-portable-proof-path-learning-review.md)
