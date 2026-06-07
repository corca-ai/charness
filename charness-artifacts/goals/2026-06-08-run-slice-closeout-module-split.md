# Achieve Goal: Split the run_slice_closeout god-module under its file limit

Status: complete
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-run-slice-closeout-module-split.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation (a concrete behavior-preserving refactor).
Shaped now by `achieve`; inert until `/goal` activates it.

## Active Operating Frame

- Current slice: COMPLETE — all 4 slices landed; reporting block extracted,
  behavior-preserving, mirror synced, read-only gate 73/0, critique SHIP,
  disposition review genuine.
- Next action: maintainer push (`achieve` does not push) — the split commit is 1
  of 2 ahead of `origin/main` (with the goal-shaping commit `187d617e`); the #332
  closeout is already on `origin/main`.
- Timebox: 4h
- Activation time: 2026-06-07T22:47:00Z
- Closeout reserve: 45m
- Done-early policy: continue_next_improvement (re-point to #184 with an explicit
  ideation/spec scope reset, not a quick slice).
- Verification cadence: cheap deterministic checks at commit boundaries
  (py_compile / ruff / check_python_lengths file+function / mirror sync); a
  behavior-preservation output diff + targeted closeout tests at slice
  boundaries; broad gate + one fresh-eye critique at the bundle boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Split `scripts/run_slice_closeout.py` (currently **474/480** tokei code lines —
inside the advisory warn band [432, 480]; the next closeout addition breaches the
480 hard limit) into the orchestrator plus one or more cohesive helper modules,
**behavior-preserving**, so the file returns comfortably below its warn band
(target < 432, with headroom for future closeout additions) and no function sits
near its 100-line limit. The leading extraction is the reporting/printing block
(`_print_list`, `_cautilus_plan_has_visible_work`, `_print_cautilus_plan`,
`_print_risk_interrupt_plan`, `_print_executed_commands`, `_print_headroom`,
`_print_usage_episode`, `print_text` — ~125 code lines) into a new
`scripts/slice_closeout_reporting.py`; extend to the blocking-helper chain
(`_maybe_block_on_*` + `_run_preexecution_blocks`) only if more headroom is
needed. The plugin export mirror (`plugins/charness/scripts/`) stays byte-synced
and the new module resolves via `import_repo_module` / parent-walk in BOTH the
source tree and the exported plugin.

## Non-Goals

- Do NOT change any closeout behavior, output text, gate ordering, exit codes, or
  the predict-commit / structural-sweep / broad-pytest logic (#332 just landed
  those). This is a purely structural move.
- Do NOT redesign the gate framework, the surfaces manifest model, or the
  `mutate → sync → verify → publish` rhythm.
- Do NOT split other near-limit files; `staged_commit_gate_plan.py` has ample
  headroom (341/480). This is `run_slice_closeout.py`-only.
- Do NOT change the public CLI surface or the importable symbols other modules
  rely on (`run_command`, `run_predict_commit` re-export, etc.).
- Not a broad de-duplication / nose-clone refactor.

## Boundaries

- Behavior-preserving: the full closeout, `--predict-commit`, and broad-pytest
  paths produce identical output; all closeout-touching tests stay green; a
  before/after closeout output diff is byte-identical.
- Export-safe: the new module ships to `plugins/charness/scripts/` and resolves
  via `import_repo_module` / parent-walk in both tree and export (mirror
  byte-identical; `check_export_safe_imports` + plugin-import-smoke green).
- Presence/structural: move code, do not rewrite logic; keep function
  signatures + module-level importable names stable.
- External side-effect scope: none — local refactor; `achieve` does not push. No
  version bump or install-manifest edit (the plugin mirror sync is not a release).
- Discuss before activation: resolved — no consequential defaults. This is a
  behavior-preserving local refactor: no live/prod/provider proof, no issue
  close/split, no irreversible side effect, and no broad multi-issue scope. The
  split granularity (one reporting module vs also extracting the block chain) is a
  Slice-1 design decision, not an activation blocker.

## User Acceptance

What the user can do to verify completion directly:

- Run `python3 scripts/check_python_lengths.py --headroom --paths
  scripts/run_slice_closeout.py scripts/slice_closeout_reporting.py` and see
  `run_slice_closeout.py` comfortably below the warn band (< 432) with the new
  module also under its limit and no NEAR-LIMIT function.
- Run the closeout-touching tests + `./scripts/run-quality.sh --read-only` and
  see them green; confirm the plugin mirror is byte-synced.
