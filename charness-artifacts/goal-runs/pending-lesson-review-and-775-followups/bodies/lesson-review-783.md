<!-- charness-work-item-key: lesson-review-783 -->

## Objective

Reuse #783. Each of the 34 scored active lessons settled one at a time, in Korean, between the operator and the agent under the three questions of `skills/shared/references/lesson-graduation.md`; graduations ship owner-page edit, duplicate removals, mechanism or stated gap, and the lifecycle event in one commit.

## Owned scope

- Order: `changed-line-proof-before-broad-quality`, `green-test-is-not-covered-line`, `detector-blind-class-unstated`, `bar-recorded-as-prose`; then `goal-closeout-evidence-binding`, `proof-surface-message-drift`, `agent-authored-score-role`, `premise-not-checked-against-source`, `closeout-diagnostic-visibility`, `proof-surface-review-binding`; then the seventeen single-score lessons; then the seven negative totals (`guard-adjacent-to-action`, `closeout-authoring-rework`, `counted-limit-retry-loop`, `artifact-contract-late-feedback`, `evidence-channel-identity`, `coverage-claim-exceeds-the-pin`, `durable-lesson-ledger-first`) as archive candidates. The table orders the conversation; it decides nothing. This list is the 2026-09-03 read of `charness-artifacts/retro/lesson-ledger.json` (active state, `score_count` above zero); regenerate it at session start and note any drift.
- Per lesson the agent drafts: disposition (helped, contradicted, did not help, never consulted) with the score events as evidence; the owning `docs/` page and every duplicate hit from `grep -rn`; the mechanism or the stated gap and whether the page is read at the decision moment; the recommended move. The operator settles; the reason is recorded before any event.
- Disposition record: `charness-artifacts/goal-runs/<parent>/783-lesson-dispositions.md`, same shape as `781-lesson-dispositions.md`.
- Events only through `record_lesson_lifecycle.py`; `check_lesson_ledger.py`, the selection preview, and `check-docs.sh` green at each commit.
- The #783 body's first bullet is updated to say the nine classes are seeded.

## Acceptance

- 34 rows in the disposition record, each with the operator's answer and the move; every graduation commit carries all three halves and a green docs gate.
- Active count at or below 50; the selection preview no longer shows any graduated lesson.

## Focused verification

`check_lesson_ledger.py`, `render_lesson_selection_preview.py`, `check-docs.sh` after every event; the standing runner before each push.

## Dependencies

none as a manifest edge. Per lesson: the four top candidates are not graduated before the mechanism they graduate onto has landed (slice 1 for the first two, slice 2 for `detector-blind-class-unstated`); the other thirty may be settled at any time. A session may advance the cursor past this item with an `update-body` operation when the operator would rather take slice 4 or 5.

## Non-claims

No budget increase, no seeder or vocabulary change, no rule or classifier; the 13 unscored active lessons are outside this item.
