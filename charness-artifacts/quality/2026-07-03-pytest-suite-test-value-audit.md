# Pytest Suite Test-Value Audit — coverage ≠ test count

Date: 2026-07-03. Trigger: maintainer asked whether the large pytest suite carries
non-meaningful/redundant/mergeable tests, and explicitly invited a challenge to the
premise that "coverage must be high" should inflate into "test count must be high."
Later refinement: adding a regression test on a bug is in-intent, but it must test the
**structural pattern/invariant**, not overfit to one issue's exact reproduction.

Method: two dynamic Workflow runs. Run 1 (16-wide) was gutted by a transient server
rate-limit + session limit and completed only 2/46 batches. Run 2 (6-wide wave-throttled)
completed all **46/46 batches** — 84 agents, 5.9M subagent tokens, ~68 min. Each batch:
one classifier reads the tests **and the source under test**, judges value against the
repo's real quality model, then the top delete/merge candidates get an adversarial
"find a surviving mutant" verify pass. Whole-suite mechanical scans (main loop) cross-checked
the numbers. Every applied deletion additionally got a pre-delete inspection + a mandated
bounded fresh-eye review — both of which caught real errors in the audit (see Correction Trail).

## Bottom line

**The suite is lean and overwhelmingly load-bearing. Bloat is a rounding error, not a
structural problem.** 3,855 test functions / 360 files / 93,643 test LOC.

| Estimate | Tests | % of 3,855 | Basis |
|---|---|---|---|
| Proven-safe floor | ~39 | ~1.0% | Adversarially verified per-candidate; none had a surviving mutant / unique branch |
| Realistic center of mass | ~110–140 | ~3–3.6% | verify realization (~80%) applied to 172 raw claims; NOT individually proven |
| Auditor-claimed ceiling | 172 | ~4.5% | Sum of all 156 raw findings; upper bound only |

Calibration: of 36 top candidates adversarially verified, **4 (~11%) were rejected as
load-bearing** and many "delete" claims shrank to "merge, relocate one assert first." So the
un-verified tail erodes similarly — hence a range, not a number.

## Why the premise is wrong here (the challenge)

This repo has **no line-coverage % gate** (`grep -rE 'fail_under|--cov=' pyproject.toml
.github/workflows/*.yml` → nothing). The binding regression signals are:
- **changed-line mutation gate** (`scripts/check_changed_line_mutation_coverage.py` + scheduled
  `.github/workflows/mutation-tests.yml`, `score_break` 60) — rewards **mutant kill-value**.
- **LOC test:production ratio** (`scripts/check_test_production_ratio.py`) — currently `--advisory`.
- **vulture** dead-code.

**No gate reads test count.** A count target optimizes a variable nothing reads → pure Goodhart.
The repo already litigated this and ruled against a hard count-side cap:
- The ratio gate was demoted to `--advisory` (commit titled *"Demote test-production-ratio…"*),
  help text: *"a hard cap pressures AGAINST writing tests… a ratio is a smell sensor, not a
  contract."*
- `inventory_standing_test_economics.py` attaches an `INTERPRETATION` self-declaration whose
  `blind_spots` state count *"cannot see whether a given test earns its isolation cost… a high
  count can be honest coverage"* and forces the consumer to answer that question first.

Measured cost of inflation (verified live): ratio **0.9734** (97.3% of the advisory 1.0 cap),
**149** nested-CLI/subprocess-spawning test files, pytest tmp footprint **3.05 GB**, 2,382
exact-string `==` asserts, 1,441 `returncode ==` subprocess-exit re-checks.

## Issue-overfit vs structural — the maintainer's lens

**The anti-pattern is essentially absent.** Whole-repo scan found **exactly one** issue-overfit
source/test pair (`render_issue_57_design_study.py` + its test — already removed, commit
`a855ce74`). 72 structural-sweep test functions already exist (e.g.
`test_structural_sweep_covers_each_329_class_file_type`). `#NNN` references are almost always
**lineage comments and structural test DATA** (the good pattern), not single-instance pins.
Only 2 other genuine overfit findings surfaced (twitter #392 pin — deleted in batch A; handoff
slice-6 budget — deleted in batch A). The suite's authors already converged on the exemplar.