- Run a full closeout (or compare the test fixtures) before and after and confirm
  the output is identical (behavior-preserving).

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` (file + function) on the changed
  files at each commit boundary.
- Targeted closeout-touching pytest modules
  (`test_staged_commit_gate_plan.py`, `test_surface_obligations.py`,
  `test_slice_closeout_*`, `test_closeout_headroom_and_mirror_gate.py`).
- `check_export_safe_imports` + plugin-import-smoke; mirror byte-sync.

### High-Confidence Checks

- Broad pytest (the full closeout suite) at the bundle boundary.
- A before/after closeout **output diff** proving byte-identical behavior (the
  central behavior-preservation proof for moving a critical gate runner).
- One bounded fresh-eye `critique` at the extraction boundary (behavior-
  preservation + export-safety risk) with the slice packet.

### External Or Live Proof

- None required. Local structural refactor; no live/prod/provider proof, no
  deploy, no remote CI watch is claimed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Map cohesive extraction units; pick the target module(s) + headroom target | Decide the split shape before moving code; lowest-risk seam first | recorded extraction map (reporting block first) + module name + target < 432 | done |
| 2 | Extract the reporting/printing block to `slice_closeout_reporting.py`, rewire imports, sync mirror | The cleanest ~125-line seam drops the file under the warn band | `run_slice_closeout.py` 474→370/480; mirror byte-synced; import resolves in tree + export | done |
| 3 | Prove behavior-preserving (output diff + closeout tests + broad gate) + fresh-eye critique | A refactor of a critical gate runner needs behavior proof | byte-identical move + 10+11 renderer-equivalence batteries; 99 targeted tests + 73/0 read-only gate; SHIP critique | done |
| 4 | Closeout: doc/handoff sync, full gate, retro + disposition review | Make it auditable; no issue to close (internal follow-up) | handoff synced; read-only gate 73/0; retro + disposition-review (genuine) artifacts; #334 filed | done |

## Coordination Cues

Phase routing is deferred to `find-skills` (`--recommend-for-task` /
`--recommendation-role <runtime|validation> --next-skill-id <skill>`); the routes
below are the *plan*, confirmed via `find-skills` during the run.

- **Routing:** `find-skills` routed `impl` + `quality` + `critique` + `retro` + `issue` (#334) — local-first, no adapter override; planned route held.
  - `impl` (Slice 1–2 extraction); `quality` (`run-quality.sh --read-only` + targeted closeout tests); `critique` (3 angle + 1 counterweight fresh-eye subagents at the extraction boundary, plus a fresh-eye disposition review); `retro` (session); `issue` (#334 off-goal finding).
- **Gather: n/a — no external URL/Slack/Notion/Docs/Drive source; shaped from the
  #332 retro follow-up and local repo files only.**
- **Release: n/a — behavior-preserving structural refactor; no version bump or
  install-manifest edit (the plugin mirror sync is generated-surface upkeep, not a
  release).**
- **Issue closeout: n/a — no tracked GitHub issue; this is the internal
  `follow-up:run-slice-closeout-module-split` deferred from the #332 retro
  (deliberately not filed to avoid issue sprawl).**

## Slice Log

_No slices yet. Activation (`/goal`) flips status to `active` and begins Slice 1._

### Slice 1: Slice 1 — extraction map

- Objective: Map cohesive extraction units; pick target module + headroom target before moving code.
- Why this approach: Reporting/printing block is the cleanest cohesive seam (8 fns, ~105 tokei code lines, lines 171-294), self-contained (only print + payload dict + one imported helper), zero external import consumers — lowest-risk move.
- Commits:
- What changed: Recorded map only (no code change this slice).
- Alternatives rejected: Also extracting the _maybe_block_on_* chain — deferred; reporting block alone drops the file well under the warn band, so no need yet.
- Targeted verification: Read full file; grep confirmed reporting symbols have no external importers; tests import only run_command/SurfaceError/_resolve_broad_producer (all stay in orchestrator); captured before-baselines A/B/C for the Slice-3 output diff.
- Test duplication pressure:
- Critique: short — local structural map, behavior-preservation + export-safety folded into Slice 3 plan.
- Off-goal findings:
- Lessons carried forward: New module's only cross-dep is print_broad_pytest_policy (from slice_closeout_broad_gate), re-imported via import_repo_module; print_text re-exported from orchestrator to keep the module attribute stable.
- Metrics:

### Slice 2: Slice 2 — extract reporting block

- Objective: Move the 8 reporting fns to scripts/slice_closeout_reporting.py, rewire orchestrator imports, sync the plugin mirror.
- Why this approach: Deterministic byte-preserving migration script (not committed) guarantees the moved fns are character-identical to originals — strongest behavior proof for a pure move.
- Commits:
- What changed: NEW scripts/slice_closeout_reporting.py (119/480); run_slice_closeout.py 474->370/480; orchestrator drops unused print_broad_pytest_policy re-export, adds print_text re-export from the new module; mirror synced to plugins/charness/scripts/.
- Alternatives rejected: Hand-transcribing the block (rejected: transcription risk on 105 lines); also extracting the _maybe_block_* chain (rejected: 370/480 already well under the 432 warn band, no need).
- Targeted verification: byte-identity vs HEAD block = True; py_compile OK; ruff All checks passed (confirms dropped import truly unused); check_python_lengths file+function (no NEAR-LIMIT); import smoke (print_text/run_command/SurfaceError/_resolve_broad_producer/run_predict_commit all importable); export-safe-imports 443 files; mirror byte-diff IN SYNC; export-tree parent-walk import smoke True; output diff A/B/C (B+JSON identical modulo the intended 474->370 headroom drop); renderer equivalence battery: ALL 10 branches byte-identical old-vs-new; 99 targeted closeout tests passed.
- Test duplication pressure: none — pure move; no new logic to test. Existing closeout tests already pin run_command/_resolve_broad_producer behavior.
- Critique: deferred to Slice 3 fresh-eye bounded reviewer (next).
- Off-goal findings:
- Lessons carried forward: print_broad_pytest_policy was NOT part of run_slice_closeout's import contract (no external consumer); dropping its re-export is safe and ruff-confirmed. print_text re-exported to keep the module attribute stable.
- Metrics:

### Slice 3: Slice 3 — behavior proof + fresh-eye critique

- Objective: Prove behavior-preserving and run the bounded fresh-eye critique at the extraction boundary.
- Why this approach: A critical gate-runner refactor needs an old-vs-new output proof plus an independent fresh-eye pass before locking in.
- Commits:
- What changed: No code change; added critique artifact charness-artifacts/critique/2026-06-08-run-slice-closeout-reporting-extraction.md + prepare packet.
- Alternatives rejected:
- Targeted verification: Renderer equivalence battery (parent): 10 branches byte-identical old-vs-new. Counterweight independent 11-payload battery on guard branches: 0 mismatch. _emit_payload byte-identical (exit-code rule + --json path untouched). 99 targeted closeout tests green.
- Test duplication pressure:
- Critique: full — 3 angle (Jackson/Weinberg/Gawande) + 1 counterweight bounded fresh-eye subagents; parent-delegated. Triage: Act-Before-Ship=none; Bundle=commit goal+critique artifacts with code (planned); Over-Worry=dropped-re-export/circular-import/missed-branch (all falsified); Defer=none. Verdict SHIP.
- Off-goal findings:
- Lessons carried forward: Counterweight that BUILDS an independent guard-branch battery (not just triages paranoia) is the high-value adversarial pass for a pure-move refactor — it re-proves preservation rather than restating it.
- Metrics:

### Slice 4: Slice 4 — closeout

- Objective: Doc/handoff sync, broad gate, retro + disposition review, complete the goal.
- Why this approach: Make the behavior-preserving split auditable and gate-clean before completion.
- Commits:
- What changed: docs/handoff.md (follow-up marked done; split recorded as awaiting push); retro persisted (recent-lessons + lesson-index refreshed); critique + disposition-review artifacts; goal Final Verification/Auto-Retro/Off-Goal filled; issue #334 filed.
- Alternatives rejected:
- Targeted verification: run-quality.sh --read-only 73 passed / 0 failed (after adding the validator-required Reviewer Tier Evidence section to the critique artifact). validate_critique_artifacts green. Fresh-eye disposition review: dispositions-genuine.
- Test duplication pressure:
- Critique: full — fresh-eye disposition review (rung 2) returned dispositions-genuine; the Slice-3 extraction critique returned SHIP.
- Off-goal findings: issue #334 — critique skill should cite scaffold_critique_artifact.py so hand-authored critique artifacts carry Reviewer Tier Evidence by construction.
- Lessons carried forward: A charness critique artifact MUST carry a ## Reviewer Tier Evidence section (4 fields; host-exposure-state from a fixed enum) or validate_critique_artifacts fails — consult the validator/scaffold before hand-authoring.
- Metrics:

## Context Sources

Follow these in order to reconstruct the goal from a cold start:

1. The #332 retro + critique where this follow-up was registered:
   `charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`,
   `charness-artifacts/critique/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md`.
2. The subject + mirror: `scripts/run_slice_closeout.py`,
   `plugins/charness/scripts/run_slice_closeout.py`.
3. Behavior pins: `tests/quality_gates/test_staged_commit_gate_plan.py`,
   `tests/quality_gates/test_surface_obligations.py`,
   `tests/quality_gates/test_slice_closeout_*`,
   `tests/quality_gates/test_closeout_headroom_and_mirror_gate.py`.
4. `docs/conventions/implementation-discipline.md` (mirror sync, generated
   surfaces, `mutate → sync → verify` barrier, near-limit advisory).
5. `scripts/staged_commit_gate_plan.py` — the #332 single-source extraction
   pattern, a model for clean module boundaries.

## Interview Decisions

- **Which goal (asked 2026-06-08).** Family: {#184 product metrics,
  run_slice_closeout split, both-in-sequence}. Chosen: *run_slice_closeout split*
  (concrete, ready follow-up; unblocks the near-limit file before the next
  closeout edit breaches the limit). Rejected: #184 (product-level, needs
  `ideation`/`spec` + a `gather` of its Slack source — a separate larger goal).
- **Split shape (strong default, not asked).** Family: {reporting-block only,
  reporting + block-chain, full decomposition}. Default: *reporting-block first*
  (clearest cohesive seam, ~125 lines, drops well under the warn band); extend to
  the block chain only if more headroom is needed. Recorded as a Slice-1 design
  decision, not pre-committed — anti-anchoring: `axis: extraction-seam cohesion`.
- **Mode (not asked; strong default).** implementation-continuation — concrete
  refactor; shaped now, pursued at `/goal`.

## Plan Critique Findings

Self-critique (Before-phase). A fresh-eye slice critique runs at the Slice 3
behavior-preservation boundary per the verification plan.

- **Behavior-preservation is the central risk (folded).** Moving a critical gate
  runner could silently change output/ordering. Folded: Slice 3 requires a
  byte-identical before/after closeout output diff + the full closeout test suite
  + a fresh-eye critique.
- **Export-safety risk (folded).** The new module must resolve in the exported
  plugin, not just the source tree. Folded into Boundaries + Slice 2
  (`check_export_safe_imports` + plugin-import-smoke + mirror byte-sync).
- **Importable-symbol stability (folded).** Tests/other modules import
  `run_command` etc. from `run_slice_closeout`; the extraction must keep those
  names importable (re-export if moved). Folded into Non-Goals + Boundaries.
- **Over-worry, not folded.** Whether to also split `staged_commit_gate_plan.py`
  — no; it has headroom (341/480), out of scope.

## Off-Goal Findings

- **issue #334** (https://github.com/corca-ai/charness/issues/334) — the critique
  skill's documented authoring path does not cite its existing
  `scaffold_critique_artifact.py`, so a hand-authored critique artifact silently
  omits the `validate_critique_artifacts`-required `## Reviewer Tier Evidence`
  section until gate time. Surfaced in this goal's Slice-4 closeout (the first
  critique-artifact draft failed the read-only gate). Out of scope for this
  behavior-preserving refactor; filed for tracking, not fixed here.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md
