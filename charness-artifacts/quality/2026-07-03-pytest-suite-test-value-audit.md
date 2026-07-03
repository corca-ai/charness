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
bounded fresh-eye review. Those layers also surfaced a **false premise this operator had
seeded into the audit context** — see **Coverage-Model Correction** below, which supersedes
the original "subprocess = 0% covered" reasoning.

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

## Coverage-Model Correction (this operator seeded a false premise)

During the audit this operator asserted — in the workflow context handed to all 46 classifiers,
the verifiers, and both fresh-eye reviewers — that *"a source line reached only via
`subprocess.run` is 0% covered, so a subprocess test provides no coverage/kill attribution."*
**That is coverage.py's generic default, but it is FALSE for this repo.** `scripts/mutation_sampling_lib.py`
enables subprocess coverage capture for the changed-line gate's probe: a generated `sitecustomize.py`
calls `coverage.process_startup()`; `coverage_subprocess_env` exports `COVERAGE_PROCESS_START` +
`COVERAGE_RCFILE` + a PYTHONPATH pointing at that sitecustomize; the rcfile sets `parallel = True`;
per-process data is combined on export. Any child Python process that **inherits `os.environ`** is
therefore traced — and because cosmic-ray mutates source and a subprocess test's child runs the
mutated code and fails, subprocess tests also **kill mutants**.

Empirically confirmed: running the probe on ONLY `test_retro_scaffold_reports_validator_and_template`
(a subprocess test) shows `scaffold_retro_artifact.py:64` `covered=True` while its in-process twin
did not run.

**Consequence:** the "load-bearing trap #1" below and the first Correction-Trail entries were
**over-caution from this false premise**, not real saves. The three tests they protected were later
deleted (commit `8e3e5225`) after the premise was empirically disproven. The net direction of the
error was safe — nothing unsafe was ever deleted — but the reasoning is corrected here.

**Residual nuance (still true):** a subprocess spawned with a *scrubbed* env (`env={...}` without
`os.environ`) does NOT inherit `COVERAGE_PROCESS_START` and is untraced; and the repo keeps some
in-process "twins" as attribution robust to env propagation. So "prefer in-process for attribution"
is a defensible *robustness* heuristic — just not the absolute "subprocess = 0%" rule asserted.

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

1. **In-process "twins" — case-by-case, NOT an absolute rule.** *(CORRECTED — see Coverage-Model
   Correction.)* The original claim that "subprocess = 0% covered → the in-process twin is the only
   attribution" is FALSE here: subprocess children that inherit `os.environ` ARE traced and DO kill
   mutants. An in-process twin is only load-bearing when its subprocess counterpart spawns with a
   scrubbed env or asserts less. Verify env-inheritance before treating a twin as unique — three
   tests wrongly kept under this trap were later deleted (`8e3e5225`). The remaining three traps
   below stand on their own evidence.
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

## Correction Trail — a false premise, caught and corrected

The failure mode here was not a bad deletion — it was **over-caution from a premise this operator
seeded** ("subprocess = 0% covered"; see Coverage-Model Correction). It made the audit's verify pass,
a fresh-eye reviewer, and this operator wrongly *keep* three redundant tests:

- `test_retro_scaffold.py::…persisted_section_in_process` — kept in batch A because its subprocess
  twin was assumed to give no attribution.
- `test_quality_tool_recommendations.py::…emit_blocking_runtime_routes` — deleted in `b06af11e`,
  then RESTORED (`33fc01e2`) when a fresh-eye review flagged it under the same premise.
- `test_setup_seed_usage_episodes.py::test_seed_usage_episodes_force_overwrites` — kept in batch B.

All three were empirically shown redundant — their subprocess twins inherit `os.environ` (traced →
kill mutants) — and DELETED in `8e3e5225`. Net direction throughout was safe: no test that should
have been kept was ever deleted. Lesson: verify the *actual* coverage config before reasoning about
attribution; do not import coverage.py's default behavior as a repo invariant.

## Applied

- `a855ce74` — issue-57 design-study renderer orphan (script + test + plugin mirror). **−2 tests.**
- `b06af11e` + `33fc01e2` — **batch A**: 12 net verified-safe deletions.
- `70cd0f2b` — this audit artifact + `quality/latest.md` pointer.
- `047cf769` — **batch B**: 3 subprocess-redundant deletions (doc-link + 2 seed refuse). **−3.**
- `8e3e5225` — **coverage-model correction**: deleted the 3 tests wrongly kept under the false
  premise. **−3.**
- `6e0347a7` — corrected this artifact (the false subprocess premise).
- `ae442a88` — **deferred items resolved**: removed the 3 deferred tests + the dead `is_available()`
  source functions (2 stage modules + plugin mirrors). **−3 tests, −2 dead source fns.**
