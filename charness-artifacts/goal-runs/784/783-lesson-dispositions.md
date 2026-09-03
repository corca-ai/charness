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

| # | lesson | disposition | settled reason | docs edit |
| --- | --- | --- | --- | --- |
| 1 | changed-line-proof-before-broad-quality | graduate | Helped: 14 of 20 encounters changed an action (slice commit → changed-line proof over `base..HEAD` → broad lane, saving a full broad rerun per uncovered line); the 4 read-but-not-applied and 1 not-consulted all predate 2026-08-18 with no recurrence since; the 1 pushed-a-wrong-action (2026-08-16) corrected the wording to "after the slice commit", because the gate reads committed lines. Operator: 동의. Before this lesson the operator asked how a docs-only exposure can be checked at all; answered by the graduated-recurrence advisory shipped one commit earlier (`check_lesson_ledger.py` names a graduated lesson that a retro outside its event's `reviewed_retros` tags again). | docs: `docs/parallel-execution.md` "Disjoint Writers" owns the order beside the lane receipt's `changed_line_gate`, names the two mechanisms (receipt gate, pre-push release lane) and the stated gap (no preamble orders proof before the broad lane, because that lane runs in consumer repos without a mutation pool); `docs/implementation-discipline.md` step 4 loses its reversed order and links. code: none new; the readback for this graduation is the pre-push hook's changed-line refusal count. |
| 2 | green-test-is-not-covered-line | graduate | Helped: all 11 encounters changed an action (2026-08-17 to 08-22), the same shape each time: a green batch left named lines unreached until the coverage read said so. The two 2026-09-03 re-tags are the lane half (subagents trusting a focused green), which the 8.0.3 lane receipt closes. Operator: 추천대로. | docs: `docs/development.md` "Verify in the shape production uses" owns the sentence beside the proxy-green rule; `parallel-execution.md` keeps the lane half; `.agents/claude-host.md` bullet stays one line plus link. code: none new; `release_changed_line_coverage.py` measures line reach and runs in the lane receipt's `changed_line_gate` and the pre-push hook, so no gap is stated. |
