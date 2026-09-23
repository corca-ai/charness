# WI-4: brief critique, premise check, acceptance-first

Goal #844 slice 4 of 14. Hard dependency: WI-1 (per-item BLOCKED verdicts are kinds, not prose).

## Objective

Own the before-launch gates: a cheap time-boxed fresh-eye brief critique (duration recorded, never a "2-minute" claim) before the expensive run; a bounded premise-check phase with per-item BLOCKED verdicts that never blocks the whole lane on one item; a committed failing acceptance skeleton for critical lanes that the lane must turn green.

## Touchpoints

- `scripts/task_run/task_run_plan.py`: brief-critique hook plus premise-check phase.
- `scripts/task_run/task_run_contract.py`: acceptance-skeleton declaration.
- `scripts/task_run/task_run_state.py`: per-item BLOCKED kinds (WI-1 vocabulary).
- New `tests/charness_cli/test_task_run_premise_gates.py`: one-item-blocked-continues, partial-success-plus-blocked, skeleton-must-turn-green cases.

## Acceptance

- Brief critique runs time-boxed with recorded duration before the lane starts (#843-1).
- Premise failures report per-item BLOCKED with the decision each needs; the lane continues past single failures (#843-2).
- A critical lane carries a committed failing acceptance skeleton; "done" requires it green (#843-3).

## Out of scope

No base-freshness or size checks (WI-5); no self-review (WI-7); no new executors. Critique stays advisory: it blocks only on premise failure, never on style.

<!-- charness-work-item-key: wi-4-premise-gates -->
