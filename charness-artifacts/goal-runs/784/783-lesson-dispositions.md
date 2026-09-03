# #783 joint lesson review, 2026-09-03

Settled lesson by lesson between the operator and the agent in conversation,
under the three questions of
`skills/shared/references/lesson-graduation.md`. Nothing below was decided by
a rule, a classifier, or commit inspection. The reason is written before the
event is applied. Same shape as `../775/781-lesson-dispositions.md`.

Drift at session start, against the #783 body's 2026-09-03 read: the ledger
still has 34 scored active lessons (47 active, budget 50), but
`durable-lesson-ledger-first` totals +1 (two legacy scalars, one
`read-but-not-applied`), not a negative; the negative group is six, not seven,
and the middle group is eighteen (fifteen at +1 with one event,
`durable-lesson-ledger-first` at +1 with three, and two at 0:
`cause-named-from-one-observation`, `executed-vs-read-field`). The order of
conversation is unchanged.

Operator rule, settled after lesson 2 ("will it really work buried between
docs?" and "docs will grow without bound"): a docs sentence carries the rule and
the mechanism's name, never the why, the counts, or the dates (those stay in
this record, the ledger, and the retros); a gate that holds the whole class
earns one table row, and a paragraph survives only for a stated gap; `docs/`
pages have a 1,500-word budget (`check_docs_length.py`, record shrinks only);
and a graduation's readback is the graduated-recurrence advisory in
`check_lesson_ledger.py` (lifecycle events record `reviewed_retros`). Applied
retroactively to lessons 1 and 2 in `c20352d45`.

Third operator rule, settled at lesson 4 ("keep with a sentence is a
contradiction"): the principle is `docs/design-north-star.md` P2/P3 (unread
prose is not a contract; principle plus worked example over rulebook), the
worked examples are the mechanisms table in `docs/development.md`, and a
graduation adds a row there or a stated gap, never a new sentence per lesson.
Applied retroactively to today's and #781's pages in the same commit: the
Disjoint Writers paragraphs lose their dates and timings, documentation-
principles loses its dated instances.

| # | lesson | disposition | settled reason | docs edit |
| --- | --- | --- | --- | --- |
| 1 | changed-line-proof-before-broad-quality | graduate | Helped: 14 of 20 encounters changed an action (slice commit → changed-line proof over `base..HEAD` → broad lane, saving a full broad rerun per uncovered line); the 4 read-but-not-applied and 1 not-consulted all predate 2026-08-18 with no recurrence since; the 1 pushed-a-wrong-action (2026-08-16) corrected the wording to "after the slice commit", because the gate reads committed lines. Operator: 동의. Before this lesson the operator asked how a docs-only exposure can be checked at all; answered by the graduated-recurrence advisory shipped one commit earlier (`check_lesson_ledger.py` names a graduated lesson that a retro outside its event's `reviewed_retros` tags again). | docs: `docs/parallel-execution.md` "Disjoint Writers" owns the order beside the lane receipt's `changed_line_gate`, names the two mechanisms (receipt gate, pre-push release lane) and the stated gap (no preamble orders proof before the broad lane, because that lane runs in consumer repos without a mutation pool); `docs/implementation-discipline.md` step 4 loses its reversed order and links. code: none new; the readback for this graduation is the pre-push hook's changed-line refusal count. |
| 2 | green-test-is-not-covered-line | graduate | Helped: all 11 encounters changed an action (2026-08-17 to 08-22), the same shape each time: a green batch left named lines unreached until the coverage read said so. The two 2026-09-03 re-tags are the lane half (subagents trusting a focused green), which the 8.0.3 lane receipt closes. Operator: 추천대로. | docs: one row in `docs/development.md`'s mechanisms table (rule, mechanism, record, cannot see); the first four-sentence version with ledger history was cut the same day under the operator's docs rule below; `parallel-execution.md` keeps the lane half; `.agents/claude-host.md` bullet stays one line plus link. code: none new; `release_changed_line_coverage.py` measures line reach and runs in the lane receipt's `changed_line_gate` and the pre-push hook, so no gap is stated. |
| 3 | detector-blind-class-unstated | keep | Helped (10 of 15 changed an action, 2026-08-16 to 08-20) but the five misses are "wrote it but wrong" (one negation instance named, an unchecked scaffold line called live), which no presence check catches; only 11 of 41 `scripts/gates/check_*.py` docstrings state a blind class today and no gate holds that. No mechanism, and a docs-only graduation would lower exposure. The mechanisms table in `docs/development.md` now asks the question structurally (a "cannot see" column, empty cell visible); whether that changes the next gate author's action is scored, not assumed. Operator: 킵 동의. | none |
| 4 | bar-recorded-as-prose | keep | Helped early (7 of 12 changed an action, 2026-08-15 to 08-21) but the three most recent encounters are misses (a structural field filled from prose, an enumerated negation list, a checked pin moved into a docstring). No mechanism can tell a bar from a description in prose, and the 8.0.3 surfaces named at session start (retention constants, `script_origin`, shrink-only records) are instances of the rule, not enforcement of it. Under the third rule a keep carries no sentence. Operator: 킵. | none |
| 5 | goal-closeout-evidence-binding | graduate | Helped: 6 of 7 changed an action (2026-08-19 to 08-21), none failed; the class stopped appearing once the dedicated close operation carried the order (index validated before provider selection, close, distinct readback, terminal metadata through the binding-aware update; failed readback is `unverified`). Operator: ok. | none: `docs/goal-lifecycle.md` "Execution And Closeout" already states the mechanism as current fact; decision_ref points there |
