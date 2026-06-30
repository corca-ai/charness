# lesson-internalization claim-fidelity (agent-context target class)

A NEW Cautilus target class — **`agent-context`** — distinct from the 20
`public_skill` claim-fidelity specs. Those score the **producer** side of a single
`/charness:<skill>` run (did it open the references it claims to route through).
This fixture scores the **consumer** side of
[`charness-artifacts/retro/recent-lessons.md`](../../../charness-artifacts/retro/recent-lessons.md):

> A lesson is written by one session (the producer). Did a **later** session
> actually **honor** that lesson, or **repeat the trap**?

Headline failure to catch: **"lesson written, next session repeats it."** This is
the operating-contract analogue of debug's substance assertions. Origin:
operator-raised in
[`2026-06-30-debug-internalize-compress-session.md`](../../../charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md)
(Lakatos lens — a lesson is a hard-core claim only if its internalization is
*tested*; "lesson written = lesson learned" is the doc-opening proxy fallacy the
debug arc exists to kill, applied to the operating contract).

## Shape

Outcome-assertions-only — no `spec.json` / `claim-fidelity-registry.json` entry.
There is no skill invocation and no `skills/public/<id>/references/` to route, so
the producer-side doc-opening floor does not apply. `outcome-assertions.json` is
auto-covered by `scripts/validate_outcome_assertions.py` (the
`*-claim-fidelity/outcome-assertions.json` glob) and graded by
`scripts/grade_skill_outcome.py`, exactly like the debug/hitl substance sets.

```text
outcome-assertions.json          the substance assertions (1 deterministic floor + 2 judge)
controls/honored/                positive control: a session that HONORED the lesson
controls/repeated-trap/          negative control: a session that REPEATED the trap
  observed.v1.json               distilled packet (summary carries the sanity marker)
  transcript.txt                 the assistant behavior the judge reads
```

## Lesson under test

The **background-launch-stacking** trap (recent-lessons.md *Repeat Traps*): when
launching a long-running/background task, use a single clean command via the native
`run_in_background` mechanism — do **not** stack a compound shell one-liner
(`nohup … &`, `&&`/`;` chaining, trailing `&`, or `rm -rf` folded into the same
backgrounded command), which trips multiple permission triggers and wastes a
round-trip. Chosen because it **actually recurred** — the canonical
"lesson written, next session repeats it" failure — and is behavioral, so
honored-vs-repeated is a real substance judgment.

## Running it

Offline instrument self-test (no API spend) — proves the honored control out-scores
the repeated-trap control:

```bash
python3 -m pytest tests/test_lesson_internalization_fixture.py -q
```

Offline grade of one control (deterministic floor only; judge-kind SKIPPED without
`--judge-cmd`):

```bash
python3 scripts/grade_skill_outcome.py \
  --assertions evals/cautilus/lesson-internalization-claim-fidelity/outcome-assertions.json \
  --grade evals/cautilus/lesson-internalization-claim-fidelity/controls/honored
```

Live judge (ask-before-run token spend — the real substance proof). The grader is
host-side; the LLM judge is the swappable `--judge-cmd` seam, not the deterministic
cautilus scorer:

```bash
python3 scripts/grade_skill_outcome.py \
  --assertions evals/cautilus/lesson-internalization-claim-fidelity/outcome-assertions.json \
  --grade evals/cautilus/lesson-internalization-claim-fidelity/controls/repeated-trap \
  --judge-cmd "python3 scripts/outcome_judge_cmd.py"
```

A trustworthy run shows the **honored** control near `pass_rate 1.0` and the
**repeated-trap** control low (the judge fails `did-not-repeat-trap` and
`internalized-by-behavior-not-citation`).

## Deferred next slice

This first slice proves the **instrument discriminates** on controlled fixture
transcripts. The deferred work:

1. **Live-session capture unit.** Point the fixture at a real later session graded
   against the live `recent-lessons.md` (the non-deterministic consumer side),
   instead of controls. Requires a session-capture harness that preserves a
   transcript bundle for an arbitrary task session (not a single `/charness:<skill>`
   run).
2. **Lesson rotation.** Generalize beyond the one pinned lesson so the fixture
   tracks whichever traps are currently live in recent-lessons.md (lesson selection
   policy), with the same anti-gaming substance stance.
   - **Vacuous-pass guard.** A live session that launches no background task at all
     could read as vacuously honored; both controls here DO launch, so it is out of
     scope for slice 1, but the live-capture slice must guard it (e.g. an
     applicability precondition before the substance assertions count).
3. **Optional `spec.json` / `targetKind: agent-context` wiring** if a producer-side
   routing floor ever becomes meaningful for this class (would require extending
   `claim_fidelity_lib.py` beyond the hardcoded `public_skill`).
