# WI-8b: declarative DAG plan, ready-derivation, single-shot pull

Goal #844 slice 9 of 14. Soft dependencies: WI-1 and WI-8a (reconcile outcome vocabulary at merge).

## Objective

Own the declarative lane DAG as a static plan file (lanes, dependencies, carrier, brief path) plus a pure ready-derivation and a single-shot pull command that launches ready dependents when a slot frees. Status is a read-through view of provider child state, never written as completion proof and never a second progress channel. Explicitly not a scheduler: no watch loop, no background poll, no daemon, ever.

## Touchpoints

- New `scripts/task_run/task_run_dag.py`: DAG schema, ready-derivation, single-shot pull.
- New `tests/charness_cli/test_task_run_dag.py`: 2-lane fixture with mocked provider child state, ready-pull cases.

## Acceptance

- One file holds lanes, dependencies, carrier, and brief path as the queue's source of truth (#843-8).
- When a dependency lands, ready dependents launch; a freed slot pulls the next ready lane via one explicit command (#843-8, #843-9).
- Provider child state owns open/blocked/closed truth; the DAG never asserts completion (#843-8).

## Out of scope

No watch loop, background poll, or daemon; no merge-train core (WI-8a); no progress cursor ownership (the provider parent owns the cursor).

<!-- charness-work-item-key: wi-8b-dag -->
