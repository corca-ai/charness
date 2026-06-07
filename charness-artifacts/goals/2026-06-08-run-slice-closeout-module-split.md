# Achieve Goal: Split the run_slice_closeout god-module under its file limit

Status: draft
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-run-slice-closeout-module-split.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation (a concrete behavior-preserving refactor).
Shaped now by `achieve`; inert until `/goal` activates it.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-08-run-slice-closeout-module-split.md`.
- Timebox: 4h
- Activation time: TBD (set at `/goal`)
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
| 1 | Map cohesive extraction units; pick the target module(s) + headroom target | Decide the split shape before moving code; lowest-risk seam first | recorded extraction map (reporting block first) + module name + target < 432 | planned |
| 2 | Extract the reporting/printing block to `slice_closeout_reporting.py`, rewire imports, sync mirror | The cleanest ~125-line seam drops the file under the warn band | `run_slice_closeout.py` < 432; mirror byte-synced; import-resolves in tree + export | planned |
| 3 | Prove behavior-preserving (output diff + closeout tests + broad gate) + fresh-eye critique | A refactor of a critical gate runner needs behavior proof | identical output diff; closeout tests + broad gate green; SHIP critique | planned |
| 4 | Closeout: doc/handoff sync, full gate, retro + disposition review | Make it auditable; no issue to close (internal follow-up) | full `run_slice_closeout.py` PASS; retro + disposition-review artifacts | planned |

## Coordination Cues

Phase routing is deferred to `find-skills` (`--recommend-for-task` /
`--recommendation-role <runtime|validation> --next-skill-id <skill>`); the routes
below are the *plan*, confirmed via `find-skills` during the run.

- **Routing (planned)**: Slice 1 → `impl` (design/extraction map); Slice 2 →
  `impl`; Slice 3 → `quality` + `critique`; Slice 4 → `quality` + `retro`.
  Confirm via `find-skills` and record the returned route at completion.
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

_None yet. File off-goal findings through `issue`; record only the reference and
reason here._

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. `python3 scripts/check_python_lengths.py --headroom --paths
   scripts/run_slice_closeout.py` — file < 432, no NEAR-LIMIT function.
2. `git log --oneline origin/main..HEAD` — the split commit(s); mirror synced.
3. Closeout tests + `./scripts/run-quality.sh --read-only` green.
4. Confirm a closeout run's output is identical to before the split.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
