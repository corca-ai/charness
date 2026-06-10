# Quality Review
Date: 2026-06-11

## Scope

Open `/charness:quality` posture pass on `main` at `v0.39.0` + 3 staged local
commits (763653c7 `Closes #349` carrier, bc70d76a, a6888927), slice 1 of the
`2026-06-10-overnight-quality-mainjob-350-then-push-release` achieve goal.
Prior artifact stale at `v0.24.1`: full re-derivation — gates, four lenses,
one bounded fresh-eye reviewer; deliverable = honest posture **plus a
prioritized candidate list scoping slices 2–5**. Routing `find-skills` →
`quality`. Concept lens: no architecture/ownership drift; the standing
tension this pass surfaces is **helper/closeout trustworthiness** (C2, C4).

## Current Gates

- `./scripts/run-quality.sh --read-only`: initially **71 passed, 2 failed**
  — `validate-handoff-artifact` (empty `## Discuss`) and
  `validate-retro-lesson-index` (stale index); both repaired this turn,
  re-run = **73/0, ~49s** (profile `local-linux-x86_64-36cpu`).
- The empty Discuss came from **bc70d76a** — the prior session's own
  goal-closeout commit, edited AFTER its final broad gate run, never
  pushed; exposure window = commit→push (pre-push would have caught it).
