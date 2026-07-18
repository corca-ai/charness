# Quality Review
Date: 2026-07-19
Title: Release evidence boundaries and fast local feedback

## Scope

Target boundary: autonomously improve release correctness, evidence-token density, and standing-test feedback while preserving judgment-first behavior and stronger proof only at publication/issue-close boundaries.

Ambient repo findings: D18 remains intentionally ignored. Seventeen near-limit files, six stale runtime labels, and the broad test/production ratio are review prompts, not failures attributable to this slice.

## Structural Packet

- capability_needed: maintainers need compact release plans, recoverable irreversible effects, and cheap local contract feedback without parallel sources of truth.
- sequencing_applicability: release evidence must remain `mutate -> sync -> verify -> publish`; test optimization is reversible but must restore process-global state.
- current_centers: release state machine, immutable Git delta, inventory output contract, and repo-owned quality runner.
- next_center: one owner per cross-process evidence boundary, with delivery-boundary smokes kept thin.
- quality_move_card: move range identity/path serialization into one helper; move repeated inventory assertions in-process; retain real Git, subprocess, public HTTP, and installed readbacks where those channels add evidence.
- enforcement_posture: reuse existing gates and focused regressions; add no broad hard floor.

## Current Gates

- Focused release suites cover pre-publication issue-close ordering, resume identities, ambiguous push recovery, SHA-1/SHA-256 ranges, unusual filenames, YAML detail output, and compact planner/checker equivalence.
- The inventory contract test checks all 20 quality inventories in-process and retains one real subprocess entrypoint smoke.
- Packaging/mirror, ruff, compile, artifact, secret, boundary-bypass, and broad read-only quality checks own portable closeout; release publication adds distinct observer/readback channels.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: read-only quality latest/median 56.4/58.2s against 90s; pytest latest/median 35.7/43.5s against 140s.
- coverage gate: focused repair packet 60 passed; read-only quality passed; locked broad and changed-line mutation proof remain pre-release barriers.
- evaluator depth: deterministic-gates-only; Cautilus planner required no run, so no live evaluator claim is made.

## Healthy

- Issue close keywords cannot reach the default branch until public release, observer artifact, and distinct evidence exist; recovery distinguishes response loss from proven remote absence.
- A release plan now carries range identity, count, digest, trigger hits, and checklist instead of 137 repeated paths: measured output fell from 23,533 to 7,061 bytes and its gate command from 8,108 to 175 characters.
- Git itself validates full commit identities; one NUL-delimited delta owner serves planner and checker across SHA-1, SHA-256, and newline-containing filenames.
- The 60-call inventory contract loop fell from 4.44s pytest / 4.78s wall to 0.84s / 1.16s in the original controlled comparison while preserving a real entrypoint smoke.
- Final fresh-eye repairs removed SHA-width assumptions and exception-unsafe `sys.modules` residue; the boundary fingerprint showed no reviewer mutation.

## Weak

- `publish_release_helpers.py` remains cohesive but has only 24 code lines before its hard length limit; the new delta owner stopped further accretion but did not split older tag/version concerns.
- The worktree-only changed-path collector remains line-oriented; the NUL-safe guarantee is deliberately scoped to immutable release deltas.
- The process loader cache retains 20 test-private module objects; repeated runs are isolated, but no persistent-memory ceiling is claimed.
- The first mutation-instrumented locked suite took 164.1s against a 120s advisory budget and caught four optional-ancestry/delta-test failures after 4,912 passes; correctness was repaired, while gate-baseline profiling is deferred explicitly.
- The second locked broad suite passed 4,916 tests in 141.9s, but changed-line proof still rejected 29 failure/recovery lines. Direct behavior tests now own those branches; no coverage exclusion or baseline was added.

## Missing

- No missing blocking gate was found for this slice. Public publication and installed-host evidence cannot exist until execute time and must not be pre-claimed.

## Deferred

- Consider moving markdown validation off the local critical path only after confirming CI runs the identical scope; token matching alone is insufficient evidence.
- Split older release tag/version discovery from the near-limit helper when that concept next changes, not as an unrelated pre-release rewrite.

## Advisory

- structural review result: artifact: `charness-artifacts/critique/2026-07-19-critique-review.md`; fix boundary ownership rather than adding compensating checks, and keep release teeth at irreversible effects.
- prose review result: command: `inventory_skill_ergonomics.py --summary`; all 16 skill findings are intentional host/adaptor references. Core overfill, mode pressure, prose ritual, path ambiguity, issue/date anchors, undiscoverable references, and missing argparse help are zero.
- runtime review result: command: `inventory_standing_test_economics.py --summary`; 404 test files and 158 standing nested-CLI files are broad prompts. This slice removes only a measured redundant subprocess fan-out and preserves delivery smoke coverage.
- structural waste result: command: `inventory_structural_waste.py --summary`; duplicate discovery, broad scanner, and repeated stable-file-read candidates are all zero.

## Delegated Review

- Delegated Review: executed — independent release-state, planner portability, and test-isolation reviews found two blockers; both were repaired and re-reviewed with no remaining blocker.
- Parent fingerprints verified no worktree/index/HEAD drift. Slow-gate lenses: fixture-economics favored in-process inventory assertions; parallel-critical-path stayed serial at mutation/sync/verify; duplicated-proof review retained only distinct seam evidence.

## Commands Run

- `./scripts/run-quality.sh --read-only`: passed; latest measured 56.4s.
- Focused release/planner/YAML suites: 60 passed in 15.75-15.83s after repair.
- Inventory output test file: 26 passed in 8.82s; repeated-interpreter isolation probe passed twice.
- SHA-256 repository and newline-path regression passed; public/plugin release mirrors are byte-identical.
- `run_slice_closeout.py --skip-broad-pytest`: completed after sync, packaging, docs, secrets, ruff, compile, scan hygiene, and boundary checks.

## Recommended Next Quality Moves

- active prove the locked mutation set before release — capability_needed=changed-branch confidence; next_center=existing closeout producer; transformation=changed-line mutation coverage; proof_boundary=repo-owned coverage consumer; enforcement_posture=existing-gate-reuse.
- passive split legacy release tag/version discovery when it next changes because speculative movement now would add release risk without new behavior — capability_needed=helper headroom; next_center=tag discovery; transformation=cohesive extraction; proof_boundary=existing release suites; enforcement_posture=no-gate.
- passive revisit local markdown cost only after exact CI-scope equivalence is observed because current inventory supplies token correlation, not proof — capability_needed=faster local gate; next_center=quality routing; transformation=conditional relocation; proof_boundary=CI/local command equivalence; enforcement_posture=no-gate.

## History

- [Prior archived quality review](history/2026-07-14-open-issue-resolution-proof.md)
