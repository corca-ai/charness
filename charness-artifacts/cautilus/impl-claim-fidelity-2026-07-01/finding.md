# impl claim-fidelity capture #1 — 2026-07-01 (correctness sweep, 5th skill)

## Verdict

**FLOOR MISS** (cautilus `failed`/reject, declared-reference coverage **0/8** —
`verification-ladder.md` not opened). **SUBSTANCE pass_rate 0.714 (4/5 weighted)** —
`executed-verification` PASS and `smallest-non-overlapping-slice` PASS, but
`honest-categorized-closeout` **FAIL**: the run produced a semantically-honest
closeout in PROSE ("ruff check → All checks passed (clean)", "Test-only addition",
residual branches "explicitly unverified") but **not** the canonical
`verification-ladder.md` enum vocabulary (`ran-pass` / completion-report category
`test-only` / `unverified-future`). This is the first `impl` capture: **impl stays a
HYPOTHESIS on the floor.** The floor MISS and the closeout-vocabulary FAIL are
CONSISTENT and mutually reinforcing — see Disposition.

## What ran

`/charness:impl` with the spec's pinned concrete slice (verbatim from
`evals/cautilus/impl-claim-fidelity/spec.json`: add deterministic unit tests that
directly call `claim_fidelity_lib.py`'s `_validate_string_list` /
`_validate_engagement` helpers, additive to and non-overlapping with the existing
`tests/quality_gates/test_claim_fidelity_specs.py`, run them, close out with Lint
Gate + completion-report category, then a stop-gate critique). Isolated-worktree
capture at `HEAD`=d5e222a6, `--timeout-sec 1200`, exit **0 (NATURAL completion, not
the cap)**, **123821ms** wall, 1.28M tokens, 17 tool calls (Bash=8 Read=6 Skill=1
Write=1 Agent=1). The run wrote `tests/quality_gates/test_claim_fidelity_lib_helpers.py`
(6 tests, +62 lines), ran `pytest` (17 passed: 6 new + 11 existing), ran `ruff`
(clean), and ran a fresh bounded subagent critique (verdict SHIP).

## Floor: MISS (0/8), and WHY it is coherent with the substance result

- Coverage 0/8: the run opened NONE of the 8 declared references — including the
  single floor `verification-ladder.md`. It worked entirely from the always-loaded
  `impl/SKILL.md` body.
- This is consistent with the substance FAIL, not separate from it. The canonical
  Lint Gate status vocabulary (`ran-pass` / `ran-fail-fixed` / `ran-fail-deferred` /
  `not-detected` / `skipped`) and the five completion-report categories (`durable` /
  `external-writes` / `test-only` / `verification` / `unverified-future`) live ONLY
  in `verification-ladder.md:83-87+`. `SKILL.md` NAMES the concept and routes to the
  doc ("`Lint Gate` per `references/verification-ladder.md`", SKILL.md:159,172) but
  does NOT inline the enum tokens. So a run that skips the doc CAN recall the
  verification DISCIPLINE (survey tools, run the strongest proof, mark unverified —
  all inlined in SKILL.md) but CANNOT emit the canonical closeout VOCABULARY. That is
  exactly what happened: discipline honored, canonical vocabulary absent.

## Substance: 4/5, with one precise, discriminating FAIL

Graded by `grade_skill_outcome.py --judge-cmd "python3 scripts/outcome_judge_cmd.py"`
(grader self-test PASSED good=1.0/bad=0.0 first; 3 live judge calls). Full table in
`outcome-grade.md`.

- `ran-impl` (det) PASS; `wrote-tests` (det) PASS (the produced test file preserved
  into `outputs/`).
- `executed-verification` (judge, w2) **PASS** — real `pytest` executed, "17 passed"
  observed, reviewer independently re-ran → 6 passed. impl's "verify it aggressively"
  claim is honored. This discipline IS internalized in SKILL.md.
- `smallest-non-overlapping-slice` (judge, w1) **PASS** — one focused file, 6 tests on
  branches the registry suite never reaches, genuine non-overlap confirmed.
- `honest-categorized-closeout` (judge, w2) **FAIL** — the closeout conveyed the
  substance in prose ("All checks passed (clean)", "Test-only addition", residual
  "unverified") but did not produce the canonical enum tokens the Output Shape
  requires. The judge (strict, defaults to fail) correctly graded the approximation
  as not-the-contracted-output.

## This is NOT an over-strict matcher (why the FAIL stands)