- **batch C** (prose-pin parametrize fold): folded the genuinely-homogeneous pure-markdown clusters
  only. `test_skill_lesson_durability.py` (**8 fns → 3**): the 6 "read a doc, assert plain substrings"
  lessons became a declarative `LESSON_GUARDS` table; the 2 special-logic guards (section-scoped
  create-skill verification, raw+normalized debug) stay byte-identical named functions.
  `test_closeout_discipline_propagation.py` (**8 fns → 4**): the 5 identical SKILL-anchor twins
  (release/announcement/gather/narrative/handoff) became one parametrized test; the 3 distinct-shape
  fns kept. **−9 test functions, 0 collected-item delta** — every asserted substring is preserved as
  a param case, whole-suite collection stays 3974. Honest accounting: **LOC is ~neutral, not reduced**
  (propagation −12; lesson-durability +15 from the table structure + an explanatory docstring). The
  real win is a declarative table for the two homogeneous clusters + fewer functions, NOT less code
  or less brittleness — coverage and the 2,382-`==`-pin brittleness are byte-identical. A first draft
  used a 4-column `(section, normalize)` schema for the lesson table; that was reverted as
  "procedure hidden in data" (it grew LOC and only 1–2 cases used each column) — folding only the
  truly-homogeneous subset is the honest shape. ruff clean; both files + full `quality_gates` dir
  (2463) green; standing suite green; bounded fresh-eye reviewed (38 + 10 substrings preserved
  verbatim, confirmed two ways).

**Total: 23 test functions removed** (issue-57 −2, A −12, B −3, correction −3, deferred −3) plus
2 dead source functions. Standing suite green (3900); collection 3997 → 3974. No unsafe deletion
shipped — every removed test's source branch is still covered by a retained sibling; all deletions
passed a bounded fresh-eye review. (Batch C is separate: a −9 test-function *fold*, 0 deletions,
0 collected-item change, LOC ~neutral.)

## Deferred — resolved / remaining

The three original deferred items were reviewed and all removed in `ae442a88` (see Applied). What
remains deliberately KEPT or explicitly out of scope:

- **Plugin bundle smokes** (`test_usage_episodes_report.py::test_plugin_usage_episode_report_smoke`
  + `…product_review_smoke` + `test_usage_episodes_validator.py::…validator_smoke`) — **KEPT**: the
  only end-to-end proof the shipped plugin BUNDLE runs (the byte-parity gate proves `.py` identity;
  import-smoke only imports; neither runs the bundle).
- **Batch C** (prose-pin cluster) — **DONE (partial by design)**. Of the 6 candidate anchors, only 2
  held a genuinely homogeneous "read one doc → assert substrings" cluster where a declarative
  parametrize is strictly better at equal capability. **Folded** (see Applied):
  `test_skill_lesson_durability.py` 8→1 and the 5 SKILL-anchor twins in
  `test_closeout_discipline_propagation.py` 5→1. **Skipped, with rationale** (folding these fails the
  "그게 정말 최선인가?" test — it would not be the best shape):
  - `test_source_bound_records_guidance.py` — already 1 fn; a fold would *increase* collected items
    and add a table for a single logical guard. Not better.
  - `test_quality_skill_docs.py` (22 fns) — heterogeneous multi-doc combos, per-assert normalization
    variants, a negative (`not in`) assert, and `#NNN` issue-context comments; a fold-schema would be
    a procedure hidden in data, not declarative, and would risk dropping the comments. (Borderline: a
    ~6–8 fn "dispatch + one lens ref" subset could be revisited, but the win is marginal.)
  - `test_issue_skill.py` (29 fns) — only 3 are pure-markdown and scattered; the rest exercise
    `issue_tool`/`issue_plan` source (out of Batch C scope). Negligible fold value.
  - `test_issue_closeout_discipline.py` (10 fns) — 2 subprocess (excluded) + 8 heterogeneous
    cross-doc guards, no homogeneous cluster to fold cleanly.
  **Framing correction:** `parametrize` does NOT reduce the collected-item count (each case is its
  own item), so Batch C's real lever is test-FUNCTION count + LOC + declarativeness — not the
  "count↓" the original bullet implied. The 2,382 `==` brittle pins are unchanged: a fold preserves
  every pin verbatim, so it does not reduce brittleness (which was never in this slice's scope).

## Blind spots

- Global mutation-kill overlap was argued by source-branch reading, **not** by an executed mutation
  matrix. The authoritative check for any merge is a real `check_changed_line_mutation_coverage.py`
  run before/after.
- Cross-batch dedup is limited: each batch saw only its own files; shared support-module helpers
  duplicated across sibling test files are a likely source of additional un-counted redundancy.
- **Duplication lens was never run (surfaced by a maintainer question post-Batch-C).** The audit and
  Batch C were both *test-as-unit* lenses (delete-redundant / parametrize); neither sees intra-function
  boilerplate. A full-path scan found **66 same-file re-reads across 16 test files** — concentrated:
  `test_quality_skill_docs.py` re-reads `quality/references/inventory-dispatch.md` **15×**;
  `test_skill_docs_contracts.py` re-reads several `setup` docs — genuine extract-constant candidates
  (real LOC). **Production code is clean** (0 within-file same-file re-reads in `scripts/` + skill
  scripts): this is a pure test-suite phenomenon (each test re-reads the same stable fixture doc to
  stay self-contained). Honesty caveats: a *basename* scan overcounts (895 raw — `SKILL.md` is
  polymorphic across skills; `gh-log.json`/`latest.md` are per-test tmp fixtures); **66** is the
  full-path figure. And `read_text` is only ONE axis — inline fixture-script duplication (e.g. the
  fake `gh` block rewritten ~5× in `test_issue_skill.py`) is real duplication this scan cannot see.
  This is a concrete instance of intent.md's Goodhart warning: reducing function *count* was
  LOC-neutral because the real LOC waste (duplication) is orthogonal to count. Cleanup deferred
  pending an approach/scope decision — standing advisory signal (extend `inventory_structural_waste`)
  vs manual extract-constant on the concentrated files vs full 16-file sweep.