## What is load-bearing (do NOT cut) — 4 verify-rejected traps

1. **In-process "twins" of subprocess tests are NOT redundant.** The changed-line mutation gate
   treats a source line reached only via `subprocess.run` as **0% covered**; the in-process
   drive is the intended attribution. Bulk-deleting "in-process duplicates" breaks the gate on
   the next diff touching those lines. (This trap bit the audit twice — see Correction Trail.)
2. **Template/render snapshots over commented-out YAML** — doctor-block templates are YAML
   comments, invisible to `yaml.safe_load`, so the snapshot is the only coverage of the
   default-vs-lefthook branch.
3. **Scaffold value-pins vs self-comparing byte-equality** — byte-equality compares a template
   to itself and cannot catch value drift; the per-field pins are the sole guard against shipping
   wrong reviewer-tier defaults.
4. **Probe/None-fallback tests that look tautological.**

## Decision rule (optimize kill-value per unit ratio-cost, not count)

1. Does it kill a mutant nothing else kills? Prove it (mutate the line / cite a `blocking_targets`
   entry). No red → don't write it.
2. Bug-driven test? Pin the **class/invariant**, not the case — like the 72 `test_structural_sweep_*`.
3. New input variant of a tested behavior? → **parametrize**, don't multiply files.
4. Genuinely new/distinct/irreversible boundary → add, as a structural sweep.
5. Otherwise, against a 0.9734 ratio → don't.

*One line: add a test only when it kills a mutant no existing test kills; when a bug earns one,
pin the class not the case; when it's a new input, parametrize not duplicate; when in doubt
against 0.9734, don't.*

## Correction Trail — the audit was wrong twice; both caught at the boundary

Adversarial verification is necessary but not sufficient. Two "confirmed_waste" verdicts were
false and were caught by a **different observer on a different evidence channel** (north-star):

- **`test_retro_scaffold.py::…persisted_section_in_process`** — caught by pre-delete inspection.
  Its in-file "twin" reads `template` from the **subprocess payload**, so the deleted test was the
  only in-process attribution for `render_template`. KEPT.
- **`test_quality_tool_recommendations.py::…emit_blocking_runtime_routes`** — caught by the bounded
  fresh-eye review of commit `b06af11e`. Retained in-process twins use `recommendation_role
  "validation"` (different branch); the claimed runtime twin is subprocess-only. It was the sole
  in-process driver of `why_recommended()`'s `runtime` branch. RESTORED in commit `33fc01e2`.

Both are the same "load-bearing trap #1" the synthesis had pre-declared. Lesson: for any test
whose redundancy argument leans on a "twin," verify the twin drives the same source **in-process**,
not via subprocess — the mutation gate does not credit subprocess-only lines.

## Applied so far

- `a855ce74` — removed the issue-57 design-study renderer orphan (script + test + plugin mirror).
- `b06af11e` + `33fc01e2` — **batch A: 12 net verified-safe deletions** (13 removed, 1 restored by
  fresh-eye review). Standing suite 3909 passed; collection 3995 → 3983.

## Deferred (need separate judgment)

- `test_web_fetch_trace_quality.py::test_optional_stage_availability_checks` — `is_available()` has
  0 production callers; deleting the test needs removing the dead source fn too (else vulture flags it).
- `test_sync_support.py::…rejects_upstream_skill_file_path` — command-bootstrap-proof nuance.
- `test_goal_artifact_lib.py::…closeout_evidence_placeholders` — cross-*producer* twin, not same path.
- **Batch B** (order-dependent merges): seed-adapter 3-file refuse/force, plugin-copy smokes,
  doc-link absolute-path pair — each requires relocating a unique assert before delete.
- **Batch C** (prose-pin cluster): parametrize/rewrite doc-substring tests that exercise no Python
  source — count↓, coverage identical. Larger, separate slice.

## Blind spots

- Global mutation-kill overlap was argued by source-branch reading, **not** by an executed mutation
  matrix. The authoritative check for any merge is a real `check_changed_line_mutation_coverage.py`
  run before/after.
- Cross-batch dedup is limited: each batch saw only its own files; shared support-module helpers
  duplicated across sibling test files are a likely source of additional un-counted redundancy.
