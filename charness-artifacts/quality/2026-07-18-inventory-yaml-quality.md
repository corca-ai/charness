# Quality Review
Date: 2026-07-18
Title: Complete quality inventory YAML-first contract

## Scope

Target boundary: every quality `inventory_*.py` producer, every canonical inventory-dispatch command, their source/plugin ownership, and the cost of proving that interface.

Ambient repo findings: D18 remains ignored per operator direction. The broad gate exposed two stale tests, one redundant subprocess boundary, and duplicate-family fingerprint rotations; all were repaired or explicitly re-baselined before closeout.

## Current Gates

- Existing YAML-output contract, focused domain tests, ruff, source/plugin sync, packaging validation, boundary-bypass and duplicate ratchets, artifact validators, and repo read-only quality.
- No new standalone gate was added; the existing YAML contract test now owns structural population discovery and semantic parity.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; local default profile. <!-- reproduction-source -->
- runtime hot spots: final read-only quality completed 81 phases in 54.5s; pytest completed in 34.1s, both below their configured budgets.
- coverage gate: 4,765 standing tests passed for the YAML slice. The first release attempt then correctly blocked on nine cumulative `v2.0.0..HEAD` files whose changed lines were exercised only through subprocesses or not at all; behavior-focused in-process tests repaired the gap, and the verification-locked cumulative closeout passed with 4,780 standing tests plus 159 focused coverage tests.
- evaluator depth: deterministic-gates-only because encoding, flag conflicts, bounds, mirror parity, and exit behavior are directly observable; Cautilus is ask-before-run and was not executed.

## Healthy

- All 20 quality `inventory_*.py` producers and all 25 canonical dispatch commands expose compact bounded `--summary` YAML, full `--detail` YAML, and hidden JSON compatibility.
- Human defaults, exit codes, and explicit execution/write flags remain intact; Markdown recommendation mode rejects conflicting structured flags.
- One helper owns encoding selection and bounded-list projection; canonical source owns behavior and generated plugin commands byte-match it.
- The all-inventory contract module runs 25 tests in about 12.4s, down from 19.34s after source semantic execution and exact plugin-copy proof replaced duplicate execution.

## Weak

- The initial migration scoped the population from dispatch prose and left two undispatched inventories plus two detail-only commands outside the claimed capability.
- First-pass “compact” proof checked YAML/JSON equality but not oversized arrays; fresh-eye review found four unbounded diagnostic surfaces.
- Duplicate-family scanning cannot distinguish standardized per-command integration glue from extractable domain duplication without reviewer judgment.
- Per-slice coverage was green while the unreleased cumulative release range was not. The release boundary was the first consumer to join those slices, so it exposed a real process gap: unreleased-range proof must be refreshed before invoking the irreversible helper, not discovered inside it.

## Missing

- Before this slice, no structural test discovered every inventory producer from the filesystem while separately deriving every agent-facing dispatch consumer.
- Before fresh-eye review, no oversized fixture proved count/sample/truncation behavior and no test rejected Markdown combined with structured modes.

## Deferred

- A separate structured dispatch registry is not justified while the canonical backticked command syntax is stable and the existing test rejects duplicate/missing contract behavior.
- Removing hidden JSON or persisted JSON artifact seams would break programmatic consumers without improving first-read agent ergonomics.
- Fifteen Python files remain in advisory length warn bands; current review found no cohesive split that belongs in this interface slice.

## Advisory

- structural review result: capability_needed=bounded truthful inventory packets; current_centers=producer files, dispatch consumers, and generated plugin copies; next_center=filesystem producer discovery plus dispatch-derived consumers; transformation=semantic source proof and exact generated-copy proof; proof_boundary=live subprocess YAML/JSON equality, oversized fixtures, plugin bytes; enforcement_posture=existing-gate reuse under the north star.
- prose review result: `inventory_skill_ergonomics.py --summary` reported `checked_skill_count=22`, `heuristic_finding_count=16`, and `prose_review_status=required`. The quality trigger, progressive disclosure, target-vs-ambient split, and evaluator boundary remain unchanged; only inventory output guidance changed.
- command: `inventory_standing_test_economics.py --summary` found `test_file_count=399` and `nested_cli_standing_or_mixed_file_count=169`; this slice reduced its own expanded contract module instead of proposing broad test deletion.
- command: compact versus detail output measured 407/1,503 bytes for CLI ergonomics (72.9% smaller), 2,349/5,078 for runtime summary (53.7% smaller), and 1,918/2,533 for structural waste (24.3% smaller).
- command: duplicate ratchet reported 18 new families and three membership reductions after the coherent cross-command migration. Review classified them as standardized interface/bootstrap/domain pairing glue rather than a nameable shared domain owner; scoped re-baseline accepted 18 families and rotated three fingerprints, after which the ratchet passed.

## Delegated Review

- Delegated Review: executed — interface-semantics and structural-ownership reviewers plus a separate counterweight found three act-before-ship classes: conflicting Markdown modes, unbounded summaries, and incomplete semantic population proof. All were fixed; rechecks passed.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): re-delegated through structural review; the contract module fell from 19.34s to ~12.4s while increasing semantic coverage from the dispatch subset to every source inventory.
- Reviewer boundary fingerprints passed after each angle, counterweight, and fix-verification pass; details: `../critique/2026-07-18-complete-inventory-yaml-contract-and-v2-1-0-release.md`.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary`
- focused inventory/output suites — worker subsets 47, 153, 65, and 45 passed; final blocker-focused suite 55 passed.
- `pytest -q tests/quality_gates/test_public_skill_yaml_output_contract.py` — 25 passed in repeated 12.3–12.5s runs.
- `ruff check` over changed Python surfaces; `python3 scripts/sync_root_plugin_manifests.py --repo-root .`; `python3 scripts/validate_packaging.py --repo-root .`.
- `./scripts/run-quality.sh --read-only` — initial 78/3 surfaced stale contract expectations and ratchet drift; final 81 passed, 0 failed in 54.5s.
- first `publish_release.py --execute` attempt — stopped before commit/tag/push because release-only changed-line coverage found nine cumulative blockers.
- cumulative `run_slice_closeout.py --base v2.0.0 --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage ...` — completed; 4,780 broad tests and 159 focused in-process coverage tests passed, clearing the same release-range consumer.

## Recommended Next Quality Moves

- active release v2.1.0 through the repo helper — capability_needed=publicly consumable complete YAML contract; next_center=release helper; transformation=version/sync/tag/publish/install refresh; proof_boundary=release-only gate, fresh checkout, distinct public readback, real-host and installed-version proof; enforcement_posture=irreversible-boundary helper plus distinct observer.
- passive structured dispatch data until syntax drift is observed because capability_needed=drift-free consumer discovery; next_center=inventory-dispatch canonical notation; transformation=replace prose extraction only when a real second syntax appears; proof_boundary=current command extraction and semantic source proof; enforcement_posture=no-gate because another registry would add ownership without current escape risk.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