`impl`'s Output Shape literally requires "`Lint Gate per references/verification-ladder.md`".
A closeout that says "All checks passed" instead of `ran-pass <command>`, and "Test-only
addition" instead of a labeled completion-report category, is not producing the
contracted vocabulary. The assertion is judge-kind and not reverse-engineered to this
run (it names only the canonical enum, which predates the capture), so it discriminates
beyond n=1. The honest counter-consideration to surface (NOT to resolve unilaterally
tonight): a reasonable reviewer could argue the semantic equivalent suffices and the
exact tokens are house-style. That is a DECISION for the operator, recorded below — it
is NOT a license to soften the assertion or the floor.

## Disposition

- **impl stays HYPOTHESIS on the floor (n=1).** Floor MISS (0/8); `requiredCommandFragments`
  unchanged (`[verification-ladder.md]`). NOT softened.
- **The substance result points at a clean skill-shape DECISION** (handoff's "re-pin /
  re-classify / planner", never soften):
  - Option A — **internalize** (debug-Plan-A-style): inline the Lint Gate status enum +
    the five completion-report categories into `impl/SKILL.md` so a run emits the
    canonical vocabulary without opening the doc. Then the floor becomes a genuine weak
    proxy AND the closeout substance passes. Lowest-friction for the most-run skill.
  - Option B — **keep the floor load-bearing**: treat the canonical closeout as
    genuinely requiring `verification-ladder.md`, so the floor MISS is a real fidelity
    gap and the fix is a planner/skill nudge that routes the doc at closeout.
  - This is a candidate issue for the operator; see Off-Goal / Auto-Retro in the goal
    artifact. NOT decided tonight.
- **Threshold (`thresholds.max_duration_ms`): left UNSET.** The capture completed
  NATURALLY (123821ms) — a valid baseline — BUT the floor did not PASS, and the
  repo's threshold policy derives the budget from a PASSING capture (~2x). Recording
  the natural-completion 123821ms here so a future PASS (or a decision to base the
  runtime guard on natural completion regardless of floor) has the number; ~2x ≈
  247000ms would be the candidate.

## Two capture-harness gaps surfaced this run (generalizable; worked around manually)

These block the sweep's reuse on ANY skill that commits / completes cleanly, so they
are tracked, not silently patched into this finding:

1. **Output preservation diffs vs `HEAD`, but a faithful `impl` run COMMITS its slice.**
   `preserve_outputs()` / `_changed_files()` (`run_skill_efficiency_ab.py:220-266`) use
   `git diff --diff-filter=ACMR HEAD`. impl committed its slice inside the worktree
   (`2ab1f891` on top of the capture ref), so HEAD moved and the diff-vs-HEAD changed
   set was EMPTY — the produced test file would NOT have been preserved, and the
   substance judge would have graded blind (the exact blocker the plan-critique warned
   about, in a new form). Worked around by diffing vs the capture ref (d5e222a6).
   Durable fix: preserve against the checked-out ref, not HEAD. (debug never hit this
   because debug writes an artifact and does not commit.)
2. **The session-tree transcript missed the final assistant block (flush/timing).**
   `_write_transcript()` reads the tree `*.jsonl`, which had only 5/6 assistant blocks
   (1499 chars) — the final `## Closeout` block was absent — while the `stream.jsonl`
   stdout had the complete record (6 blocks, 4322 chars, closeout present). A judge
   reading the tree-built transcript would grade the closeout blind. Worked around by
   rebuilding `transcript.txt` from `stream.jsonl`. Durable fix: build the transcript
   from `stream.jsonl` (or await the tree flush).

## Non-Claims

- This is **n=1** for impl; the floor MISS + closeout-vocabulary FAIL are one capture,
  not a proven trend. A re-capture (or a post-internalization capture) would confirm.
- The substance grade is **advisory** (judge-kind), never a gate. `executed-verification`
  PASS rests on the observed pytest run + reviewer re-run, not a mutation score.
- The canonical cautilus FLOOR verdict (`cautilus-report.json`: 1 failed / 0 passed) is
  the authoritative floor signal; the `.mjs` `outcome: failed` agrees.
- No `impl` SKILL surface, `verification-ladder.md`, planner, matcher, floor, or
  assertion was softened or changed to flip any verdict this run.

## Bundle

`justification.md`, `observed.v1.json`, `cautilus-report.json`, `trace-digest.jsonl`,
`transcript.txt` (rebuilt from stream.jsonl), `outputs/test_claim_fidelity_lib_helpers.py`
+ `outputs/outputs-manifest.json`, `grade.selftest.txt`, `outcome-grade.md`, this
`finding.md`. New eval companion: `evals/cautilus/impl-claim-fidelity/outcome-assertions.json`.
