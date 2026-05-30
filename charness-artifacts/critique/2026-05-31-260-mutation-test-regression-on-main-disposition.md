# Disposition critique — Goal #260: Mutation test regression on main

Bounded fresh-eye reviewer, `critique` discipline, read-only in the shared parent
worktree. #253 disposition-gate rung-2 (substantive judgment beyond the regex floor).

## Disposition verdict

1. **Defensive restore in `run_cosmic_ray_mutation.py` → issue #262** —
   **genuinely-filed.** `gh issue view 262 --repo corca-ai/charness` exists (OPEN,
   author spilist), titled "run_cosmic_ray_mutation: defensively restore
   module-path files on exit/interrupt". Observed-problem cites the exact
   `render_cli_reference.py:102` `repo_root >> args.output` leak and the
   try/finally + signal-handling fix; Disposition section names the #260 retro as
   source and marks it deferred next-session pickup. Matches the Auto-Retro claim.

2. **New pool files must clear BOTH floors → applied (teeth 100% line + 90.1%
   mutation)** — **genuinely-applied (real teeth, not prose).** The script
   `scripts/check_changed_line_mutation_coverage.py` (142 lines) and
   `tests/quality_gates/test_changed_line_mutation_coverage.py` (204 lines) are
   both real, added in commit `c35e028`. Ran
   `python3 -m pytest -q tests/quality_gates/test_changed_line_mutation_coverage.py`
   → **7 passed**. The test file covers exactly the claimed branches:
   `test_resolves_relative_coverage_json_under_repo_root` (the line-102-style Div
   dogfood that hardened 70.4%→90.1%), `test_no_base_sha_is_non_blocking_by_
   construction` (B1), `test_flags_uncovered_changed_lines` (exit-1 path),
   `test_passes_when_changed_lines_are_covered` (clean tree), untracked-file,
   no-eligible-change, runs-probe-when-not-reusing. The 100% line / 90.1% mutation
   figures are not cheaply re-verifiable without a full mutation run, but the
   in-session work is genuine: a real script + a dedicated 7-test wiring suite that
   demonstrably passes. Applied claim is honest.

3. **Persist lessons → applied (recent-lessons + lesson-selection-index)** —
   **genuinely-applied.** `git diff charness-artifacts/retro/recent-lessons.md`
   shows it was refreshed: Current Focus now leads with the #260 goal; Repeat Traps
   added the timeout-killed-exec, dump-parsing-slip, and polling-cadence lessons;
   Next-Time Checklist added the defensive-restore capability + the both-floors
   workflow + the memory-persist line; Sources now lists
   `2026-05-31-260-mutation-test-regression-on-main.md`. Every new line is
   source-attributed to this goal's retro. `lesson-selection-index.json` is also
   modified (working tree). Both transferable lessons (timeout-killed exec leaves a
   mutation; new pool file must clear both floors) are present.

## Closeout honesty

- **Score-path proof — confirmed honest.** Goal claims 22 survivors killed via a
  LOCAL targeted scoped re-run → `check_mutation_score.py` 100.0% / 101 executed /
  PASS. The cited score-path behavior tests run green:
  `pytest tests/quality_gates/test_command_docs_gate.py
  tests/test_markdown_preview_support.py` → **18 passed** (matches the goal's "18
  passed"). The relative-output, run_help signal-death, and glow mocked-payload
  tests exist in commit `0c53a59` and target exactly the named mutated branches.
  No CI/dispatch/live score proof is claimed.
- **Blocking-path proof — confirmed honest.** Proven by
  `classify_changed_line_scope_gap` over base `9565b92`..head `454f7dd` (0
  blocking) + the new teeth (flags pre-fix coverage exit 1, clean exit 0), with CI
  confirmation explicitly deferred to the next scheduled cron. Not overclaimed.
- **Dispatch marked NOT RUN — confirmed.** Final Verification and the "NOT
  claimed" block state plainly: no `workflow_dispatch` run, no push, #260 not
  closed via `gh`; the `Closes #260` is staged in the closeout commit body for the
  maintainer's push. The B1 reasoning (dispatch computes no `base_sha`, so it could
  never prove the blocking path) is correctly carried forward.
- **#219 not-subsumed — confirmed.** `gh issue view 219` shows OPEN; its 38
  survivors are in `scripts/validate_rca_ledger.py` + the `artifact_closeout_status`
  cluster (`scripts/artifact_closeout_lib.py`) — a file set entirely distinct from
  #260's render/glow survivors. Goal correctly leaves it open with that reason; no
  false subsumption.
- **#261 filed — confirmed.** `gh issue view 261` exists (OPEN), scoped to the
  trio's ~70 latent survivors, explicitly NOT part of #260's measured FAIL, with
  the per-file kill-rate table showing the two fill-eligible files held ≥85%. Goal
  does not claim to have killed all trio mutants.
- **Clean tree — confirmed.** `git status --short` shows only the expected goal /
  retro / probe / lesson-index / recent-lessons artifacts. No stray mutated SOURCE
  file (no `>>`/`<<` operator left in `render_cli_reference.py` or the trio); Slice
  3's commit `0c53a59` touched only test files + the goal artifact (verified via
  `git show --name-only`).

## Blockers

None. All three Auto-Retro improvements are genuinely dispositioned (one filed as
#262, two applied with real in-session teeth). Closeout proofs are honest and
correctly scoped — local-deterministic proofs only, with the dispatch/live and
next-cron paths explicitly marked not-run. The goal is safe to flip to `complete`.
