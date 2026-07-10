# Quality Review
Date: 2026-07-10

## Scope

Target boundary: repo-wide evidence inventory followed by selected correctness,
standing-test/gate speed, shipped CLI speed, and v0.64.0 release-readiness work.

Ambient repo findings: high-confidence dead code, brittle guards, structural
waste, dual implementations, CLI contracts, scan hygiene, Ruff, compile, and
ShellCheck were clean. Advisory length, test ratio, doc clones, and product
feedback gaps remain visible rather than being converted into cleanup churn.

## Current Gates

- Healthy: `./scripts/run-quality.sh --read-only` passed 81 gates with zero
  failures in 47.2s after the duplicate hard-arm repair.
- Healthy: standing pytest passed in 28.1s; focused correctness/speed tests,
  whole-tree critique validation (650 records), repo-copy invariants, mirror
  equality, Ruff, py_compile, and ShellCheck passed.
- Healthy: duplicate ratchet is clean at `fixable_ceiling=0` without accepting
  a baseline; two extractable families were reduced and two residual standard
  shapes received evidence-specific intentional dispositions.
- Weak: changed-line mutation evidence remains stale until the committed final
  verification-lock producer runs; the broad gate correctly warned, not claimed.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 28.1s latest / 30.6s median, budget 140.0s;
  `dead-code-advisory` 7.8s / 7.8s; `check-coverage` 7.5s / 7.4s, budget
  55.0s; `check-markdown` 5.3s / 5.9s, budget 11.0s; `check-secrets` 5.0s /
  5.0s, budget 6.0s.
- measured deltas: healthy bootstrap resolution 502.40ms to 102.01ms median
  (4.93x); Markdown gate 4.73s to 4.01s local median; the dominated preflight
  integration call 5.02s to 3.96s; plain version 112.32ms median and no writes.
- coverage gate: broad deterministic suite passed; final changed-line mutation
  proof is intentionally pending the committed verification lock.
- evaluator depth: deterministic gates only. This code/data/runtime slice did
  not require Cautilus and the ask-before-run boundary was not opened.

## Healthy

- Product review now counts only deliveries for usage, time, dimensions, and
  evidence while linked explicit feedback enriches its target's signals.
- Delivery and feedback windows are applied independently; friction/missed
  thresholds preserve outcome-only failures and count unique target episodes.
- Schema-invalid historical JSONL returns structured `invalid_feedback`, never
  appends, and is proven byte-identical after rejection.
- Bootstrap reuse validates contract shape, Python minimum, modules, and env in
  one read-only probe; every unhealthy/launch-error case retains one repair owner.
- Markdown advisory and blocking scans overlap while retaining deterministic
  output order, stderr channel, WARN posture, and MarkdownLint exit status.
- Plain version probes are read-only; verbose/json/check retain provenance and
  update-state behavior.

## Weak

- No observer-owned feedback event exists: 1,335 deliveries, zero feedback.
- The feedback append path has no interprocess lock; concurrent writers remain
  a plausible but unobserved integrity risk.
- Twelve Python files are in advisory length bands and test/production ratio is
  1.01 versus 1.00; neither count alone proves a bad split or low-value tests.

## Missing

- Missing: consumer-repo evidence that feedback changes a real product decision.
- Missing: automatic lifecycle observers and rotated-stream reconciliation.
- Missing: final remote/tag/release/fresh-checkout/install readback; publication
  is a later irreversible boundary, not implied by local green.

## Deferred

- Deferred: concurrent append locking until automatic or concurrent emitters
  supply a real trigger and race fixture.
- Deferred: changed-file Markdown caching because invalidation proof is absent.
- Deferred: broad nested-process consolidation, pytest worker changes, parser
  rewrite, lazy urllib, and arbitrary-invalid direct reconciliation callers.

## Advisory

- structural review result: command: `inventory_structural_waste.py`; no broad
  scanners or duplicate discovery candidates. Existing shared readers and
  runners remain the current centers; no new quality floor was added.
- test-economics result: command: `inventory_standing_test_economics.py`; 385
  test files and 144 standing nested-CLI files are a review signal, not a deletion
  target. Worker-count experiments (8/16/24) kept 16 as the honest fastest layer.
- duplicate review result: command: `check_dup_ratchet.py`; extracted delivery
  target ownership and removed dead command boilerplate. The remaining two-line
  loop and cross-domain JSONL parser shapes are intentional, not baseline growth.
- prose/skill review result: command: `inventory_skill_ergonomics.py`; no trigger,
  progressive-disclosure, reference-discoverability, or core-overfill blocker;
  host-reference/argparse counts remain lexical advisories.
- north-star/floor restraint: artifact: `docs/design-north-star.md`; reversible
  code fixes use tests and existing gates;
  no new standing gate was added because wrong answers are already caught by
  schema, focused regression, dup-ratchet, mirror, and release boundaries.

## Delegated Review

- Delegated Review: executed — lower-power workers owned all code edits; fresh-eye
  plan, correctness, performance, version-contract, and counterweight reviewers
  found and closed window/outcome/min-version/OSError/test-value risks.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  executed — copy-heavy tests stayed release-only, Markdown's independent checks
  overlap, bootstrap repair proof was not duplicated, and real CLI isolation was
  retained where inventory could not prove waste.

## Commands Run

- command: quality planners plus runtime, test-economics, structural, verbosity,
  lint-ignore, brittle-source, dual-implementation, CLI, dead-code, clone, and
  skill-ergonomics inventories.
- command: focused pytest, worker-count experiments, repeated startup/Markdown/
  preflight timings, source/plugin `cmp`, Ruff, py_compile, and ShellCheck.
- command: `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- command: `./scripts/run-quality.sh --read-only`

## Recommended Next Quality Moves

- active final-verification-lock — capability_needed=mutation-aware committed proof; next_center=`scripts/run_slice_closeout.py`; transformation=produce coverage over the final committed bundle; proof_boundary=verification-lock plus changed-line gate; enforcement_posture=blocking at release lock.
- passive first-real-feedback because zero observer-owned feedback exists; capability_needed=outcome evidence; next_center=`record_usage_feedback.py`; transformation=record only a legitimate closed-enum observation; proof_boundary=writer/validator/reporter readback; enforcement_posture=no-gate until evidence exists.
- passive concurrent-append-hardening until concurrent or automatic writers exist; capability_needed=idempotent multi-process append; next_center=usage storage seam; transformation=lock or atomic append; proof_boundary=race fixture plus validator readback; enforcement_posture=no-gate because current writes are explicit single-operator actions.

## History

- [2026-07-10 outcome-driven feedback review](./2026-07-10-outcome-driven-feedback.md)
- [2026-07-03 pytest suite test-value audit](./history/2026-07-03-pytest-suite-test-value-audit.md)
