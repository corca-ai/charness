# Quality Review
Date: 2026-07-15
Title: Session Routing and Catalog CLI Repair

## Scope

Target boundary: the copied global CLI catalog backend and the session/setup
routing contract that directs agents to the matching workflow or exact inventory.

Ambient repo findings: the first locked broad run surfaced two adjacent contract
gaps: a Charness-management detector that hid missing policy findings, and a
missing handoff link to the current retro digest. Both are repaired in this slice.

## Current Gates

- Focused routing, setup inspection/rendering, retro memory, and copied-CLI tests: 71 passed.
- The maintained `setup-compact-skill-routing-discoverability` scenario passed
  after asserting the direct workflow, exact catalog, and nonzero-result actions.
- The first locked broad run found the two contract gaps above after its other
  deterministic gates passed; the final locked closeout is the release-quality
  proof for this repaired working tree.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: `run-quality-full-release` 80.2s latest / 76.1s median; `run-quality-read-only` 56.5s latest / 56.7s median.
- coverage gate: focused tests and the maintained setup scenario pass; locked closeout runs changed-line mutation proof.
- evaluator depth: deterministic gates plus maintained scenario review; Cautilus execution is ask-before-run and no explicit evaluation request was made.

## Healthy

- The copied-CLI subprocess executes `catalog list` through the managed checkout.
- Hook, AGENTS, renderer, default surface, semantic inspector, and plugin mirror
  carry the same direct-action contract.
- The evaluator scenario now proves the compact-routing contract without adding
  another scenario identifier.
- Charness-management detection now stays distinct from the complete routing
  contract, so missing Dynamic Workflows and Codex profile policies remain visible.

## Weak

- Runtime metrics are historical machine samples and do not measure this small
  routing change directly.

## Missing

- No released-install or already-open-host-session readback is in this source-slice proof boundary.

## Deferred

- A live Cautilus evaluation awaits an explicit log-backed behavior proof request.

## Advisory

- structural review result: command: `python3 scripts/check_skill_surface_preflight.py --path skills/public/setup/references/default-surfaces.md --run-checks`; all targeted portable-package checks passed.
- prose review result: fresh-eye reviewers found the final parser order resolution sound; artifact: `charness-artifacts/critique/2026-07-15-critique-review.md`.
- scenario review: artifact: `evals/cautilus/scenarios.json`; the maintained compact-routing scenario already owns this consumer contract, so its assertions changed and its registry IDs remained stable.

## Delegated Review

- Delegated Review: executed — independent reviewers covered installed-CLI portability, routing wording, counterweight, and final parser resolution; boundary fingerprints reported no drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not re-delegated because this slice changes neither gate topology nor runtime recommendations.

## Commands Run

- `pytest -q tests/test_session_start_routing.py tests/quality_gates/test_setup_render_skill_routing.py tests/quality_gates/test_setup_inspect_policy.py tests/charness_cli/test_codex_cache_refresh.py`.
- `python3 scripts/run_evals.py --scenario setup-compact-skill-routing-discoverability`.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .` and setup skill-surface preflight.
- `pytest -q tests/quality_gates/test_retro_memory.py tests/quality_gates/test_setup_inspect_critique_adapter.py tests/quality_gates/test_setup_inspect_policy.py tests/quality_gates/test_setup_render_skill_routing.py tests/test_session_start_routing.py tests/charness_cli/test_codex_cache_refresh.py`.

## Recommended Next Quality Moves

- passive released-install readback because source-slice proof cannot update an already installed executable or open host session — capability_needed=operator update confidence; next_center=release workflow; transformation=verify after authorized publication; proof_boundary=installed binary and new session; enforcement_posture=release-gate.

## History

- [Previous quality review](history/2026-07-14-open-issue-resolution-proof.md)