- `validate_usage_episodes.py`: 743 records; veto gaps stay visible
  (feedback_coverage 0% — #184 territory); attention-state visibility: 79
  files, no hidden exit-zero state. `plan_cautilus_proof.py`
  next_action=none → no eval; deterministic gates own closeout.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` this turn; profile
  `local-linux-x86_64-36cpu`; runtime visibility configured.
- runtime hot spots: `check-coverage` 43.5s latest / 43.7s median vs 45.0s
  budget (watch); `pytest` 19.7s/19.8s vs 140s; then
  `check-current-pointer-writes` 14.2s, `check-duplicates` 11.9s median.
- coverage gate: `check-coverage` is changed-path-gated and did not run this
  turn; last full-run sample brushes budget; `check-runtime-budget` PASS.
- evaluator depth: no live Cautilus (next_action=none); proof is
  deterministic gates + one bounded fresh-eye review.
- **Scheduled mutation lane (C3 evidence).** Run 27279937136 (768ded84)
  FAILED the changed-line blocking signal: fd3c2c6c..768ded84 changed 10
  eligible py files vs `max_files: 5` — budget-dropped by design. Same-SHA
  reruns 27290330577/27299766603 went green and auto-closed #351: real
  111-mutant samples but **vacuous on the changed-file proof arm** (base =
  previous run's headSha → empty diff; dropped files never re-proven).
  Noise: **47** "Mutation test regression" issues historically. Mitigation:
  the local pre-push changed-line gate is the primary lane.

## Healthy

- All 73 gates pass with real fail semantics on the staged tree.
- `inventory_lint_ignores.py`: blanket=0, file-level=0, all suppressions
  inline-scoped; codes remain E402-dominant + documented ANN001/BLE001 —
  zero production-logic suppressions.
- `inventory_public_spec_quality.py`: 4 specs, `source_guard_row_count`=0,
  `pointer_proof_marker_count`=0, thin `executable_block_count` (1+2+2+3=8)
  — no brittle guards, no proof duplicated at the wrong layer.
- `inventory_skill_ergonomics.py`: `checked_skill_count`=24 (hotl new since
  prior pass), `heuristic_finding_count`=17, `subcheck_counts` non-zero only
  for `host_surface_reference` (deferred portability advisory);
  `prose_review_status`=required.
- prose review result: spot pass over the 24 inventory rows — no
  trigger-overlap or prose-ritual smell; full prose re-read not redone
  (skill cores unchanged since 2026-06-06).

## Weak

- **C2 (BUG, reviewer-confirmed): `quality_bootstrap_lib.py` silently drops
  unknown adapter fields.** `bootstrap_adapter.py` rewrote
  `.agents/quality-adapter.yaml` this turn, deleting the live
  `standing_doc_provenance` and `changed_line_mutation_gate` blocks (both
  have active gate consumers) and all comments; `_load_existing_adapter_data`
  loads an allowlist only. Restored via `git checkout` before commit.
- `inventory_standing_test_economics.py` keeps rising: `test_file_count`=283
  (258 on 06-06), `nested_cli_file_count`=128 (was 118). Advisory-by-design;
  durable lever is still shrinking the release-only CLI lifecycle surface.

## Missing

- **C4: commit-time handoff validation wiring.** `staged_commit_gate_plan.py`
  and `.agents/surfaces.json` have no handoff entry, so a staged
  `docs/handoff.md` edit runs no validator until pre-push — exactly the
  bc70d76a window. Sub-second validator; fits the timing layer.
- **C3: scheduled-lane base/auto-close semantics** (see Runtime Signals).
  Constraints (reviewer): same-SHA dedup was deliberately removed
  (corca-ai/craken-agents#127); #341 made per-file-budget exclusions
  non-blocking — target base-selection/auto-close only.

## Deferred

- #184 (goal-excluded, seventh time; now a handoff Discuss decision item);
  `host_surface_reference` portability advisories; real-host `nose` proof.

## Advisory

- `inventory-nose-clones` (0.5.0): family_count=20, total_dup_lines=2156
  (1951 prior); top families remain intentional per-package
  `resolve_adapter.py` portability boilerplate (family #1 members=11
  dup_lines=100) — Non-Goals fence holds, not a candidate.
- `check_python_lengths`: 8 files in the advisory warn band (top: two test
  files at 758/798 vs limit 800) — trim nudges, exit 0; and
  `check-coverage` brushing its 45s budget — carried watch items.

## Delegated Review

- Delegated Review: **executed**. Tier `high-leverage`, read-only in the
  shared parent worktree. Verdict **REVISE → folded**: confirmed C2 (lib
  allowlist read) and C3 mechanism with precision corrections (greens
  vacuous only on the changed-file arm; noise history 47 not 20), corrected
  the Discuss attribution to bc70d76a, confirmed C4 is real wiring, kept
  the C2→C3→C4 ranking (C3 bounded to unit-testable script logic).

## Commands Run

- `find-skills` → `quality`; `resolve_adapter.py`, `bootstrap_adapter.py`
  (destructive rewrite observed + reverted = C2), `run-quality.sh
  --read-only` (x2), `plan_cautilus_proof.py`, `validate_usage_episodes.py`
  + report, attention-state visibility, `render_runtime_summary.py`,
  `check_python_lengths.py`; `gh` reads for the three scheduled runs.
- Inventories (fields engaged above): `inventory_standing_test_economics.py`,
  `inventory_skill_ergonomics.py`, `inventory_lint_ignores.py`,
  `inventory_public_spec_quality.py`, `inventory_nose_clones.py`. One
  bounded fresh-eye reviewer (read-only).

## Recommended Next Gates

- active `AUTO_CANDIDATE` (slice 3, C2): unknown-field-preserving rewrite
  (or refuse-without-force) in `quality_bootstrap_lib.py` + regression test;
  read-only sibling scan for the same allowlist-rewrite class.
- active `AUTO_CANDIDATE` (slice 4, C3): scheduled mutation lane — stop
  advancing base past budget-dropped backlog and/or gate auto-close on the
  changed-file arm being re-proven; honor craken-agents#127/#341.
- active `AUTO_CANDIDATE` (slice 5, C4): handoff entry in the staged commit
  gate plan / surfaces so staged handoff edits validate at commit time.
- passive watch: test-economics growth, coverage budget brush, warn-band files, #184 — watch items, not slices, because none is yet actionable.

## History

- [2026-06-06 quality review](history/2026-06-06-quality-review.md)