Host log probe: charness-artifacts/retro/2026-06-08-run-slice-closeout-host-log-probe.md
Disposition review: charness-artifacts/critique/2026-06-08-run-slice-closeout-disposition-review.md
Early close rationale: a single behavior-preserving seam completed with full proof in ~40 min, far inside the 4h timebox; no in-scope slice remains (file at 370/480, block-chain split is a Non-Goal), so the goal closes early rather than manufacturing filler.
Early close report: charness-artifacts/goals/2026-06-08-run-slice-closeout-early-close-report.md

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. `python3 scripts/check_python_lengths.py --headroom --paths
   scripts/run_slice_closeout.py` — file < 432, no NEAR-LIMIT function.
2. `git log --oneline origin/main..HEAD` — the split commit(s); mirror synced.
3. Closeout tests + `./scripts/run-quality.sh --read-only` green.
4. Confirm a closeout run's output is identical to before the split.

## Auto-Retro

Retro:
[charness-artifacts/retro/2026-06-08-run-slice-closeout-module-split.md](../retro/2026-06-08-run-slice-closeout-module-split.md)

Surfaced-improvement dispositions (every retro Next-Improvement → `applied:` or `issue #N`):

- **issue #334** — critique skill should cite its `scaffold_critique_artifact.py`
  (or have prepare-packet emit a stub) so hand-authored critique artifacts carry
  the validator-required `## Reviewer Tier Evidence` by construction. Covers the
  retro's `workflow` (consult validator before hand-authoring) and `capability`
  (wire the scaffold) improvements — both are the same discoverability gap, now
  tracked. Out of scope to apply in this behavior-preserving goal.
- **applied: memory** — the lesson is persisted to
  `charness-artifacts/retro/recent-lessons.md` via `persist_retro_artifact.py`
  (summary + lesson-selection-index refreshed this run) so the next critique
  author inherits it.

No other actionable improvement surfaced; the refactor itself shipped with no
deferred follow-up of its own.
