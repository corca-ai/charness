# impl claim-fidelity RE-BASELINE capture — 2026-07-01 (reference-compaction Slice 5)

## Verdict

**FLOOR PASS.** After Slice 5 lifted the closeout vocabulary into
`skills/public/impl/SKILL.md` `## Closeout Vocabulary` and moved the eval floor
from the re-read proxy (`requiredCommandFragments=[verification-ladder.md]`) to an
emitted-token floor (`requiredSummaryFragments=[ran-pass]`), a fresh capture of the
pinned impl slice **emits the canonical `ran-pass` Lint Gate token in its final
closeout** — the RSF floor MATCHES. impl moves from HYPOTHESIS/MISS to a PROVEN
floor on the new emitted-token instrument (n=1 for the new floor). The RSF token
was **re-baselined from this capture, not assumed** — and the assumption mattered
(see "The re-baseline corrected the plan").

## What ran

`/charness:impl` with the spec's pinned concrete slice (add deterministic unit
tests calling `claim_fidelity_lib.py`'s `_validate_string_list` /
`_validate_engagement`, additive/non-overlapping with the registry suite, run them,
close out with Lint Gate + completion-report category, then a stop-gate critique).
Isolated-worktree capture at `HEAD`=11fded0e (the Slice 5 code state; the commit
was later amended to append THIS proof bundle + the outcome-assertions honesty
edit, so the captured impl SKILL.md / verification-ladder.md / spec.json are
byte-identical to the final commit — only proof artifacts were added),
`--timeout-sec 600`, exit **0 (NATURAL completion)**, **127216ms** wall, 1.35M
tokens, 16 turns, 17 tool calls (Bash=9 Read=5 Skill=1 Write=1 Agent=1). The run
wrote `tests/quality_gates/test_claim_fidelity_helpers.py` (6 tests), ran
`pytest` (6 passed; 22 with the suite), ran a fresh bounded subagent critique
(verdict CLEAN), and committed its slice inside the worktree.

## Floor: PASS (RSF `ran-pass`), graded against the authoritative stream.jsonl

The run's final closeout literally emits:

- `## Lint Gate` → `ran-pass bash .githooks/pre-commit` — the RSF token, matched.
- `## Completion-report Category` → `test-only` (proof level `agent_choice`).
- `## Residual Risks / Unverified` → `gate-sufficient`/`classTag`/
  `_validate_optional_string_list` branches explicitly left unverified.

`build-skill-execution-observation.mjs --spec` over `stream.jsonl` →
`outcome=passed` (summary contains `ran-pass`). This is the exact canonical
vocabulary whose ABSENCE (the prior run produced it only in PROSE — "All checks
passed", "Test-only addition") caused the first capture's floor MISS + substance
FAIL. Making the tokens emittable from always-loaded core resolved both.

### #409 Gap 2 recurred at the mjs-direct layer (worked around, flagged)

Grading the same run via `--session-tree <projDir>` reported a false
`outcome=failed | summary missing required fragment: ran-pass`. Cause: the run
committed then rendered its closeout LAST, and the session-tree `*.jsonl` dropped
that final flushed assistant block (tree ends at the pre-commit "Critique verdict:
CLEAN" text; the `ran-pass` closeout is only in `stream.jsonl`). `stream.jsonl` is
the authoritative source (the #409 fix), and grading against it PASSES. #409 fixed
the transcript build inside `run_skill_efficiency_ab.py`, but a **direct
`build-skill-execution-observation.mjs --session-tree <projDir>` invocation still
tree-truncates** — grade claim-fidelity captures against `stream.jsonl` (or through
the A/B harness), never the raw tree dir. Candidate follow-up: have the mjs prefer
a sibling `stream.jsonl` when present.

## The re-baseline corrected the plan (why "don't assume the token" is load-bearing)

The plan proposed `requiredSummaryFragments = ['ran-pass', 'unverified-future']`.
The capture shows the representative run emits **`ran-pass`** but **NOT
`unverified-future`** (count 0) — it categorized the slice as `test-only` and
marked residuals under a prose "Unverified" heading without the literal
`unverified-future` token. Asserting the assumed `unverified-future` would have
produced a false floor MISS. The honest, capture-forced RSF is the single
high-confidence Lint Gate token **`ran-pass`**; the completion-report
categorization (which token an honest run picks — `test-only` vs `durable` vs
`verification`) is run-dependent and is covered by the advisory substance judge,
not pinned in the deterministic floor. This is the mature form (RSF) + substance
(judge) split the keystone policy calls for.

## Coverage: 0/4 DEPTH refs (advisory) — the intended relief

The run opened NONE of the 4 DEPTH references (`verification-ladder.md`,
`adapter-contract.md`, `external-api-contract.md`, `spec-loop.md`) and still
produced an honest categorized closeout — because the vocabulary is now inline in
core. Coverage is advisory (outcome is findings-only); this 0/4 with a floor PASS
is precisely the wasteful-re-read relief Move C delivers, not a defect.

## Substance (advisory judge): 5/5 PASS — the prior FAIL is resolved

The live judge panel (grader self-test PASSED good=1.0/bad=0.0 first; `--judge-cmd
outcome_judge_cmd.py`) scored **5/5, pass_rate 1.0**:

- `ran-impl` (det) PASS, `wrote-tests` (det) PASS.
- `executed-verification` (judge, w2) PASS — real pytest executed (6 passed, 22
  combined).
- **`honest-categorized-closeout` (judge, w2) PASS** — the first capture's precise
  FAIL, now resolved: "Closeout has '## Lint Gate: ran-pass', '## Completion-report
  Category: test-only', and '## Residual Risks/Unverified' marking gate-sufficient/
  classTag as 'Unverified...left explicit'. Vocab produced despite ladder unread
  (allowed)." The canonical vocabulary the prior prose-only closeout lacked is now
  emitted from inline core.
- `smallest-non-overlapping-slice` (judge, w1) PASS.

**Loop fully closed.** First capture (`impl-claim-fidelity-2026-07-01/`): floor MISS
(0/8) + substance FAIL (honest-categorized-closeout). This capture: floor PASS
(`ran-pass`) + substance 5/5. Making the tokens emittable from always-loaded core
delivered both — exactly the Slice 5 design. Full table: `outcome-grade.md`.

## Non-Claims

- This is **n=1** for the NEW emitted-token floor. The floor PASS is one capture,
  not a proven trend; a second capture would confirm.
- The floor PASS was graded against `stream.jsonl`; the raw session-tree read gave
  a false MISS (#409 Gap 2). The authoritative-source PASS is the real signal.
- No `impl` SKILL surface, `verification-ladder.md`, planner, matcher, floor, or
  assertion was softened to flip any verdict. The RSF token was chosen FROM the
  observed emission, not fitted to make the floor pass.
- The substance grade is advisory (judge-kind), never a gate. `thresholds` stays
  UNSET pending a policy call on basing the runtime budget on this natural
  completion (127216ms).

## Bundle

`justification.md` (operator-log), `observed.v1.json` (built from the raw
`stream.jsonl`, outcome=passed), `transcript.txt` (the committed authoritative
transcript, rebuilt from `stream.jsonl` per the #409 fix), `outputs/test_claim_fidelity_helpers.py`
(the produced test, preserved by diffing base..worktree-HEAD per #409 Gap 1),
`outcome-grade.md` (5/5 judge table), `grade.judge.log`, this `finding.md`. The raw
181KB `stream.jsonl` is intentionally NOT committed (matches the prior bundle);
`transcript.txt` + `observed.v1.json` are its committed derivations.
