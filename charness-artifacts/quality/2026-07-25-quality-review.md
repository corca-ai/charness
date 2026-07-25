# Quality Review
Date: 2026-07-25
Title: Quality Review

## Scope

Target boundary: repo-wide, with the operator's question narrowed to "any speed problems?" immediately before cutting a release. No target skill.

Ambient repo findings: none — the broad gate is 81 passed / 0 failed both before and after this turn's changes. Two guard failures appeared mid-turn and were caused by this turn's own edit, not found pre-existing.

## Current Gates

- Broad gate `./scripts/run-quality.sh --read-only`: 81 gates, 0 failures, 62.5s wall.
- Commit boundary: 22 pre-commit gates via `.githooks`; slice closeout adds sync + verify + locked broad pytest.
- Maintainer-Local Enforcement: **enforced** — checked-in `.githooks` plus `check_staged_worktree_consistency` / `check_staged_mirror_drift` at the commit boundary, and CI (`quality-core.yml`) mirrors a subset. Not a clone-pushable gap.
- Runtime budgets: enforced by `check_runtime_budget.py` against the machine-resolved profile.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: `run-quality-read-only-release` 86.4s latest / 81.4s median, `run-quality-full-release` 70.4s / 73.0s, `run-quality-full` 62.7s / 67.2s, `run-quality-read-only` 60.8s / 58.9s, `pytest` 42.6s / 41.8s. All now budgeted; before this turn the three slowest were not.
- serial gate cost: 109.8s summed across 81 gates against 62.5s wall (~10x parallelism). `pytest` is 42.5s of that 109.8s and is the critical path; every other gate is under 5s.
- test-surface shape (`inventory_standing_test_economics`): `test_file_count` 424, of which `nested_cli_file_count` is 182 — 43% of the suite drives a nested CLI, and only `nested_cli_all_release_only_file_count` 1 is fenced behind release-only. That ratio, not the worker count, is why the suite is subprocess-bound: `runner_snippets` confirms a single standing runner, so those 182 files run in the standing gate.
- coverage gate: run-quality pass, 81/0.
- evaluator depth: deterministic gates only. Cautilus planner reported `next_action: none` and repo policy is ask-before-run, so no live evaluator run is claimed.

## Healthy

- Parallelism is real, not nominal: 109.8s of serial gate work lands in 62.5s wall.
- No global lock, no `--dist` misconfiguration, no per-worker session-fixture N-times cost. The seed cache (`tests/seed_cache.py`) is filelock-guarded and content-hashed, so only one worker pays the repo-copy build.
- Structural waste (`inventory_structural_waste`): `duplicate_discovery_candidates` and `broad_scanner_candidates` are both empty across `python_source_count` 306 sources and `command_snippet_count` 12 snippets, so no gate re-walks the tree or parses before prefiltering. One advisory intra-test repeated read is the only finding.
- CI-recoverable gates: one candidate (`check-markdown`), already mirrored in CI, correctly kept local.
- Budget resolution is live, not dead config: `runtime_profile_default: default` resolves through `machine_runtime_profile()` to the x86_64 profile, and profile budgets replace rather than merge without silently dropping any top-level label.

## Weak

- The `pytest` runtime budget was **sized from a conflated sample window**. `run-quality.sh` recorded standing-mode (~42s) and release-mode (~62s) pytest under one label, and the 90000 bar was drawn from the release mode's max — so a 2x standing regression (~84s) would have landed under the bar and reported OK. Split into `pytest` / `pytest-release` this turn; the 90000 number is still loose for standing mode alone and is deliberately left for the slack advisory to retighten once the split window fills, rather than guessed at now from contaminated samples.
- `scripts/run-quality.sh` runs as five `flush_phase` barriers, and `pytest` is queued in the third. `flush_phase` is not fail-fast (every phase runs regardless of earlier failures), so the barriers buy output ordering plus one real data dependency (`doc-duplicates` -> `dup-ratchet`), while the 42s critical-path gate waits behind ~9s of cheap validators it does not depend on.
- The slowest single test was paying for a feature it never reads: `test_scaffold_changed_lines_read_covered_through_gate_probe` ran the coverage probe with the default `dynamic_context=True` while asserting only executed/missing lines. Fixed this turn (21.3s -> 15.4s for the file, assertions unchanged).

## Missing

- No "hot label with no budget" detector. `runtime_visibility_lib.py` fires only when the `budgets` map is entirely empty, so a slow label with no budget produces one advisory `HOTSPOT ... (unbudgeted)` line and nothing can ever fail on it. That is how the three release-path labels stayed unbudgeted; the labels are fixed, the detector gap is not.
- No invocation that restamps the dup-ratchet scanner version without absorbing debt. `_scoped_rebaseline` already restamps `tool_version` while structurally refusing unnamed live deltas, but `run()` dispatches to it only when `--accept-rotation`/`--accept-family` names at least one id, so a pure version restamp is unreachable.

## Deferred

- The nose 0.19.0 -> 0.20.0 baseline skew warning printed by `dup-ratchet` and `inventory-nose-clones` on every run. Verified it is a WARNING that never degrades the verdict (a block stays a block), so it costs noise, not teeth. `--write-baseline` is a full-scan overwrite that would silently re-accept every current family, and `docs/handoff.md` parks the #448 scoped-accept items for a dedicated dup-ratchet slice. Declining is the right call until that slice or the restamp seam above exists.
- Raising `DEFAULT_XDIST_WORKER_CAP` from 16: **refuted by measurement**, see Advisory.

