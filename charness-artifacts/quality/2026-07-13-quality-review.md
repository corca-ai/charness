# Quality Review
Date: 2026-07-13
Title: v1.0.0 legacy compatibility removal release readiness

## Scope

Target boundary: the release-quality remediation after removing the public `find-skills` skill and all accepted legacy configuration/runtime compatibility for v1.0.0.

Ambient repo findings: release-only validation exposed a Markdown wrapping warning and treated this repo's expanded, semantically complete `## Skill Routing` contract as drift. The duplicate ratchet also surfaced 16 new fingerprints plus 9 membership reductions after the rename/removal slice.

## Current Gates

- `./scripts/run-quality.sh --release`: 82 passed, 0 failed after remediation.
- `check_dup_ratchet.py --repo-root . --json`: clean; zero new code/doc families and `fixable_ceiling=0`.
- focused setup and issue-parser tests: 89 passed in the implementation pass; the fresh-eye reviewer reran 9 focused tests successfully.
- plugin mirror sync: 917 paths unchanged after source-to-export synchronization.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, with the executed release-gate timings summarized by `run-quality.sh --release`.
- runtime hot spots: pytest 54.2s, coverage 6.8s, Markdown 5.4s; total release-quality runtime 73.7s.
- coverage gate: broad coverage passed, but changed-line mutation proof for the eight then-uncommitted Python files was explicitly excluded and must be regenerated after commit.
- evaluator depth: deterministic gates only. The Cautilus planner said live evaluator proof was not required, and no ask-before-run authorization was requested.

## Healthy

- The release-only gate caught both the Markdown diagnostic ordering issue and the setup semantic-equivalence issue before tag or push.
- Semantic routing detection checks all six capabilities: handoff trigger, installed metadata/model judgment, read-only catalog, `gather`, `quality`, and SessionStart context-only behavior.
- The hard duplicate arm is clean after extracting shared Markdown parsers and explicitly reviewing every residual family.

## Weak

- A normal release-quality pass can look green while warning that uncommitted mutation-pool files were excluded. This review does not treat that pass as changed-line mutation proof.
- The first failed publish attempt wrote intended future release state into `release/latest.md` before publication; closeout must correct that record and rely on public readback.

## Missing

- Commit-based changed-line mutation coverage is missing until the remediation and release mutation are committed and the verification lock is rerun.

## Deferred

- The pre-install `nose`-missing disposition cannot be reproduced honestly on this maintainer machine because `nose` 0.18.0 was already installed.
- Test/production ratio 1.03 and doc-clone drift remain advisory; neither is evidence of a release regression in this slice.

## Advisory

- structural review result: the gate structure is sound; semantic equivalence belongs in the setup owner, duplicate intent belongs in the reviewed overlay, and release publication remains a separate boundary. Evidence: command `./scripts/run-quality.sh --release` and artifact `charness-artifacts/release/latest.md`.
- prose review result: the expanded root routing prose retains all six required trigger boundaries and keeps the SessionStart hook context-only. Evidence: artifact `scripts/setup_skill_routing_lib.py` and the bounded renderer probes.
- duplicate review: all 16 residual code families were inspected. They are import/bootstrap idioms, one-line delegates, hook lifecycle symmetry, separate parser grammars, or zero-shared-line scanner matches. Evidence: artifact `charness-artifacts/quality/dup-review.json` and command `check_dup_ratchet.py --json`.

## Delegated Review

- Delegated Review: executed — bounded reviewer verdict was BLOCK only because the already-executed 82/82 release-quality result had not yet been recorded in `release/latest.md`; semantic routing, helper ownership, mirrors, and duplicate classifications passed. Boundary fingerprint verification reported `ok: true` with no drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not re-delegated because the target was release correctness and false-positive remediation, not slow-gate economics; runtime timing is recorded above.

## Commands Run

- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- scoped `--accept-rotation` and `--accept-family` update for only the reviewed fingerprint set
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `./scripts/run-quality.sh --release`
- bounded reviewer focused pytest, renderer probes, mirror comparison, and duplicate-ratchet readback

## Recommended Next Quality Moves

- active regenerate committed changed-line mutation proof — capability_needed=verification lock; next_center=committed remediation range; transformation=replace the explicit false-green warning with analyzed changed-line evidence; proof_boundary=`run_slice_closeout.py --produce-mutation-coverage --verification-lock`; enforcement_posture=existing-gate.
- passive revisit doc-clone and test-ratio advisories — capability_needed=maintainer prioritization; next_center=repo-wide economics; transformation=none until a concrete maintenance failure or budget trend makes them actionable; proof_boundary=advisory inventories; enforcement_posture=no-gate because current signals are proxies, not release defects.

## History

- [Prior pytest test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
