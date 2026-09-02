<!-- charness-work-item-key: lesson-promotion-and-budget -->

## Objective

The lesson ledger can promote a proven lesson into its owning standing docs page, and the three recurrence classes hit again in the #770 session are active lessons within the 50 budget.

## Owned scope

- Add `graduate` with a new `graduated` state as one coordinated change: `LIFECYCLE_TRANSITIONS` gains `("graduate", "active"): "graduated"` and `("resurrect", "graduated"): "active"` in `scripts/lessons/lesson_ledger_lib.py` and replay honours it; `_materialize` and the argparse choices in `scripts/lessons/record_lesson_lifecycle.py` stop hardcoding the archive-or-active ternary; the literal refusal message pinned by `tests/test_lesson_lifecycle_refusals.py` is updated. A graduate event requires a decision ref to a commit that touches a `docs/` page. Graduated lessons leave the active budget and stay readable in the ledger. Record that `docs/deferred-decisions.md` D38 is reopened by its own trigger (third recurrence) and resolved by this action.
- Joint review, lesson by lesson, of the 15 active score-0 lessons. For each the agent drafts: the disposition in the ledger's own vocabulary (helped, contradicted, did not help, never consulted) with the evidence (source retro, later retros that hit or missed it, `outcome_counts`); the proposed action (graduate, archive, keep); and for graduate the exact `docs/` edit, both what the owning page gains and what it loses. The operator and agent settle each in conversation; the settled reason is written per lesson before anything is applied. No rule, no classifier, no after-the-fact commit inspection decides a lesson.
- Apply the settled dispositions as lifecycle events and one docs commit per graduated lesson (or one commit per owning page); then seed `wrong-path-is-premise-failure`, `probe-stimulus-from-model-not-source`, `parallel-coverage-runtime-collision` through `seed_lesson_transitions.py`.
- Neither half alone closes the item.

## Acceptance

- `render_lesson_selection_preview.py` shows the three classes active and the active count at or below 50.
- At least one lesson graduated, with its docs commit referenced by the event; `scripts/check-docs.sh` green at that commit.
- `check_lesson_ledger.py` and the selection-index `--check` green.

## Focused verification

Ledger and lesson tests (`tests/test_lesson_ledger.py` and siblings), `check-docs.sh`.

## Dependencies

none

## Non-claims

Does not raise the budget; does not add a classifier that decides which lessons decay.
