# Finding — lesson-internalization claim-fidelity fixture (agent-context target class)

Date: 2026-07-01

## Fixture

NEW Cautilus target class — `agent-context` — judging the CONSUMER side of
`charness-artifacts/retro/recent-lessons.md`: did a LATER session HONOR a named prior
lesson, or REPEAT the trap? ("lesson written, next session repeats it.")
Outcome-assertions-only fixture (no spec.json), graded by the host-side
`scripts/grade_skill_outcome.py` over an evidence bundle.

- behavior source: controlled fixture transcripts (slice-1 capture-unit decision),
  `evals/cautilus/lesson-internalization-claim-fidelity/controls/{honored,repeated-trap}/`.
- assertions: `evals/cautilus/lesson-internalization-claim-fidelity/outcome-assertions.json`
  (1 deterministic sanity floor + 2 judge substance assertions).
- lesson under test: the background-launch-stacking trap (recent-lessons.md Repeat
  Traps), chosen because it ACTUALLY RECURRED — the canonical consumer-side failure.
- live judge: real `claude -p` via `scripts/outcome_judge_cmd.py` (operator-authorized
  ask-before-run spend: "you can test it with cautilus", 2026-07-01).

Origin: operator-raised in
`charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md` (Lakatos
lens — a lesson is a hard-core claim only if its internalization is *tested*; "lesson
written = lesson learned" is the doc-opening proxy fallacy applied to the operating
contract).

## Verdict

Accept — the instrument DISCRIMINATES, proven two independent ways.

Offline (no spend, CI-enforced): `tests/test_lesson_internalization_fixture.py`
passes — honored pass_rate 1.0 > repeated-trap 0.167 with an oracle keyed on the real
stacked-command signature; deterministic sanity floor passes both controls.

Live judge (real `claude -p`), n=1 per control:

| control | pass_rate | substance judge verdicts |
| --- | --- | --- |
| honored | 1.0 (3/3) | did-not-repeat-trap PASS, internalized-by-behavior-not-citation PASS |
| repeated-trap | 0.167 (1/3) | both substance assertions FAIL (only the sanity floor passes) |

Live judge evidence (honored): "cleanup `rm -rf` as separate foreground Bash step,
then single clean launch via run_in_background=true with no nohup/&&/;/trailing &."
Live judge evidence (repeated): "folded rm -rf + nohup ... & + multi-statement chain
into one run_in_background command; denied, retried with same stacked pattern. Exact
trap repeated."

Per-control live reports: `honored.outcome-grade.md`, `repeated-trap.outcome-grade.md`.
Machine evidence: `summary.v1.json`.

## Non-Claims

- NOT a live-session proof. Both controls are authored fixture transcripts, not a
  captured arbitrary session. The live-session capture unit is deferred (below).
- Live judge is n=1 per control — discrimination is shown, not a stability claim.
- Anti-gaming check PASSED: the honored control deliberately MENTIONS `nohup` in its
  reasoning while avoiding it in action; the live judge was NOT fooled (passed it on
  substance), and the offline oracle keys on the actual stacked-command operators, not
  the bare token. Reading/citing the lesson while repeating the trap fails
  `internalized-by-behavior-not-citation` — the proxy-fallacy guard.
- KNOWN gap (not guarded this slice): a session that launches NO background task could
  be read as vacuously honored. Out of scope for the two launching controls here;
  flagged for the live-capture slice.

## Path note

This is the HOST-SIDE outcome grader (`grade_skill_outcome.py --judge-cmd`), NOT
`cautilus evaluate`. By repo design the LLM judge lives host-side; cautilus stays the
deterministic scorer. `plan_cautilus_proof.py` returned `not-required /
next_action none / ask` — consistent: no `cautilus evaluate` ran, so that gate did not
bind. The only live spend was the operator-authorized judge calls.

## Follow-up (deferred next slice)

- Live-session capture unit (judge a real later session against the live
  recent-lessons.md), vs the controlled fixture transcripts proven here; add the
  vacuous-pass guard there.
- Lesson rotation / selection policy beyond the one pinned lesson.
- Optional spec.json / `targetKind: agent-context` wiring if a producer-side routing
  floor ever becomes meaningful (would extend `claim_fidelity_lib.py` beyond
  public_skill).