## Advisory

- structural review result: no target skill was named, so the structural packet is answered at repo scope. The capability under review is "a maintainer can tell whether the gate that precedes a release got slower". Current centers: `check_runtime_budget` + the runtime-signals store. The center strengthened this turn is budget coverage of the release-path labels; the center left weak is the barrier layout in `run-quality.sh`. Enforcement posture for both moves is existing-gate-reuse, not a new floor.
- prose review result: not run — no skill trigger boundaries, progressive-disclosure, or dogfood-pressure findings arose, because the question was runtime economics and no public skill body changed beyond `state-selection.md` in the preceding slice.
- `doc-duplicates`: 8 new/changed Markdown families (26 total, 28 accepted). Top families are `goal_artifact_template.md` vs `auto_draft_goal.md` — intentional shared template shape, not single-sourceable drift. command: `./scripts/run-quality.sh --read-only`.
- `inventory-nose-clones`: 5 families, 1028 duplicated lines, ranked 20 of 647. Family #1 (22 members) is the portable `resolve_adapter.py` preamble copied per skill package — intentional portability boilerplate the interpretation block already names as its own blind spot. command: `./scripts/run-quality.sh --read-only`.
- `inventory_structural_waste`: one advisory intra-test repeated read. command: `python3 skills/public/quality/scripts/inventory_structural_waste.py --repo-root . --summary`.

## Delegated Review

- Delegated Review: executed — one bounded `bounded-reviewer` at the high-leverage tier, spawned with no host addressing name; findings returned inline. Rail-1 boundary snapshot taken before the spawn and verified `{"ok": true, "drift": []}` on return, before any fix was applied. It refuted the parent's stated reasoning for declining the worker-cap raise (low CPU% argues FOR oversubscription, not against; the 16-vs-32 A/B is the real evidence) and found the `pytest` label conflation, the `dynamic_context` waste, and five false positives in the preceding slice's handoff validator. Non-claim: `git show`/`log`/`diff` are outside the read-only envelope, so its release-readiness pass reviewed working-tree state, not the three commit diffs.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): all three delegated and answered — fixture economics (seed cache, no N-times cost), parallel critical path (the five-barrier layout and the 92%-non-scaling fit), duplicated proof (the 24.9s test is load-bearing and not redundant with its in-library sibling).

## Commands Run

- `./scripts/run-quality.sh --read-only` (three times: baseline, after the label split, final)
- the full pytest suite at 16 and at 32 xdist workers (110.2s vs 102.6s), plus a slowest-durations pass
- `render_runtime_summary.py --detail`, `inventory_standing_test_economics.py`, `inventory_standing_gate_verbosity.py`, `inventory_structural_waste.py`, `inventory_ci_recoverable_gates.py`
- `skills/public/quality/scripts/check_runtime_budget.py --runtime-profile local-linux-x86_64-36cpu`
- `plan_cautilus_proof.py --detail` (next_action: none; no evaluator run)

## Recommended Next Quality Moves

- active move `run-quality.sh` pytest out of the third `flush_phase` batch — capability_needed=a maintainer waits less for the same evidence; next_center=the barrier layout in `scripts/run-quality.sh`; transformation=queue `pytest` in the first batch so its 42s overlaps the ~9s of validators it has no dependency on, keeping only the real `doc-duplicates` -> `dup-ratchet` ordering; proof_boundary=three timed `--read-only` runs before and after, plus the existing `run-quality-read-only` budget; enforcement_posture=existing-gate-reuse. Estimated ~13% of wall, larger than the worker-cap raise that was refuted, and deliberately not bundled into a release turn.
- active retighten `pytest: 90000` once the split sample window fills — capability_needed=the standing pytest budget can fail on a real regression; next_center=`.agents/quality-adapter.yaml` x86_64 profile; transformation=resize from standing-only `max_recent` at the code's own 1.4x `SLACK_SUGGESTION_HEADROOM`; proof_boundary=`check_runtime_budget` slack advisory reporting the over-slack bar; enforcement_posture=existing-gate-reuse.
- active add a `--restamp-tool-version` path to `check_dup_ratchet.py` — capability_needed=clear a scanner-version skew warning without absorbing deferred debt; next_center=`_scoped_rebaseline`, which already restamps while refusing unnamed deltas; transformation=let `run()` dispatch to it with zero accepted ids; proof_boundary=a test proving a restamp with an unnamed live delta still refuses; enforcement_posture=existing-gate-reuse. Pairs with the #448 dup-ratchet slice.
- passive raise `DEFAULT_XDIST_WORKER_CAP` above 16 — capability_needed=none; next_center=none; transformation=none; proof_boundary=the 16-vs-32 A/B (110.2s vs 102.6s, ~7%); enforcement_posture=no-gate because measurement refuted it: ~92% of the suite's wall does not scale with worker count, so the lever is test-level (the release-only tail), not the cap.
- passive budget `run-quality-read-only-release` from a full window — capability_needed=a tighter bar than the deliberately loose 150000 set this turn; next_center=`.agents/quality-adapter.yaml`; transformation=resize at 1.4x once more samples exist; proof_boundary=`runtime-signals.json` sample count; enforcement_posture=no-gate until the sample window fills beyond the current two runs.

## History

- [prior review](2026-07-22-quality-review.md) · [portable proof-path learning review](history/2026-07-19-portable-proof-path-learning-review.md)
